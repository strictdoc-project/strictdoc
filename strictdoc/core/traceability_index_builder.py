import glob
import os
import sys
from typing import List, Iterator, Optional

from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.models.inline_link import InlineLink
from strictdoc.backend.sdoc.models.reference import ParentReqReference
from strictdoc.backend.sdoc.models.type_system import ReferenceType
from strictdoc.backend.sdoc.models.requirement import Requirement
from strictdoc.backend.source_file_syntax.reader import (
    SourceFileTraceabilityReader,
)
from strictdoc.cli.cli_arg_parser import ExportCommandConfig
from strictdoc.core.document_finder import DocumentFinder
from strictdoc.core.document_iterator import DocumentCachingIterator
from strictdoc.core.document_meta import DocumentMeta
from strictdoc.core.document_tree import DocumentTree
from strictdoc.core.error_message import ErrorMessage
from strictdoc.core.finders.source_files_finder import (
    SourceFilesFinder,
    SourceFile,
)
from strictdoc.core.source_tree import SourceTree
from strictdoc.core.traceability_index import (
    TraceabilityIndex,
    FileTraceabilityIndex,
)
from strictdoc.core.tree_cycle_detector import TreeCycleDetector
from strictdoc.helpers.file_modification_time import get_file_modification_time
from strictdoc.helpers.timing import timing_decorator


class TraceabilityIndexBuilder:
    @staticmethod
    @timing_decorator("Collect traceability information")
    def create(
        *, config: ExportCommandConfig, parallelizer
    ) -> TraceabilityIndex:
        # TODO: It would be great to hide this code behind --development flag.
        # There is no need for this to be activated in the Pip-released builds.
        strict_own_files_unfiltered: Iterator[str] = glob.iglob(
            f"{config.strictdoc_root_path}/strictdoc/**/*",
            recursive=True,
        )
        strict_own_files: List[str] = [
            f
            for f in strict_own_files_unfiltered
            if f.endswith(".html") or f.endswith(".py")
        ]
        latest_strictdoc_own_file = (
            max(strict_own_files, key=os.path.getctime)
            if len(strict_own_files) > 0
            else 0
        )

        strictdoc_last_update = get_file_modification_time(
            latest_strictdoc_own_file
        )

        document_tree, asset_dirs = DocumentFinder.find_sdoc_content(
            config, parallelizer
        )

        # TODO: This is rather messy but it is better than it used to be.
        # Currently, the traceability index holds everything that is later used
        # by HTML generators:
        # - traceability index itself
        # - document tree
        # - assets
        # - runtime configuration
        traceability_index = TraceabilityIndexBuilder.create_from_document_tree(
            document_tree
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
                config.strictdoc_root_path,
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
        if config.experimental_enable_file_traceability:
            source_tree: SourceTree = SourceFilesFinder.find_source_files(
                config
            )
            source_files = source_tree.source_files
            source_file: SourceFile
            for source_file in source_files:
                is_source_file_referenced = (
                    traceability_index.has_source_file_reqs(
                        source_file.in_doctree_source_file_rel_path
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
                        source_file.in_doctree_source_file_rel_path,
                        traceability_info,
                    )
            traceability_index.document_tree.attach_source_tree(source_tree)

        return traceability_index

    @staticmethod
    @timing_decorator("Collect traceability information")
    def create_from_document_tree(document_tree: DocumentTree):
        # TODO: Too many things going on below. Would be great to simplify this
        # workflow.
        d_01_document_iterators = {}
        d_02_requirements_map = {}
        d_03_map_doc_titles_to_tag_lists = {}
        d_05_map_documents_to_parents = {}
        d_06_map_documents_to_children = {}
        d_07_file_traceability_index = FileTraceabilityIndex()
        d_08_requirements_children_map = {}
        d_11_map_id_to_node = {}

        # It seems to be impossible to accomplish everything in just one for
        # loop. One particular problem that requires two passes: it is not
        # possible to know after one iteration if any of the requirements
        # reference parents that do not exist.
        #
        # Step #1:
        # - Collect a dictionary of all requirements in the document tree:
        # {req_id: req}
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
            d_11_map_id_to_node[document.node_id] = document

            document_iterator = DocumentCachingIterator(document)
            d_01_document_iterators[document] = document_iterator
            if document.title not in d_03_map_doc_titles_to_tag_lists:
                d_03_map_doc_titles_to_tag_lists[document.title] = {}
            for node in document_iterator.all_content():
                d_11_map_id_to_node[node.node_id] = node

                if not node.uid:
                    continue
                if node.uid in d_02_requirements_map:
                    other_req_doc = d_02_requirements_map[node.uid]["document"]
                    if other_req_doc == document:
                        print(
                            "error: DocumentIndex: "
                            "two nodes with the same UID "
                            "exist in the same document: "
                            f'{node.uid} in "{document.title}".'
                        )
                    else:
                        print(
                            "error: DocumentIndex: "
                            "two nodes with the same UID "
                            "exist in two different documents: "
                            f'{node.uid} in "{document.title}" and '
                            f'"{other_req_doc.title}".'
                        )
                    sys.exit(1)
                d_02_requirements_map[node.uid] = {
                    "document": document,
                    "requirement": node,
                    "parents": [],
                    "parents_uids": [],
                    "children": [],
                }
                if not node.is_requirement:
                    continue
                requirement: Requirement = node
                document_tags = d_03_map_doc_titles_to_tag_lists[document.title]
                if requirement.tags is not None:
                    for tag in requirement.tags:
                        if tag not in document_tags:
                            document_tags[tag] = 0
                        document_tags[tag] += 1
                if requirement.uid not in d_08_requirements_children_map:
                    d_08_requirements_children_map[requirement.uid] = []
                for ref in requirement.references:
                    if ref.ref_type == ReferenceType.FILE:
                        d_07_file_traceability_index.register(requirement)
                        continue
                    if ref.ref_type != ReferenceType.PARENT:
                        continue
                    ref: ParentReqReference
                    d_02_requirements_map[requirement.uid][
                        "parents_uids"
                    ].append(ref.ref_uid)
                    if ref.ref_uid not in d_08_requirements_children_map:
                        d_08_requirements_children_map[ref.ref_uid] = []
                    d_08_requirements_children_map[ref.ref_uid].append(
                        requirement
                    )

        # Now iterate over the requirements again to build an in-depth map of
        # parents and children.
        parents_cycle_detector = TreeCycleDetector(d_02_requirements_map)
        children_cycle_detector = TreeCycleDetector(d_02_requirements_map)

        for document in document_tree.document_list:
            d_05_map_documents_to_parents.setdefault(document, set())
            d_06_map_documents_to_children.setdefault(document, set())
            document_iterator = d_01_document_iterators[document]

            for node in document_iterator.all_content():
                if node.is_section:
                    for free_text in node.free_texts:
                        for part in free_text.parts:
                            if isinstance(part, InlineLink):
                                if part.link not in d_02_requirements_map:
                                    print(
                                        ErrorMessage.inline_link_uid_not_exist(
                                            part.link
                                        )
                                    )
                                    sys.exit(1)
                if not node.is_requirement:
                    continue
                requirement: Requirement = node
                if not requirement.uid:
                    continue

                # Now it is possible to resolve parents first checking if they
                # indeed exist.
                requirement_parent_ids = d_02_requirements_map[requirement.uid][
                    "parents_uids"
                ]
                for requirement_parent_id in requirement_parent_ids:
                    if requirement_parent_id not in d_02_requirements_map:
                        # TODO: Strict variant of the behavior will be to stop
                        # and raise an error message.
                        print(
                            f"warning: [DocumentIndex.create] "
                            f"Requirement {requirement.uid} references "
                            f"parent requirement which doesn't exist: "
                            f"{requirement_parent_id}"
                        )
                        d_08_requirements_children_map.pop(
                            requirement_parent_id, None
                        )
                        continue
                    parent_requirement = d_02_requirements_map[
                        requirement_parent_id
                    ]["requirement"]
                    d_02_requirements_map[requirement.uid]["parents"].append(
                        parent_requirement
                    )
                    # Set document dependencies.
                    parent_document = d_02_requirements_map[
                        requirement_parent_id
                    ]["document"]
                    d_05_map_documents_to_parents.setdefault(
                        requirement.document, set()
                    )
                    d_05_map_documents_to_parents[requirement.document].add(
                        parent_document
                    )
                    d_06_map_documents_to_children.setdefault(
                        parent_document, set()
                    )
                    d_06_map_documents_to_children[parent_document].add(
                        requirement.document
                    )

                # [SDOC-VALIDATION-NO-CYCLES]
                # Detect cycles
                parents_cycle_detector.check_node(
                    requirement.uid,
                    lambda requirement_id: d_02_requirements_map[
                        requirement_id
                    ]["parents_uids"],
                )
                children_cycle_detector.check_node(
                    requirement.uid,
                    lambda requirement_id: list(
                        map(
                            lambda current_requirement: current_requirement.uid,
                            d_08_requirements_children_map[requirement_id],
                        )
                    ),
                )
                # [/SDOC-VALIDATION-NO-CYCLES]

                d_02_requirements_map[requirement.uid][
                    "children"
                ] = d_08_requirements_children_map[requirement.uid]

        traceability_index = TraceabilityIndex(
            d_01_document_iterators,
            d_02_requirements_map,
            d_03_map_doc_titles_to_tag_lists,
            d_05_map_documents_to_parents,
            d_06_map_documents_to_children,
            file_traceability_index=d_07_file_traceability_index,
            map_id_to_node=d_11_map_id_to_node,
        )
        return traceability_index
