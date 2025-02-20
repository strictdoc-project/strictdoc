# mypy: disable-error-code="arg-type,attr-defined,no-redef,no-untyped-call,no-untyped-def,union-attr"
import datetime
import glob
import os
import sys
from typing import Dict, Iterator, List, Optional, Set, Tuple, Union

from textx import TextXSyntaxError

from strictdoc.backend.sdoc.error_handling import StrictDocSemanticError
from strictdoc.backend.sdoc.models.anchor import Anchor
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_from_file import DocumentFromFile
from strictdoc.backend.sdoc.models.document_grammar import DocumentGrammar
from strictdoc.backend.sdoc.models.inline_link import InlineLink
from strictdoc.backend.sdoc.models.node import SDocCompositeNode, SDocNode
from strictdoc.backend.sdoc.models.reference import (
    ChildReqReference,
    ParentReqReference,
)
from strictdoc.backend.sdoc.models.section import SDocSection
from strictdoc.backend.sdoc.models.type_system import ReferenceType
from strictdoc.backend.sdoc.validations.sdoc_validator import SDocValidator
from strictdoc.backend.sdoc_source_code.caching_reader import (
    SourceFileTraceabilityCachingReader,
)
from strictdoc.core.document_finder import DocumentFinder
from strictdoc.core.document_iterator import DocumentCachingIterator
from strictdoc.core.document_tree import DocumentTree
from strictdoc.core.file_dependency_manager import FileDependencyManager
from strictdoc.core.finders.source_files_finder import (
    SourceFile,
    SourceFilesFinder,
)
from strictdoc.core.graph.many_to_many_set import ManyToManySet
from strictdoc.core.graph.one_to_one_dictionary import OneToOneDictionary
from strictdoc.core.graph.validations import RemoveNodeValidation
from strictdoc.core.graph_database import GraphDatabase
from strictdoc.core.project_config import ProjectConfig, ProjectFeature
from strictdoc.core.query_engine.query_object import (
    QueryNullObject,
    QueryObject,
)
from strictdoc.core.query_engine.query_reader import QueryReader
from strictdoc.core.source_tree import SourceTree
from strictdoc.core.traceability_index import (
    FileTraceabilityIndex,
    GraphLinkType,
    TraceabilityIndex,
)
from strictdoc.core.tree_cycle_detector import TreeCycleDetector
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.exception import StrictDocException
from strictdoc.helpers.file_modification_time import (
    get_file_modification_time,
)
from strictdoc.helpers.mid import MID
from strictdoc.helpers.timing import measure_performance, timing_decorator


class TraceabilityIndexBuilder:
    @staticmethod
    def create(
        *,
        project_config: ProjectConfig,
        parallelizer,
        skip_source_files: bool = False,
        auto_uid_mode: bool = False,
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

        strictdoc_last_update: datetime.datetime = get_file_modification_time(
            latest_strictdoc_own_file
        )
        if (
            project_config.config_last_update is not None
            and project_config.config_last_update > strictdoc_last_update
        ):
            strictdoc_last_update = project_config.config_last_update

        document_tree, asset_manager = DocumentFinder.find_sdoc_content(
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
            TraceabilityIndexBuilder.create_from_document_tree(
                document_tree,
                project_config,
                auto_uid_mode,
            )
        )
        traceability_index.document_tree = document_tree
        traceability_index.asset_manager = asset_manager
        traceability_index.strictdoc_last_update = strictdoc_last_update

        TraceabilityIndexBuilder._filter_nodes(
            project_config=project_config, traceability_index=traceability_index
        )

        # File traceability
        if not skip_source_files and project_config.is_feature_activated(
            ProjectFeature.REQUIREMENT_TO_SOURCE_TRACEABILITY
        ):
            file_tracability_index = (
                traceability_index.get_file_traceability_index()
            )
            source_tree: SourceTree = SourceFilesFinder.find_source_files(
                project_config=project_config
            )
            source_files = source_tree.source_files
            source_file: SourceFile
            for source_file in source_files:
                with measure_performance(
                    f"Reading source: {source_file.in_doctree_source_file_rel_path}"
                ):
                    traceability_info = (
                        SourceFileTraceabilityCachingReader.read_from_file(
                            source_file.full_path, project_config
                        )
                    )

                if traceability_info:
                    traceability_index.create_traceability_info(
                        source_file,
                        traceability_info,
                    )
                    # Is file referenced by backwards links?
                    if len(traceability_info.markers) > 0:
                        source_file.is_referenced = True

            file_tracability_index.validate_and_resolve(traceability_index)

            # Iterate again to resolve if the file is referenced.
            # FIXME: Not great to iterate two times.
            for source_file in file_tracability_index.indexed_source_files():
                # Is file referenced by forward links?
                is_source_file_referenced = (
                    traceability_index.has_source_file_reqs(
                        source_file.in_doctree_source_file_rel_path_posix
                    )
                )
                if is_source_file_referenced:
                    source_file.is_referenced = True

                    source_file_reqs: Tuple[List[SDocNode], List[SDocNode]] = (
                        traceability_index.get_source_file_reqs(
                            source_file.in_doctree_source_file_rel_path_posix
                        )
                    )
                    for node_ in source_file_reqs[0] + source_file_reqs[1]:
                        node_document = node_.document
                        traceability_index.file_dependency_manager.add_dependency(
                            source_file.full_path,
                            source_file.output_file_full_path,
                            node_document.meta.input_doc_full_path,
                        )
                        traceability_index.file_dependency_manager.add_dependency(
                            node_document.meta.input_doc_full_path,
                            node_document.meta.output_document_full_path,
                            source_file.full_path,
                        )

            traceability_index.document_tree.attach_source_tree(source_tree)

        """
        Resolve all modification dates to support the incremental generation of
        all artifacts.
        """

        file_dependency_manager = traceability_index.file_dependency_manager

        file_dependency_manager.resolve_modification_dates(
            traceability_index.strictdoc_last_update
        )

        return traceability_index

    @staticmethod
    @timing_decorator("Build traceability graph")
    def create_from_document_tree(
        document_tree: DocumentTree,
        project_config: ProjectConfig,
        auto_uid_mode: bool = True,
    ) -> TraceabilityIndex:
        # FIXME: Too many things going on below. Would be great to simplify this
        # workflow.
        d_01_document_iterators: Dict[
            SDocDocument, DocumentCachingIterator
        ] = {}
        d_07_file_traceability_index = FileTraceabilityIndex()

        graph_database = GraphDatabase(
            [
                (
                    GraphLinkType.MID_TO_NODE,
                    OneToOneDictionary(
                        MID,
                        (
                            SDocNode,
                            SDocSection,
                            SDocDocument,
                            InlineLink,
                            Anchor,
                        ),
                    ),
                ),
                (
                    GraphLinkType.UID_TO_NODE,
                    OneToOneDictionary(
                        str, (SDocDocument, SDocNode, SDocSection, Anchor)
                    ),
                ),
                (
                    GraphLinkType.NODE_TO_PARENT_NODES,
                    ManyToManySet(SDocNode, SDocNode),
                ),
                (
                    GraphLinkType.NODE_TO_CHILD_NODES,
                    ManyToManySet(SDocNode, SDocNode),
                ),
                (
                    GraphLinkType.NODE_TO_INCOMING_LINKS,
                    ManyToManySet(MID, InlineLink),
                ),
                (
                    GraphLinkType.DOCUMENT_TO_TAGS,
                    OneToOneDictionary(MID, dict),
                ),
            ]
        )
        graph_database.remove_node_validation = RemoveNodeValidation()

        file_dependency_manager: FileDependencyManager = (
            FileDependencyManager.create_from_cache(
                project_config=project_config
            )
        )

        traceability_index = TraceabilityIndex(
            d_01_document_iterators,
            file_traceability_index=d_07_file_traceability_index,
            graph_database=graph_database,
            file_dependency_manager=file_dependency_manager,
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
        # - Check if each requirement's has valid parent relations.
        # - Resolve parent forward declarations
        # - Re-assign children declarations
        # - Detect cycles
        # - Calculate depth of both parent and child relations.
        for (
            path_to_grammar_,
            grammar_from_file_,
        ) in document_tree.map_grammars_by_filenames.items():
            try:
                SDocValidator.validate_grammar_from_file(
                    path_to_grammar_, grammar_from_file_
                )
            except StrictDocSemanticError as exc:
                print(exc.to_print_message())  # noqa: T201
                sys.exit(1)

        document: SDocDocument
        for document in document_tree.document_list:
            """
            First, resolve all grammars that are imported from grammar files.
            """
            if document.grammar.import_from_file is not None:
                document_grammar: Optional[DocumentGrammar] = (
                    document_tree.get_grammar_by_filename(
                        document.grammar.import_from_file
                    )
                )
                if document_grammar is None:
                    raise StrictDocException(
                        "TraceabilityIndex: "
                        f'the document "{document.reserved_title}" '
                        "imports a grammar from a file that does not exist: "
                        f'"{document.grammar.import_from_file}".'
                    )
                document.grammar.update_with_elements(document_grammar.elements)

            # This is important because due to the difference between the
            # normal grammar vs imported grammar, the parent may not be set at
            # this point.
            document.grammar.parent = document

            try:
                SDocValidator.validate_document(document)
            except StrictDocSemanticError as exc:
                print(exc.to_print_message())  # noqa: T201
                sys.exit(1)

            if graph_database.has_link(
                link_type=GraphLinkType.MID_TO_NODE,
                lhs_node=document.reserved_mid,
            ):
                other_document: SDocDocument = graph_database.get_link_value(
                    link_type=GraphLinkType.MID_TO_NODE,
                    lhs_node=document.reserved_mid,
                )
                raise StrictDocException(
                    "TraceabilityIndex: "
                    "the document MID is not unique: "
                    f"{document.reserved_mid}. "
                    "All machine identifiers (MID) must be unique values. "
                    f"Affected documents:\n"
                    f"{other_document.get_debug_info()}\n"
                    f"and\n"
                    f"{document.get_debug_info()}."
                )

            graph_database.create_link(
                link_type=GraphLinkType.MID_TO_NODE,
                lhs_node=document.reserved_mid,
                rhs_node=document,
            )
            if document.uid:
                graph_database.create_link(
                    link_type=GraphLinkType.UID_TO_NODE,
                    lhs_node=document.uid,
                    rhs_node=document,
                )

            document_tags: Dict[str, int] = {}
            graph_database.create_link(
                link_type=GraphLinkType.DOCUMENT_TO_TAGS,
                lhs_node=document.reserved_mid,
                rhs_node=document_tags,
            )

            document_iterator = DocumentCachingIterator(document)
            d_01_document_iterators[document] = document_iterator

            for node in document_iterator.all_content(
                print_fragments=False,
                print_fragments_from_files=False,
            ):
                if isinstance(node, SDocNode):
                    try:
                        SDocValidator.validate_node(
                            node,
                            document_grammar=document.grammar,
                            path_to_sdoc_file=document.meta.input_doc_full_path,
                            auto_uid_mode=auto_uid_mode,
                        )
                    except StrictDocSemanticError as exc:
                        print(exc.to_print_message())  # noqa: T201
                        sys.exit(1)

                if graph_database.has_link(
                    link_type=GraphLinkType.MID_TO_NODE,
                    lhs_node=node.reserved_mid,
                ):
                    other_node: SDocDocument = graph_database.get_link_value(
                        link_type=GraphLinkType.MID_TO_NODE,
                        lhs_node=node.reserved_mid,
                    )
                    raise StrictDocException(
                        "TraceabilityIndex: "
                        "the node MID is not unique: "
                        f"{node.reserved_mid}. "
                        "All machine identifiers (MID) must be unique values. "
                        f"Affected nodes:\n"
                        f"{other_node.get_debug_info()}\n"
                        f"and\n"
                        f"{node.get_debug_info()}."
                    )
                graph_database.create_link(
                    link_type=GraphLinkType.MID_TO_NODE,
                    lhs_node=node.reserved_mid,
                    rhs_node=node,
                )

                if node.reserved_uid is not None:
                    # @relation(SDOC-SRS-29, scope=range_start)
                    if traceability_index.graph_database.has_link(
                        link_type=GraphLinkType.UID_TO_NODE,
                        lhs_node=node.reserved_uid,
                    ):
                        already_existing_node = (
                            traceability_index.graph_database.get_link_value(
                                link_type=GraphLinkType.UID_TO_NODE,
                                lhs_node=node.reserved_uid,
                            )
                        )
                        other_req_doc = already_existing_node.document
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
                    # @relation(SDOC-SRS-29, scope=range_end)

                    traceability_index.graph_database.create_link(
                        link_type=GraphLinkType.UID_TO_NODE,
                        lhs_node=node.reserved_uid,
                        rhs_node=node,
                    )

                if node.is_requirement:
                    requirement: SDocNode = assert_cast(node, SDocNode)
                    if requirement.reserved_tags is not None:
                        for tag in requirement.reserved_tags:
                            document_tags.setdefault(tag, 0)
                            document_tags[tag] += 1
                    for node_field_ in node.enumerate_fields():
                        for part in node_field_.parts:
                            # The inline links are handled at the next big
                            # For loop pass because the information about
                            # all Nodes and Anchors have not been
                            # collected yet at this point.
                            # see create_inline_link below.
                            if isinstance(part, Anchor):
                                graph_database.create_link(
                                    link_type=GraphLinkType.MID_TO_NODE,
                                    lhs_node=part.mid,
                                    rhs_node=part,
                                )
                                graph_database.create_link(
                                    link_type=GraphLinkType.UID_TO_NODE,
                                    lhs_node=part.value,
                                    rhs_node=part,
                                )

        # Now iterate over the requirements again to build an in-depth map of
        # parents and children.
        for document in document_tree.document_list:
            document_iterator = d_01_document_iterators[document]

            for node in document_iterator.all_content(
                print_fragments=False,
                print_fragments_from_files=False,
            ):
                if not node.is_requirement:
                    continue

                requirement: SDocNode = node

                """
                At this point, we resolve LINKs, and the expectation is that
                all UIDs or ANCHORS (they also have UIDs) are registered at the
                previous pass.
                """
                for node_field_ in node.enumerate_fields():
                    for part in node_field_.parts:
                        if isinstance(part, InlineLink):
                            if not graph_database.has_link(
                                link_type=GraphLinkType.UID_TO_NODE,
                                lhs_node=part.link,
                            ):
                                raise StrictDocException(
                                    "DocumentIndex: "
                                    "the inline link references an "
                                    "object with an UID "
                                    "that does not exist: "
                                    f"{part.link}."
                                )
                            traceability_index.create_inline_link(part)
                if requirement.reserved_uid is None:
                    continue

                # Now it is possible to resolve parents first checking if they
                # indeed exist.
                for reference in requirement.relations:
                    if reference.ref_type == ReferenceType.FILE:
                        d_07_file_traceability_index.create_requirement(
                            requirement
                        )
                    elif reference.ref_type == ReferenceType.PARENT:
                        parent_reference: ParentReqReference = assert_cast(
                            reference, ParentReqReference
                        )
                        parent_requirement = traceability_index.graph_database.get_link_value_weak(
                            link_type=GraphLinkType.UID_TO_NODE,
                            lhs_node=parent_reference.ref_uid,
                        )
                        if parent_requirement is None:
                            raise StrictDocException(
                                f"[DocumentIndex.create] "
                                f"Requirement {requirement.reserved_uid} "
                                f"references "
                                f"parent requirement which doesn't exist: "
                                f"{parent_reference.ref_uid}."
                            )
                        traceability_index.graph_database.create_link(
                            link_type=GraphLinkType.NODE_TO_PARENT_NODES,
                            lhs_node=requirement,
                            rhs_node=parent_requirement,
                            edge=parent_reference.role,
                        )
                        traceability_index.graph_database.create_link(
                            link_type=GraphLinkType.NODE_TO_CHILD_NODES,
                            lhs_node=parent_requirement,
                            rhs_node=requirement,
                            edge=parent_reference.role,
                        )

                        # Set document dependencies.
                        parent_document: SDocDocument = assert_cast(
                            parent_requirement.get_document(), SDocDocument
                        )
                        if document != parent_document:
                            # This is where we help the incremental generation to
                            # understand that the related documents must be
                            # re-generated together.
                            file_dependency_manager.add_dependency(
                                document.meta.input_doc_full_path,
                                document.meta.output_document_full_path,
                                parent_document.meta.input_doc_full_path,
                            )
                            file_dependency_manager.add_dependency(
                                parent_document.meta.input_doc_full_path,
                                parent_document.meta.output_document_full_path,
                                document.meta.input_doc_full_path,
                            )
                    elif reference.ref_type == ReferenceType.CHILD:
                        child_reference: ChildReqReference = assert_cast(
                            reference, ChildReqReference
                        )
                        child_requirement = traceability_index.graph_database.get_link_value_weak(
                            link_type=GraphLinkType.UID_TO_NODE,
                            lhs_node=child_reference.ref_uid,
                        )
                        if child_requirement is None:
                            raise StrictDocException(
                                f"[DocumentIndex.create] "
                                f"Requirement {requirement.reserved_uid} "
                                f"references a "
                                f"child requirement that doesn't exist: "
                                f"{child_reference.ref_uid}."
                            )
                        traceability_index.graph_database.create_link(
                            link_type=GraphLinkType.NODE_TO_PARENT_NODES,
                            lhs_node=child_requirement,
                            rhs_node=requirement,
                            edge=child_reference.role,
                        )
                        traceability_index.graph_database.create_link(
                            link_type=GraphLinkType.NODE_TO_CHILD_NODES,
                            lhs_node=requirement,
                            rhs_node=child_requirement,
                            edge=child_reference.role,
                        )
                        # Set document dependencies.
                        if document != child_requirement.document:
                            # This is where we help the incremental generation to
                            # understand that the related documents must be
                            # re-generated together.
                            file_dependency_manager.add_dependency(
                                document.meta.input_doc_full_path,
                                document.meta.output_document_full_path,
                                child_requirement.document.meta.input_doc_full_path,
                            )
                            file_dependency_manager.add_dependency(
                                child_requirement.document.meta.input_doc_full_path,
                                child_requirement.document.meta.output_document_full_path,
                                document.meta.input_doc_full_path,
                            )
                    else:
                        raise AssertionError(reference.ref_type)

        # Iterate for the third time to validate the graph against
        # requirement cycles.
        parents_cycle_detector = TreeCycleDetector()
        children_cycle_detector = TreeCycleDetector()
        for document in document_tree.document_list:
            document_iterator = d_01_document_iterators[document]

            for node in document_iterator.all_content(
                print_fragments=False,
                print_fragments_from_files=False,
            ):
                if not node.is_requirement:
                    continue
                requirement: Union[SDocNode, SDocCompositeNode] = assert_cast(
                    node, (SDocNode, SDocCompositeNode)
                )
                if requirement.reserved_uid is None:
                    continue

                # @relation(SDOC-SRS-30, scope=range_start)
                # Detect cycles
                def parent_cycle_traverse_(node_id):
                    current_node = (
                        traceability_index.graph_database.get_link_value(
                            link_type=GraphLinkType.UID_TO_NODE,
                            lhs_node=node_id,
                        )
                    )
                    return list(
                        map(
                            lambda node_: node_.reserved_uid,
                            traceability_index.graph_database.get_link_values(
                                link_type=GraphLinkType.NODE_TO_PARENT_NODES,
                                lhs_node=current_node,
                            ),
                        )
                    )

                parents_cycle_detector.check_node(
                    requirement.reserved_uid,
                    parent_cycle_traverse_,
                )

                def child_cycle_traverse_(node_id):
                    current_node = (
                        traceability_index.graph_database.get_link_value(
                            link_type=GraphLinkType.UID_TO_NODE,
                            lhs_node=node_id,
                        )
                    )
                    return list(
                        map(
                            lambda node_: node_.reserved_uid,
                            traceability_index.graph_database.get_link_values(
                                link_type=GraphLinkType.NODE_TO_CHILD_NODES,
                                lhs_node=current_node,
                            ),
                        )
                    )

                children_cycle_detector.check_node(
                    requirement.reserved_uid,
                    child_cycle_traverse_,
                )
                # @relation(SDOC-SRS-30, scope=range_end)

        map_documents_by_input_rel_path: Dict[str, SDocDocument] = {}
        for document_ in document_tree.document_list:
            map_documents_by_input_rel_path[
                document_.meta.input_doc_full_path
            ] = document_

        # @relation(SDOC-SRS-109, scope=range_start)
        unique_document_from_file_occurences: Set[str] = set()
        for document_ in document_tree.document_list:
            document_from_file_: DocumentFromFile
            for document_from_file_ in document_.fragments_from_files:
                traceability_index.contains_included_documents = True

                assert isinstance(document_from_file_, DocumentFromFile), (
                    document_from_file_
                )

                assert (
                    document_from_file_.resolved_full_path_to_document_file
                    is not None
                )

                if (
                    document_from_file_.resolved_full_path_to_document_file
                    not in map_documents_by_input_rel_path
                ):
                    raise StrictDocException(
                        "A document includes contains a link to another document "
                        "which is not resolved in the current documentation tree: "
                        f"'{document_from_file_.file}'. This can happen if a single "
                        f"document path is provided as input to a StrictDoc command. "
                        f"Try providing a path to a folder where all documents "
                        f"are stored."
                    )
                resolved_document: SDocDocument = (
                    map_documents_by_input_rel_path[
                        document_from_file_.resolved_full_path_to_document_file
                    ]
                )

                if (
                    document_from_file_.resolved_full_path_to_document_file
                    in unique_document_from_file_occurences
                ) and resolved_document.has_any_requirements():
                    raise StrictDocException(
                        "[DOCUMENT_FROM_FILE]: "
                        "A multiple inclusion of a document is detected. "
                        "A document that contains requirements or other nodes "
                        "can be only included once: "
                        f"{document_from_file_.file}."
                    )
                unique_document_from_file_occurences.add(
                    document_from_file_.resolved_full_path_to_document_file
                )

                document_from_file_.configure_with_resolved_document(
                    resolved_document
                )

        # @relation(SDOC-SRS-109, scope=range_end)

        return traceability_index

    @staticmethod
    def _filter_nodes(
        project_config: ProjectConfig, traceability_index: TraceabilityIndex
    ):
        if (
            project_config.filter_requirements is not None
            or project_config.filter_sections is not None
        ):
            query_reader = QueryReader()
            requirements_query_object: Union[QueryObject, QueryNullObject]
            sections_query_object: Union[QueryObject, QueryNullObject]
            try:
                if project_config.filter_requirements is not None:
                    requirements_query = query_reader.read(
                        project_config.filter_requirements
                    )
                    requirements_query_object = QueryObject(
                        requirements_query, traceability_index
                    )
                else:
                    requirements_query_object = QueryNullObject()
                if project_config.filter_sections is not None:
                    sections_query = query_reader.read(
                        project_config.filter_sections
                    )
                    sections_query_object = QueryObject(
                        sections_query, traceability_index
                    )
                else:
                    sections_query_object = QueryNullObject()
            except TextXSyntaxError:
                print("error: Cannot parse filter query.")  # noqa: T201
                sys.exit(1)
            try:
                for document in traceability_index.document_tree.document_list:
                    document_iterator = (
                        traceability_index.get_document_iterator(document)
                    )
                    for node in document_iterator.all_content():
                        if (
                            node.is_section
                            and not sections_query_object.evaluate(node)
                        ):
                            node.ng_whitelisted = False
                            # If the node is the last one, we check if all other
                            # nodes are filtered out and if so, mark the parent
                            # section node as not whitelisted as well.
                            if (
                                node.parent.section_contents[
                                    len(node.parent.section_contents) - 1
                                ]
                                == node
                            ):
                                if isinstance(node.parent, SDocSection):
                                    node.parent.blacklist_if_needed()

                        elif (
                            node.is_requirement
                            and not requirements_query_object.evaluate(node)
                        ):
                            node.ng_whitelisted = False
                            # If the node is the last one, we check if all other
                            # nodes are filtered out and if so, mark the parent
                            # section node as not whitelisted as well.
                            if (
                                node.parent.section_contents[
                                    len(node.parent.section_contents) - 1
                                ]
                                == node
                            ):
                                if node.parent.is_section:
                                    node.parent.blacklist_if_needed()

            except (AttributeError, NameError, TypeError) as attribute_error_:
                print(  # noqa: T201
                    "error: cannot apply a filter query to a node: "
                    f"{attribute_error_}"
                )
                sys.exit(1)
