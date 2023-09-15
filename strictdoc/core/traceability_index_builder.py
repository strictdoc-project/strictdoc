import glob
import os
import sys
from collections import defaultdict
from typing import Dict, Iterator, List, Optional, Set, Tuple

from strictdoc.backend.sdoc.models.anchor import Anchor
from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.models.inline_link import InlineLink
from strictdoc.backend.sdoc.models.reference import (
    ChildReqReference,
    ParentReqReference,
)
from strictdoc.backend.sdoc.models.requirement import Requirement
from strictdoc.backend.sdoc.models.type_system import ReferenceType
from strictdoc.backend.sdoc_source_code.reader import (
    SourceFileTraceabilityReader,
)
from strictdoc.core.document_finder import DocumentFinder
from strictdoc.core.document_iterator import DocumentCachingIterator
from strictdoc.core.document_meta import DocumentMeta
from strictdoc.core.document_tree import DocumentTree
from strictdoc.core.finders.source_files_finder import (
    SourceFile,
    SourceFilesFinder,
)
from strictdoc.core.graph.validations import RemoveNodeValidation
from strictdoc.core.graph_database import GraphDatabase
from strictdoc.core.project_config import ProjectConfig, ProjectFeature
from strictdoc.core.source_tree import SourceTree
from strictdoc.core.traceability_index import (
    FileTraceabilityIndex,
    RequirementConnections,
    TraceabilityIndex,
)
from strictdoc.core.tree_cycle_detector import TreeCycleDetector
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.exception import StrictDocException
from strictdoc.helpers.file_modification_time import get_file_modification_time
from strictdoc.helpers.timing import timing_decorator


class TraceabilityIndexBuilder:
    @staticmethod
    def create(
        *,
        project_config: ProjectConfig,
        parallelizer,
    ) -> TraceabilityIndex:
        # TODO: It would be great to hide this code behind --development flag.
        # There is no need for this to be activated in the Pip-released builds.
        strict_own_files_unfiltered: Iterator[str] = glob.iglob(
            f"{project_config.get_strictdoc_root_path()}/strictdoc/**/*",
            recursive=True,
        )
        strict_own_files: List[str] = [
            f
            for f in strict_own_files_unfiltered
            if f.endswith(".html") or f.endswith(".py") or f.endswith(".jinja")
        ]
        latest_strictdoc_own_file = (
            max(strict_own_files, key=os.path.getctime)
            if len(strict_own_files) > 0
            else 0
        )

        strictdoc_last_update = get_file_modification_time(
            latest_strictdoc_own_file
        )
        if (
            project_config.config_last_update is not None
            and project_config.config_last_update > strictdoc_last_update
        ):
            strictdoc_last_update = project_config.config_last_update

        document_tree, asset_dirs = DocumentFinder.find_sdoc_content(
            project_config=project_config, parallelizer=parallelizer
        )

        # TODO: This is rather messy, but it is better than it used to be.
        # Currently, the traceability index holds everything that is later used
        # by HTML generators:
        # - traceability index itself
        # - document tree
        # - assets
        # - runtime configuration
        traceability_index: TraceabilityIndex = (
            TraceabilityIndexBuilder.create_from_document_tree(document_tree)
        )
        traceability_index.document_tree = document_tree
        traceability_index.asset_dirs = asset_dirs
        traceability_index.strictdoc_last_update = strictdoc_last_update

        # Incremental re-generation of documents
        document: Document
        for document in traceability_index.document_tree.document_list:
            # If a document file exists we want to check its modification path
            # in order to skip its generation in case it has not changed since
            # the last generation. We also check the Traceability Index for the
            # document's dependencies to see if they must be regenerated as
            # well.
            document_meta_or_none: Optional[DocumentMeta] = document.meta
            assert document_meta_or_none is not None
            document_meta: DocumentMeta = document_meta_or_none
            full_output_path = os.path.join(
                project_config.get_strictdoc_root_path(),
                document_meta.get_html_doc_path(),
            )
            if not os.path.isfile(full_output_path):
                document.ng_needs_generation = True
            else:
                output_file_mtime = get_file_modification_time(full_output_path)
                sdoc_mtime = get_file_modification_time(
                    document_meta.input_doc_full_path
                )
                if not (
                    sdoc_mtime < output_file_mtime
                    and strictdoc_last_update < output_file_mtime
                ):
                    document.ng_needs_generation = True
            if document.ng_needs_generation:
                todo_list = [document]
                finished = set()
                while todo_list:
                    document = todo_list.pop()
                    if document in finished:
                        continue
                    document.ng_needs_generation = True
                    document_parents = traceability_index.get_document_parents(
                        document
                    )
                    document_children = (
                        traceability_index.get_document_children(document)
                    )
                    todo_list.extend(document_parents)
                    todo_list.extend(document_children)
                    finished.add(document)

        # File traceability
        if project_config.is_feature_activated(
            ProjectFeature.REQUIREMENT_TO_SOURCE_TRACEABILITY
        ):
            source_tree: SourceTree = SourceFilesFinder.find_source_files(
                project_config=project_config
            )
            source_files = source_tree.source_files
            source_file: SourceFile
            for source_file in source_files:
                is_source_file_referenced = (
                    traceability_index.has_source_file_reqs(
                        source_file.in_doctree_source_file_rel_path_posix
                    )
                )
                if not is_source_file_referenced:
                    continue
                source_file.is_referenced = True
                traceability_reader = SourceFileTraceabilityReader()
                traceability_info = traceability_reader.read_from_file(
                    source_file.full_path
                )
                if traceability_info:
                    traceability_index.attach_traceability_info(
                        source_file.in_doctree_source_file_rel_path_posix,
                        traceability_info,
                    )
            traceability_index.get_file_traceability_index().validate()
            traceability_index.document_tree.attach_source_tree(source_tree)

        return traceability_index

    @staticmethod
    @timing_decorator("Build traceability graph")
    def create_from_document_tree(
        document_tree: DocumentTree,
    ) -> TraceabilityIndex:
        # TODO: Too many things going on below. Would be great to simplify this
        # workflow.
        d_01_document_iterators: Dict[Document, DocumentCachingIterator] = {}
        d_03_map_doc_titles_to_tag_lists = {}
        d_05_map_documents_to_parents: Dict[
            Document, Set[Document]
        ] = defaultdict(set)
        d_06_map_documents_to_children: Dict[
            Document, Set[Document]
        ] = defaultdict(set)
        d_07_file_traceability_index = FileTraceabilityIndex()
        d_08_requirements_children_map: Dict[
            str, List[Requirement]
        ] = defaultdict(list)
        d_09_reverse_parents: List[Tuple[Requirement, str]] = []
        d_11_map_id_to_node = {}

        graph_database = GraphDatabase()
        graph_database.remove_node_validation = RemoveNodeValidation()

        traceability_index = TraceabilityIndex(
            d_01_document_iterators,
            {},
            d_03_map_doc_titles_to_tag_lists,
            d_05_map_documents_to_parents,
            d_06_map_documents_to_children,
            file_traceability_index=d_07_file_traceability_index,
            map_id_to_node=d_11_map_id_to_node,
            graph_database=graph_database,
        )

        # It seems to be impossible to accomplish everything in just one for
        # loop. One particular problem that requires two passes: it is not
        # possible to know after one iteration which of the requirements
        # parents do not exist for each given requirement.
        #
        # Step #1:
        # - Collect a dictionary of all requirements in the document tree:
        # {req_id: req}  # noqa: ERA001
        # - Each requirement's 'parents_uids' is populated with the forward
        # declarations of its parents uids.
        # - A separate map is created: {req_id: [req_children]}
        # At this point some information is in place, but it was not known if
        # some UIDs could not be resolved which is the task of the second
        # step.
        #
        # Step #2:
        # - Check if each requirement's has valid parent links.
        # - Resolve parent forward declarations
        # - Re-assign children declarations
        # - Detect cycles
        # - Calculate depth of both parent and child links.

        document: Document
        for document in document_tree.document_list:
            for free_text in document.free_texts:
                for part in free_text.parts:
                    if isinstance(part, Anchor):
                        assert part.value not in d_11_map_id_to_node
                        graph_database.add_node_by_mid(
                            mid=part.mid,
                            uid=part.value,
                            node=part,
                        )

            d_11_map_id_to_node[document.mid] = document

            document_iterator = DocumentCachingIterator(document)
            d_01_document_iterators[document] = document_iterator
            if document.title not in d_03_map_doc_titles_to_tag_lists:
                d_03_map_doc_titles_to_tag_lists[document.title] = {}
            for node in document_iterator.all_content():
                d_11_map_id_to_node[node.mid] = node

                if node.is_section:
                    for free_text in node.free_texts:
                        for part in free_text.parts:
                            if isinstance(part, InlineLink):
                                graph_database.add_node_by_mid(
                                    mid=part.mid,
                                    uid=None,
                                    node=part,
                                )
                            elif isinstance(part, Anchor):
                                assert part.value not in d_11_map_id_to_node
                                graph_database.add_node_by_mid(
                                    mid=part.mid,
                                    uid=part.value,
                                    node=part,
                                )

                if not node.reserved_uid:
                    continue
                if node.reserved_uid in traceability_index.requirements_parents:
                    other_req_doc = traceability_index.requirements_parents[
                        node.reserved_uid
                    ].document
                    if other_req_doc == document:
                        print(  # noqa: T201
                            "error: DocumentIndex: "
                            "two nodes with the same UID "
                            "exist in the same document: "
                            f'{node.reserved_uid} in "{document.title}".'
                        )
                    else:
                        print(  # noqa: T201
                            "error: DocumentIndex: "
                            "two nodes with the same UID "
                            "exist in two different documents: "
                            f'{node.reserved_uid} in "{other_req_doc.title}" '
                            f'and "{document.title}".'
                        )
                    sys.exit(1)
                traceability_index.requirements_parents[
                    node.reserved_uid
                ] = RequirementConnections(
                    requirement=node,
                    document=document,
                    parents=[],
                    parents_uids=[],
                    children=[],
                )
                if not node.is_requirement:
                    continue
                requirement: Requirement = node
                document_tags = d_03_map_doc_titles_to_tag_lists[document.title]
                if requirement.reserved_tags is not None:
                    for tag in requirement.reserved_tags:
                        if tag not in document_tags:
                            document_tags[tag] = 0
                        document_tags[tag] += 1
                for reference in requirement.references:
                    if reference.ref_type == ReferenceType.FILE:
                        d_07_file_traceability_index.register(requirement)
                        continue

                    if reference.ref_type == ReferenceType.PARENT:
                        parent_reference: ParentReqReference = assert_cast(
                            reference, ParentReqReference
                        )
                        assert requirement.reserved_uid is not None  # mypy
                        traceability_index.requirements_parents[
                            requirement.reserved_uid
                        ].parents_uids.append(parent_reference.ref_uid)
                        d_08_requirements_children_map[
                            parent_reference.ref_uid
                        ].append(requirement)
                        continue

                    if reference.ref_type == ReferenceType.CHILD:
                        child_reference: ChildReqReference = assert_cast(
                            reference, ChildReqReference
                        )
                        assert requirement.reserved_uid is not None  # mypy
                        d_09_reverse_parents.append(
                            (node, child_reference.ref_uid)
                        )
                        continue

        for requirement_, child_requirement_uid_ in d_09_reverse_parents:
            if (
                child_requirement_uid_
                not in traceability_index.requirements_parents
            ):
                raise StrictDocException(
                    f"[DocumentIndex.create] "
                    f"Requirement {requirement_.reserved_uid} "
                    f"references a "
                    f"child requirement that doesn't exist: "
                    f"{child_requirement_uid_}."
                )

            child_requirement: Requirement = (
                traceability_index.requirements_parents[
                    child_requirement_uid_
                ].requirement
            )
            requirement_uid: str = assert_cast(requirement_.reserved_uid, str)
            traceability_index.requirements_parents[
                child_requirement_uid_
            ].parents_uids.append(requirement_uid)
            d_08_requirements_children_map[requirement_uid].append(
                child_requirement
            )

        # Now iterate over the requirements again to build an in-depth map of
        # parents and children.
        parents_cycle_detector = TreeCycleDetector(
            traceability_index.requirements_parents
        )
        children_cycle_detector = TreeCycleDetector(
            traceability_index.requirements_parents
        )

        for document in document_tree.document_list:
            if len(document.free_texts) > 0:
                for part in document.free_texts[0].parts:
                    if isinstance(part, InlineLink):
                        if (
                            part.link
                            not in traceability_index.requirements_parents
                            and not graph_database.node_with_uid_exists(
                                uid=part.link,
                            )
                        ):
                            raise StrictDocException(
                                "DocumentIndex: "
                                "the inline link references an "
                                "object with an UID "
                                "that does not exist: "
                                f"{part.link}."
                            )
                        traceability_index.create_inline_link(part)

            document_iterator = d_01_document_iterators[document]

            for node in document_iterator.all_content():
                if node.is_section:
                    for free_text in node.free_texts:
                        for part in free_text.parts:
                            if isinstance(part, InlineLink):
                                if (
                                    part.link
                                    not in traceability_index.requirements_parents
                                    and not graph_database.node_with_uid_exists(
                                        uid=part.link,
                                    )
                                ):
                                    raise StrictDocException(
                                        "DocumentIndex: "
                                        "the inline link references an "
                                        "object with an UID "
                                        "that does not exist: "
                                        f"{part.link}."
                                    )
                                traceability_index.create_inline_link(part)

                if not node.is_requirement:
                    continue
                requirement: Requirement = node
                if not requirement.reserved_uid:
                    continue

                # Now it is possible to resolve parents first checking if they
                # indeed exist.
                requirement_parent_ids = (
                    traceability_index.requirements_parents[
                        requirement.reserved_uid
                    ].parents_uids
                )
                for requirement_parent_id in requirement_parent_ids:
                    if (
                        requirement_parent_id
                        not in traceability_index.requirements_parents
                    ):
                        raise StrictDocException(
                            f"[DocumentIndex.create] "
                            f"Requirement {requirement.reserved_uid} "
                            f"references "
                            f"parent requirement which doesn't exist: "
                            f"{requirement_parent_id}."
                        )
                    parent_requirement = (
                        traceability_index.requirements_parents[
                            requirement_parent_id
                        ].requirement
                    )
                    traceability_index.requirements_parents[
                        requirement.reserved_uid
                    ].parents.append(parent_requirement)
                    # Set document dependencies.
                    parent_document = traceability_index.requirements_parents[
                        requirement_parent_id
                    ].document
                    d_05_map_documents_to_parents[requirement.document].add(
                        parent_document
                    )
                    d_06_map_documents_to_children[parent_document].add(
                        requirement.document
                    )

                # @sdoc[SDOC-VALIDATION-NO-CYCLES]  # noqa: ERA001
                # Detect cycles
                parents_cycle_detector.check_node(
                    requirement.reserved_uid,
                    lambda requirement_id: traceability_index.requirements_parents[
                        requirement_id
                    ].parents_uids,
                )
                children_cycle_detector.check_node(
                    requirement.reserved_uid,
                    lambda requirement_id: list(
                        map(
                            lambda current_requirement: current_requirement.reserved_uid,  # noqa: E501
                            d_08_requirements_children_map[requirement_id],
                        )
                    ),
                )
                # @sdoc[/SDOC-VALIDATION-NO-CYCLES]

                traceability_index.requirements_parents[
                    requirement.reserved_uid
                ].children = d_08_requirements_children_map[
                    requirement.reserved_uid
                ]

        return traceability_index
