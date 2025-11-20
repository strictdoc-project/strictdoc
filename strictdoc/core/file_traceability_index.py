"""
@relation(SDOC-SRS-28, SDOC-SRS-33, scope=file)
"""

from copy import copy
from typing import (
    TYPE_CHECKING,
    Dict,
    Iterator,
    List,
    Optional,
    Set,
    Tuple,
    Union,
)

from strictdoc.backend.sdoc.document_reference import DocumentReference
from strictdoc.backend.sdoc.error_handling import StrictDocSemanticError
from strictdoc.backend.sdoc.models.document_grammar import (
    DocumentGrammar,
)
from strictdoc.backend.sdoc.models.model import SDocDocumentIF
from strictdoc.backend.sdoc.models.node import SDocNode, SDocNodeField
from strictdoc.backend.sdoc.models.reference import FileEntry, FileReference
from strictdoc.backend.sdoc_source_code.models.function import Function
from strictdoc.backend.sdoc_source_code.models.function_range_marker import (
    ForwardFunctionRangeMarker,
    FunctionRangeMarker,
    RangeMarkerType,
)
from strictdoc.backend.sdoc_source_code.models.line_marker import LineMarker
from strictdoc.backend.sdoc_source_code.models.range_marker import (
    ForwardFileMarker,
    ForwardRangeMarker,
    RangeMarker,
)
from strictdoc.backend.sdoc_source_code.models.requirement_marker import Req
from strictdoc.backend.sdoc_source_code.models.source_file_info import (
    RelationMarkerType,
    SourceFileTraceabilityInfo,
)
from strictdoc.backend.sdoc_source_code.models.source_node import SourceNode
from strictdoc.core.constants import GraphLinkType
from strictdoc.core.document_iterator import SDocDocumentIterator
from strictdoc.core.project_config import ProjectConfig, SourceNodesEntry
from strictdoc.core.source_tree import SourceFile
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.exception import StrictDocException
from strictdoc.helpers.google_test import convert_function_name_to_gtest_macro
from strictdoc.helpers.mid import MID
from strictdoc.helpers.ordered_set import OrderedSet

if TYPE_CHECKING:
    from strictdoc.core.traceability_index import (
        TraceabilityIndex,
    )


class FileTraceabilityIndex:
    def __init__(self) -> None:
        # "file.py" -> List[SDocNode]
        self.map_paths_to_reqs: Dict[str, OrderedSet[SDocNode]] = {}

        # "REQ-001" -> {"file.py", ...}
        self.map_reqs_uids_to_paths: Dict[str, OrderedSet[str]] = {}

        # "file.py" -> SourceFileTraceabilityInfo.
        self.map_paths_to_source_file_traceability_info: Dict[
            str, SourceFileTraceabilityInfo
        ] = {}

        # "file.py" -> { { "foo" -> [("REQ-1", "Impl"), ("REQ-2", "Test")] }, ... }
        self.map_file_function_names_to_reqs_uids: Dict[
            str, Dict[str, List[Tuple[str, Optional[str]]]]
        ] = {}
        self.map_file_class_names_to_reqs_uids: Dict[
            str, Dict[str, List[Tuple[str, Optional[str]]]]
        ] = {}

        # This is only public non-static functions from languages like C.
        self.map_all_function_names_to_definition_functions: Dict[
            str, List[Function]
        ] = {}

        # "file.py" -> [SDocNode]  # noqa: ERA001
        self.source_file_reqs_cache: Dict[str, Optional[List[SDocNode]]] = {}

        self.requirements_with_forward_links: OrderedSet[SDocNode] = (
            OrderedSet()
        )
        self.trace_infos: List[SourceFileTraceabilityInfo] = []

    def has_source_file_reqs(self, source_file_rel_path: str) -> bool:
        path_reqs = self.map_paths_to_reqs.get(source_file_rel_path)
        if path_reqs is not None and len(path_reqs) > 0:
            return True
        file_trace_info = self.map_paths_to_source_file_traceability_info[
            source_file_rel_path
        ]
        return len(file_trace_info.markers) > 0

    def get_requirement_file_links(
        self, requirement: SDocNode
    ) -> List[Tuple[str, List[RelationMarkerType]]]:
        if requirement.reserved_uid not in self.map_reqs_uids_to_paths:
            return []

        matching_links_with_markers: List[
            Tuple[str, List[RelationMarkerType]]
        ] = []
        requirement_source_paths: OrderedSet[str] = self.map_reqs_uids_to_paths[
            requirement.reserved_uid
        ]

        # Now that one requirement can have multiple File-relations to the same file.
        # This can be multiple FUNCTION: or RANGE: forward-relations.
        # To avoid duplication of results, visit each unique file link path only once.
        visited_file_links: Set[str] = set()
        for requirement_source_path_ in requirement_source_paths:
            if requirement_source_path_ in visited_file_links:
                continue
            visited_file_links.add(requirement_source_path_)

            source_file_traceability_info: Optional[
                SourceFileTraceabilityInfo
            ] = self.map_paths_to_source_file_traceability_info.get(
                requirement_source_path_
            )
            assert source_file_traceability_info is not None, (
                f"Requirement {requirement.reserved_uid} references a file"
                f" that does not exist: {requirement_source_path_}."
            )
            markers = source_file_traceability_info.ng_map_reqs_to_markers.get(
                requirement.reserved_uid
            )
            if markers is None or len(markers) == 0:
                matching_links_with_markers.append(
                    (requirement_source_path_, [])
                )
                continue
            matching_links_with_markers.append(
                (requirement_source_path_, markers)
            )

        return matching_links_with_markers

    def indexed_source_files(self) -> Iterator[SourceFile]:
        for _, sfti in self.map_paths_to_source_file_traceability_info.items():
            if sfti.source_file is not None:
                yield sfti.source_file

    def get_source_file_reqs(
        self, source_file_rel_path: str
    ) -> Optional[List[SDocNode]]:
        assert (
            source_file_rel_path
            in self.map_paths_to_source_file_traceability_info
        )
        if source_file_rel_path in self.source_file_reqs_cache:
            return self.source_file_reqs_cache[source_file_rel_path]

        source_file_traceability_info: SourceFileTraceabilityInfo = (
            self.map_paths_to_source_file_traceability_info[
                source_file_rel_path
            ]
        )

        if source_file_rel_path not in self.map_paths_to_reqs:
            self.source_file_reqs_cache[source_file_rel_path] = None
            return None

        requirements = self.map_paths_to_reqs[source_file_rel_path]
        assert len(requirements) > 0
        range_requirements = []

        for requirement in requirements:
            if (
                requirement.reserved_uid
                in source_file_traceability_info.ng_map_reqs_to_markers
            ):
                range_requirements.append(requirement)

        self.source_file_reqs_cache[source_file_rel_path] = range_requirements
        return range_requirements

    def get_coverage_info(
        self, source_file_rel_path: str
    ) -> SourceFileTraceabilityInfo:
        assert (
            source_file_rel_path
            in self.map_paths_to_source_file_traceability_info
        )
        source_file_tr_info: SourceFileTraceabilityInfo = (
            self.map_paths_to_source_file_traceability_info[
                source_file_rel_path
            ]
        )
        return source_file_tr_info

    def get_coverage_info_weak(
        self, source_file_rel_path: str
    ) -> Optional[SourceFileTraceabilityInfo]:
        source_file_tr_info: Optional[SourceFileTraceabilityInfo] = (
            self.map_paths_to_source_file_traceability_info.get(
                source_file_rel_path
            )
        )
        return source_file_tr_info

    def validate_and_resolve(
        self,
        traceability_index: "TraceabilityIndex",
        project_config: ProjectConfig,
    ) -> None:
        """
        Resolve all source code traceability after the index is fully built.
        """

        #
        # STEP: Collect minimal information that will help to resolve the
        #       forward-declared paths/function names at the step 2.
        #
        for trace_info_ in self.trace_infos:
            source_file: SourceFile = assert_cast(
                trace_info_.source_file, SourceFile
            )

            self.map_paths_to_source_file_traceability_info[
                source_file.in_doctree_source_file_rel_path_posix
            ] = trace_info_

            for function_ in trace_info_.functions:
                if function_.is_definition() and function_.is_public():
                    self.map_all_function_names_to_definition_functions.setdefault(
                        function_.name, []
                    ).append(function_)

        #
        # STEP: Resolve requirements that have forward links.
        #       Some requirements can come from the SDoc documents generated
        #       on the fly from JUnit XML documents.
        #
        for forward_requirement_ in self.requirements_with_forward_links:
            assert forward_requirement_.reserved_uid is not None

            for relation_ in forward_requirement_.relations:
                if not isinstance(relation_, FileReference):
                    continue

                file_reference: FileReference = assert_cast(
                    relation_, FileReference
                )
                file_posix_path = file_reference.get_posix_path()

                if file_posix_path == "#FORWARD#":
                    test_function = (
                        forward_requirement_.get_meta_field_value_by_title(
                            "TEST_FUNCTION"
                        )
                    )
                    assert test_function is not None

                    functions: List[Function]
                    if test_function.startswith("#GTEST#"):
                        test_function = test_function.removeprefix("#GTEST#")
                        possible_gtest_functions = (
                            convert_function_name_to_gtest_macro(test_function)
                        )
                        for (
                            possible_gtest_function_
                        ) in possible_gtest_functions:
                            if (
                                possible_gtest_function_
                                in self.map_all_function_names_to_definition_functions
                            ):
                                test_function = possible_gtest_function_
                                break
                        else:
                            raise RuntimeError(
                                "Could not find a matching Google Test function: "
                                f"{possible_gtest_functions}"
                            )  # pragma: no cover
                        forward_requirement_.set_field_value(
                            field_name="TEST_FUNCTION",
                            form_field_index=0,
                            value=test_function,
                        )
                    functions = (
                        self.map_all_function_names_to_definition_functions[
                            test_function
                        ]
                    )
                    assert len(functions) == 1

                    function: Function = functions[0]
                    resolved_path_to_function_file = function.parent.source_file.in_doctree_source_file_rel_path_posix
                    file_posix_path = resolved_path_to_function_file

                    file_reference.g_file_entry = FileEntry(
                        relation_,
                        g_file_format=relation_.g_file_entry.g_file_format,
                        g_file_path=resolved_path_to_function_file,
                        g_line_range=None,
                        function=test_function,
                        clazz=None,
                    )

                    forward_requirement_.set_field_value(
                        field_name="TEST_PATH",
                        form_field_index=0,
                        value=resolved_path_to_function_file,
                    )

                    #
                    # This transitively connects requirements and test results
                    # through the test source files.
                    #
                    for function_marker_ in function.markers:
                        for req_ in function_marker_.reqs:
                            node = traceability_index.get_node_by_uid_weak2(
                                req_
                            )
                            traceability_index.graph_database.create_link(
                                link_type=GraphLinkType.NODE_TO_PARENT_NODES,
                                lhs_node=forward_requirement_,
                                rhs_node=node,
                                edge="Satisfies",
                            )
                            traceability_index.graph_database.create_link(
                                link_type=GraphLinkType.NODE_TO_CHILD_NODES,
                                lhs_node=node,
                                rhs_node=forward_requirement_,
                                edge="IsSatisfiedBy",
                            )
                #
                # Validate that all requirements reference existing files.
                #
                source_file_traceability_info: Optional[
                    SourceFileTraceabilityInfo
                ] = self.map_paths_to_source_file_traceability_info.get(
                    file_posix_path
                )
                if source_file_traceability_info is None:
                    raise StrictDocException(
                        f"Requirement {forward_requirement_.reserved_uid} "
                        "references a file that does not exist: "
                        f"{file_posix_path}."
                    )

                #
                # Now that the test reports related fixups are done, the
                # following code registers the requirements with forward links.
                #
                self.map_paths_to_reqs.setdefault(
                    file_posix_path, OrderedSet()
                ).add(forward_requirement_)

                assert forward_requirement_.reserved_uid is not None
                self.map_reqs_uids_to_paths.setdefault(
                    forward_requirement_.reserved_uid, OrderedSet()
                ).add(file_posix_path)

                if file_reference.g_file_entry.function is not None:
                    one_file_function_name_to_reqs_uids = (
                        self.map_file_function_names_to_reqs_uids.setdefault(
                            file_posix_path, {}
                        )
                    )
                    one_file_function_name_to_reqs_uids.setdefault(
                        file_reference.g_file_entry.function, []
                    ).append(
                        (forward_requirement_.reserved_uid, relation_.role)
                    )
                elif file_reference.g_file_entry.clazz is not None:
                    one_file_class_name_to_reqs_uids = (
                        self.map_file_class_names_to_reqs_uids.setdefault(
                            file_posix_path, {}
                        )
                    )
                    one_file_class_name_to_reqs_uids.setdefault(
                        file_reference.g_file_entry.clazz, []
                    ).append(
                        (forward_requirement_.reserved_uid, relation_.role)
                    )
                elif file_reference.g_file_entry.line_range is not None:
                    line_range = file_reference.g_file_entry.line_range
                    uid = forward_requirement_.reserved_uid
                    source_file_info = (
                        self.map_paths_to_source_file_traceability_info[
                            file_posix_path
                        ]
                    )
                    start_marker, end_marker = (
                        self.forward_range_markers_from_range(
                            line_range, uid, relation_.role
                        )
                    )
                    source_file_info.ng_map_reqs_to_markers.setdefault(
                        uid, []
                    ).append(start_marker)
                    source_file_info.markers.append(start_marker)
                    source_file_info.markers.append(end_marker)
                else:
                    uid = forward_requirement_.reserved_uid
                    source_file_info = (
                        self.map_paths_to_source_file_traceability_info[
                            file_posix_path
                        ]
                    )
                    forward_file_marker = (
                        self.forward_file_marker_from_file_info(
                            source_file_info,
                            uid,
                            relation_.role,
                        )
                    )
                    source_file_info.ng_map_reqs_to_markers.setdefault(
                        forward_requirement_.reserved_uid, []
                    ).append(forward_file_marker)
                    source_file_info.markers.append(forward_file_marker)

        #
        # STEP: Add markers for forward relations to functions and classes
        #
        for trace_info_ in self.trace_infos:
            source_file = assert_cast(trace_info_.source_file, SourceFile)

            self.map_paths_to_source_file_traceability_info[
                source_file.in_doctree_source_file_rel_path_posix
            ] = trace_info_

            for function_ in trace_info_.functions:
                # FIXME: Using display_name, not name. A separate exercise is
                #        to disambiguate forward links to C++ overloaded functions.
                if (
                    reqs_uids := self.get_req_uids_by_function_name(
                        source_file.in_doctree_source_file_rel_path_posix,
                        function_.display_name,
                    )
                ) is not None:
                    self.create_traceability_info_shared_markers_for_function(
                        trace_info_,
                        function_,
                        RangeMarkerType.FUNCTION,
                        reqs_uids,
                    )
                if (
                    reqs_uids := self.get_req_uids_by_class_name(
                        source_file.in_doctree_source_file_rel_path_posix,
                        function_.display_name,
                    )
                ) is not None:
                    self.create_traceability_info_shared_markers_for_function(
                        trace_info_,
                        function_,
                        RangeMarkerType.CLASS,
                        reqs_uids,
                    )

            marker_: Union[
                FunctionRangeMarker, LineMarker, RangeMarker, ForwardRangeMarker
            ]
            for marker_ in copy(trace_info_.markers):
                # FIXME: Is this 'continue' needed here?
                if isinstance(marker_, ForwardRangeMarker):
                    continue
                for requirement_uid_ in marker_.reqs:
                    node = traceability_index.get_node_by_uid_weak2(
                        requirement_uid_
                    )
                    if node is None:
                        raise StrictDocException(
                            f"Source file {source_file.in_doctree_source_file_rel_path_posix} references "
                            f"a requirement that does not exist: {requirement_uid_}."
                        )

                    self.map_reqs_uids_to_paths.setdefault(
                        requirement_uid_, OrderedSet()
                    ).add(source_file.in_doctree_source_file_rel_path_posix)

                    self.map_paths_to_reqs.setdefault(
                        source_file.in_doctree_source_file_rel_path_posix,
                        OrderedSet(),
                    ).add(node)

                if isinstance(marker_, FunctionRangeMarker):
                    marker_copy = marker_.create_end_marker()
                    trace_info_.markers.append(marker_copy)

        #
        # Resolve definitions to declarations (only applicable for C and C++).
        #

        reversed_trace_info = {
            value: key
            for key, value in self.map_paths_to_source_file_traceability_info.items()
        }

        for (
            traceability_info_
        ) in self.map_paths_to_source_file_traceability_info.values():
            for function_ in traceability_info_.functions:
                if (
                    function_.is_declaration()
                    and function_.name
                    in self.map_all_function_names_to_definition_functions
                ):
                    definition_functions: List[Function] = []
                    if not function_.is_public():
                        definition_function = traceability_info_.ng_map_names_to_definition_functions.get(
                            function_.name, None
                        )
                        if definition_function is not None:
                            definition_functions.append(definition_function)
                    else:
                        mapped_definition_functions = (
                            self.map_all_function_names_to_definition_functions[
                                function_.name
                            ]
                        )
                        definition_functions.extend(mapped_definition_functions)
                    if len(definition_functions) == 0:
                        continue

                    for definition_function_ in definition_functions:
                        definition_function_trace_info: SourceFileTraceabilityInfo = definition_function_.parent

                        for marker_ in function_.markers:
                            function_marker = self.forward_function_marker_from_function(
                                function=definition_function_,
                                marker_type=RangeMarkerType.FUNCTION,
                                reqs=marker_.reqs_objs,
                                role=marker_.role,
                                description=f"function {function_.display_name}()",
                            )

                            for req_uid_ in marker_.reqs:
                                definition_function_trace_info.ng_map_reqs_to_markers.setdefault(
                                    req_uid_, []
                                ).append(function_marker)

                                path_to_info = reversed_trace_info[
                                    definition_function_trace_info
                                ]
                                self.map_reqs_uids_to_paths.setdefault(
                                    req_uid_, OrderedSet()
                                ).add(path_to_info)

                                node = traceability_index.get_node_by_uid(
                                    req_uid_
                                )
                                self.map_paths_to_reqs.setdefault(
                                    path_to_info, OrderedSet()
                                ).add(node)

                            definition_function_trace_info.markers.append(
                                function_marker
                            )

        #
        # STEP: Create auto-generated documents created from source file comments.
        #       Register these documents with the main traceability index.
        #
        documents_with_generated_content = set()

        section_cache: Dict[str, Union[SDocDocumentIF, SDocNode]] = {}
        source_nodes_config: List[SourceNodesEntry] = (
            project_config.source_nodes
        )
        unused_source_node_paths = {
            config_entry_.path for config_entry_ in source_nodes_config
        }
        for (
            path_to_source_file_,
            traceability_info_,
        ) in self.map_paths_to_source_file_traceability_info.items():
            if len(traceability_info_.source_nodes) == 0:
                continue

            if len(source_nodes_config) == 0:
                continue

            relevant_source_node_entry = (
                project_config.get_relevant_source_nodes_entry(
                    path_to_source_file_
                )
            )
            if relevant_source_node_entry is not None:
                unused_source_node_paths.discard(
                    relevant_source_node_entry.path
                )
            else:
                continue

            document_uid = relevant_source_node_entry.uid
            document = traceability_index.get_node_by_uid(document_uid)
            documents_with_generated_content.add(document)
            current_top_node = None

            for source_node_ in traceability_info_.source_nodes:
                if len(source_node_.fields) == 0:
                    continue

                assert source_node_.entity_name is not None
                sdoc_node = None
                sdoc_node_uid = source_node_.get_sdoc_field(
                    "UID", relevant_source_node_entry
                )
                mid = source_node_.get_sdoc_field(
                    "MID", relevant_source_node_entry
                )

                # First merge criterion: Merge if SDoc node with same MID exists.
                if mid is not None:
                    sdoc_node_mid = MID(mid)
                    merge_candidate_sdoc_node = (
                        traceability_index.get_node_by_mid_weak(sdoc_node_mid)
                    )
                    if isinstance(merge_candidate_sdoc_node, SDocNode):
                        sdoc_node = merge_candidate_sdoc_node
                        sdoc_node_uid = sdoc_node.reserved_uid

                if sdoc_node is None:
                    # If no UID from source code field or merge-by-MID, create UID by conventional scheme.
                    if sdoc_node_uid is None:
                        sdoc_node_uid = f"{document_uid}/{path_to_source_file_}/{source_node_.entity_name}"
                    # Second merge criterion: Merge if SDoc node with same UID exists.
                    tmp_sdoc_node = traceability_index.get_node_by_uid_weak(
                        sdoc_node_uid
                    )
                    if isinstance(tmp_sdoc_node, SDocNode):
                        sdoc_node = tmp_sdoc_node

                assert sdoc_node_uid is not None
                if sdoc_node is not None:
                    sdoc_node = assert_cast(sdoc_node, SDocNode)
                    self.merge_sdoc_node_with_source_node(
                        relevant_source_node_entry,
                        source_node_,
                        sdoc_node,
                        document,
                    )
                else:
                    sdoc_node = self.create_sdoc_node_from_source_node(
                        source_node_,
                        relevant_source_node_entry,
                        sdoc_node_uid,
                        document,
                    )
                    sdoc_node_uid = assert_cast(sdoc_node.reserved_uid, str)
                    if current_top_node is None:
                        current_top_node = (
                            FileTraceabilityIndex.create_source_node_section(
                                document,
                                path_to_source_file_,
                                section_cache,
                            )
                        )
                    current_top_node.section_contents.append(sdoc_node)

                self.connect_source_node_function(
                    source_node_, sdoc_node_uid, traceability_info_
                )
                self.connect_sdoc_node_with_file_path(
                    sdoc_node, path_to_source_file_
                )
                self.connect_source_node_requirements(
                    source_node_, sdoc_node, traceability_index
                )

        # Warn if source_node was not matched by any include_source_paths, it indicates misconfiguration
        for unused_source_node_path in unused_source_node_paths:
            print(  # noqa: T201
                f"warning: source_node path {unused_source_node_path} doesn't match any source file. "
                "Hint: Check include_source_paths."
            )

        # Iterate over all generated documents to calculate all node levels.
        for document_ in documents_with_generated_content:
            document_iterator = SDocDocumentIterator(document_)
            for _, _ in document_iterator.all_content(
                print_fragments=False,
            ):
                pass

        #
        # STEP: Calculate requirements coverage by code. Sort nodes.
        #
        self.calculate_code_coverage_and_sort_nodes(traceability_index)

    def create_requirement_with_forward_source_links(
        self, requirement: SDocNode
    ) -> None:
        self.requirements_with_forward_links.add(requirement)

    def create_traceability_info(
        self,
        source_file: SourceFile,
        traceability_info: SourceFileTraceabilityInfo,
    ) -> None:
        assert isinstance(traceability_info, SourceFileTraceabilityInfo)
        traceability_info.source_file = source_file

        self.trace_infos.append(traceability_info)

    def get_req_uids_by_function_name(
        self, rel_path_posix: str, name: str
    ) -> Optional[List[Tuple[str, Optional[str]]]]:
        if rel_path_posix in self.map_file_function_names_to_reqs_uids:
            return self.map_file_function_names_to_reqs_uids[
                rel_path_posix
            ].get(name, None)
        return None

    def get_req_uids_by_class_name(
        self, rel_path_posix: str, name: str
    ) -> Optional[List[Tuple[str, Optional[str]]]]:
        if rel_path_posix in self.map_file_class_names_to_reqs_uids:
            return self.map_file_class_names_to_reqs_uids[rel_path_posix].get(
                name, None
            )
        return None

    @staticmethod
    def create_traceability_info_shared_markers_for_function(
        traceability_info: SourceFileTraceabilityInfo,
        function: Function,
        marker_type: RangeMarkerType,
        reqs_uids: List[Tuple[str, Optional[str]]],
    ) -> None:
        markers_by_role = {}
        for req_uid_, role in reqs_uids:
            req = Req(None, req_uid_)
            if role not in markers_by_role:
                markers_by_role[role] = (
                    FileTraceabilityIndex.forward_function_marker_from_function(
                        function, marker_type, [req], role
                    )
                )
            else:
                markers_by_role[role].reqs_objs.append(req)

        for req_uid_, role in reqs_uids:
            markers = traceability_info.ng_map_reqs_to_markers.setdefault(
                req_uid_, []
            )
            markers.append(markers_by_role[role])

        traceability_info.markers.extend(markers_by_role.values())

    @staticmethod
    def forward_function_marker_from_function(
        function: Function,
        marker_type: RangeMarkerType,
        reqs: List[Req],
        role: Optional[str],
        description: Optional[str] = None,
    ) -> ForwardFunctionRangeMarker:
        function_marker = ForwardFunctionRangeMarker(
            parent=None, reqs_objs=reqs, scope=marker_type.value
        )
        function_marker.ng_source_line_begin = function.line_begin
        function_marker.ng_range_line_begin = function.line_begin
        function_marker.ng_range_line_end = function.line_end
        function_marker.role = role
        if description is not None:
            function_marker.set_description(description)
        elif marker_type == RangeMarkerType.FUNCTION:
            function_marker.set_description(
                f"function {function.display_name}()"
            )
        elif marker_type == RangeMarkerType.CLASS:
            function_marker.set_description(f"class {function.name}")
        return function_marker

    @staticmethod
    def forward_range_markers_from_range(
        file_range: Tuple[int, int], requirement_uid_: str, role: Optional[str]
    ) -> Tuple[ForwardRangeMarker, ForwardRangeMarker]:
        start_marker = ForwardRangeMarker(
            start_or_end=True,
            reqs_objs=[Req(parent=None, uid=requirement_uid_)],
            role=role,
        )
        start_marker.ng_range_line_begin = file_range[0]
        start_marker.ng_source_line_begin = file_range[0]
        start_marker.ng_range_line_end = file_range[1]

        end_marker = ForwardRangeMarker(
            start_or_end=False,
            reqs_objs=[Req(parent=None, uid=requirement_uid_)],
            role=role,
        )
        end_marker.ng_source_line_begin = file_range[1]
        end_marker.ng_range_line_begin = file_range[0]
        end_marker.ng_range_line_end = file_range[1]

        return start_marker, end_marker

    @staticmethod
    def forward_file_marker_from_file_info(
        file_info: SourceFileTraceabilityInfo,
        requirement_uid_: str,
        role: Optional[str],
    ) -> ForwardFileMarker:
        marker = ForwardFileMarker(
            reqs_objs=[Req(parent=None, uid=requirement_uid_)],
            role=role,
        )
        marker.ng_range_line_begin = 1
        marker.ng_source_line_begin = 1
        marker.ng_range_line_end = file_info.file_stats.lines_total
        return marker

    def calculate_code_coverage_and_sort_nodes(
        self, traceability_index: "TraceabilityIndex"
    ) -> None:
        """
        Finalize code coverage and sort all nodes.

        For each trace info object:
        - Sort the markers according to their source location.
        - Calculate coverage information.
        """

        for (
            path,
            traceability_info_,
        ) in self.map_paths_to_source_file_traceability_info.items():

            def marker_comparator_start(
                marker: RelationMarkerType,
            ) -> int:
                assert marker.ng_range_line_begin is not None
                return marker.ng_range_line_begin

            sorted_markers = sorted(
                traceability_info_.markers, key=marker_comparator_start
            )

            traceability_info_.markers = sorted_markers
            # Finding how many lines are covered by the requirements in the file.
            # Quick and dirty: https://stackoverflow.com/a/15273749/598057
            merged_ranges: List[List[int]] = []
            for marker_ in traceability_info_.markers:
                assert isinstance(
                    marker_,
                    (
                        FunctionRangeMarker,
                        ForwardRangeMarker,
                        RangeMarker,
                        LineMarker,
                    ),
                ), marker_
                if marker_.ng_is_nodoc:
                    continue
                if not marker_.is_begin():
                    continue
                begin, end = (
                    assert_cast(marker_.ng_range_line_begin, int),
                    assert_cast(marker_.ng_range_line_end, int),
                )
                if merged_ranges and merged_ranges[-1][1] >= (begin - 1):
                    merged_ranges[-1][1] = max(merged_ranges[-1][1], end)
                else:
                    merged_ranges.append([begin, end])
            coverage = 0
            for merged_range in merged_ranges:
                for line_ in range(merged_range[0], merged_range[1] + 1):
                    if traceability_info_.file_stats.lines_info[line_]:
                        coverage += 1

            for function_ in traceability_info_.functions:
                for merged_range in merged_ranges:
                    if (
                        function_.line_begin >= merged_range[0]
                        and function_.line_end <= merged_range[1]
                    ):
                        traceability_info_.covered_functions += 1
                        break

            traceability_info_.set_coverage_stats(merged_ranges, coverage)

            for (
                req_uid_,
                markers_,
            ) in traceability_info_.ng_map_reqs_to_markers.items():

                def marker_comparator_range(
                    marker: RelationMarkerType,
                ) -> Tuple[int, int]:
                    assert marker.ng_range_line_begin is not None
                    assert marker.ng_range_line_end is not None
                    return marker.ng_range_line_begin, marker.ng_range_line_end

                markers_.sort(key=marker_comparator_range)

                # Validate here, SDocNode.relations doesn't track marker roles.
                node = traceability_index.get_node_by_uid(req_uid_)
                document = node.get_document()
                assert document is not None
                assert document.grammar is not None
                grammar_element = document.grammar.elements_by_type[
                    node.node_type
                ]
                for marker in markers_:
                    # Backwards markers do not require referenced node grammar
                    # to have the relation/role registered in the grammar.
                    if isinstance(marker, (FunctionRangeMarker, RangeMarker)):
                        continue

                    if not grammar_element.has_relation_type_role(
                        relation_type="File",
                        relation_role=marker.role,
                    ):
                        raise StrictDocSemanticError.invalid_marker_role(
                            node=node,
                            marker=marker,
                            path_to_src_file=path,
                        )

        # Sort by paths alphabetically.
        for paths_with_role in self.map_reqs_uids_to_paths.values():
            paths_with_role.sort()

        # Sort by node UID alphabetically.
        for path_requirements_ in self.map_paths_to_reqs.values():

            def compare_sdocnode_by_uid(node_: SDocNode) -> str:
                return assert_cast(node_.reserved_uid, str)

            path_requirements_.sort(key=compare_sdocnode_by_uid)

    def connect_source_node_function(
        self,
        source_node: SourceNode,
        source_sdoc_node_uid: str,
        traceability_info: SourceFileTraceabilityInfo,
    ) -> None:
        source_node_function = source_node.function
        assert source_node_function is not None

        function_marker = self.forward_function_marker_from_function(
            function=source_node_function,
            marker_type=RangeMarkerType.FUNCTION,
            reqs=[Req(None, source_sdoc_node_uid)],
            role=None,
            description=f"function {source_node_function.display_name}()",
        )

        traceability_info.ng_map_reqs_to_markers.setdefault(
            source_sdoc_node_uid, []
        ).append(function_marker)
        function_marker_copy = function_marker.create_end_marker()
        traceability_info.markers.append(function_marker)
        traceability_info.markers.append(function_marker_copy)

    @staticmethod
    def create_sdoc_node_from_source_node(
        source_node: SourceNode,
        source_node_config_entry: SourceNodesEntry,
        sdoc_node_uid: str,
        parent_document: SDocDocumentIF,
    ) -> SDocNode:
        sdoc_node = SDocNode(
            parent=parent_document,
            node_type=source_node_config_entry.node_type,
            fields=[],
            relations=[],
            # It is important that this autogenerated node is marked as such.
            autogen=True,
        )
        sdoc_node.ng_document_reference = DocumentReference()
        sdoc_node.ng_document_reference.set_document(parent_document)
        sdoc_node.ng_including_document_reference = DocumentReference()
        sdoc_node_fields = source_node.get_sdoc_fields(source_node_config_entry)
        sdoc_node_fields["UID"] = sdoc_node_uid
        if (
            "TITLE" not in sdoc_node_fields
            and source_node.entity_name is not None
        ):
            sdoc_node_fields["TITLE"] = source_node.entity_name
        FileTraceabilityIndex.set_sdoc_node_fields(sdoc_node, sdoc_node_fields)
        return sdoc_node

    @staticmethod
    def merge_sdoc_node_with_source_node(
        source_node_config_entry: SourceNodesEntry,
        source_node: SourceNode,
        sdoc_node: SDocNode,
        parent_document: SDocDocumentIF,
    ) -> None:
        # First check if grammar element definitions are compatible.
        source_node_type = source_node_config_entry.node_type
        source_node_grammar = assert_cast(
            parent_document.grammar, DocumentGrammar
        )
        source_node_grammar_element = source_node_grammar.elements_by_type[
            source_node_type
        ]
        sdoc_node_document = assert_cast(
            sdoc_node.get_document(), SDocDocumentIF
        )
        sdoc_node_grammar = assert_cast(
            sdoc_node_document.grammar, DocumentGrammar
        )
        sdoc_node_grammar_element = sdoc_node_grammar.elements_by_type[
            source_node_type
        ]
        if source_node_grammar_element != sdoc_node_grammar_element:
            raise StrictDocException(
                f"Can't merge node {sdoc_node.reserved_uid} with source portion: "
                f"Grammar element {sdoc_node_document.reserved_uid}::{source_node_type} "
                f"incompatible with {parent_document.reserved_uid}::{source_node_type}"
            )
        # Merge strategy: overwrite any field if there's a field with same name from custom tags.
        sdoc_node_fields = source_node.get_sdoc_fields(source_node_config_entry)

        # Sanity check: Nor UID neither MID must conflict (early auto-MID is allowed to be overwritten)
        if (
            "MID" in sdoc_node.ordered_fields_lookup
            and "MID" in sdoc_node_fields
        ):
            sdoc_mid_field = sdoc_node.get_field_by_name("MID").get_text_value()
            if sdoc_mid_field != sdoc_node_fields["MID"]:
                raise StrictDocException(
                    f"Can't merge node by UID {sdoc_node.reserved_uid}: "
                    f"Conflicting MID: {sdoc_mid_field} != {sdoc_node_fields['MID']}"
                )
        if sdoc_node.reserved_uid is not None and "UID" in sdoc_node_fields:
            if sdoc_node.reserved_uid != sdoc_node_fields["UID"]:
                raise StrictDocException(
                    f"Can't merge node by MID {sdoc_node.reserved_mid}: "
                    f"Conflicting UID: {sdoc_node.reserved_uid} != {sdoc_node_fields['UID']}"
                )

        FileTraceabilityIndex.set_sdoc_node_fields(sdoc_node, sdoc_node_fields)
        source_node.sdoc_node = sdoc_node

    @staticmethod
    def set_sdoc_node_fields(
        sdoc_node: SDocNode, sdoc_node_fields: dict[str, str]
    ) -> None:
        for field_name, field_value in sdoc_node_fields.items():
            sdoc_node_has_field = field_name in sdoc_node.ordered_fields_lookup

            sdoc_node.set_field_value(
                field_name=field_name,
                form_field_index=0,
                value=field_value,
            )

            if not sdoc_node_has_field:
                new_field: SDocNodeField = sdoc_node.ordered_fields_lookup[
                    field_name
                ][0]
                new_field.mark_as_source_origin()

    @staticmethod
    def create_source_node_section(
        document: SDocDocumentIF,
        path_to_source_file: str,
        section_cache: Dict[str, Union[SDocDocumentIF, SDocNode]],
    ) -> Union[SDocDocumentIF, SDocNode]:
        """
        Add a subsection for each path components in a given file path.
        """
        current_top_node: Union[SDocDocumentIF, SDocNode] = document
        path_components = path_to_source_file.split("/")
        for path_component_idx_, path_component_ in enumerate(path_components):
            if path_component_ not in section_cache:
                path_component_title = (
                    path_component_ + "/"
                    if path_component_idx_ < (len(path_components) - 1)
                    else path_component_
                )
                current_section = SDocNode(
                    parent=current_top_node,
                    node_type="SECTION",
                    fields=[],
                    relations=[],
                    is_composite=True,
                    node_type_close="SECTION",
                    # It is important that this autogenerated node is marked as such.
                    autogen=True,
                )
                current_section.ng_document_reference = DocumentReference()
                current_section.ng_document_reference.set_document(document)
                current_section.ng_including_document_reference = (
                    DocumentReference()
                )
                current_section.set_field_value(
                    field_name="TITLE",
                    form_field_index=0,
                    value=path_component_title,
                )

                current_top_node.section_contents.append(current_section)
                section_cache[path_component_] = current_section
            current_top_node = section_cache[path_component_]
        return current_top_node

    def connect_sdoc_node_with_file_path(
        self, sdoc_node: SDocNode, path_to_source_file_: str
    ) -> None:
        uid = sdoc_node.reserved_uid
        assert uid is not None
        self.map_reqs_uids_to_paths.setdefault(uid, OrderedSet()).add(
            path_to_source_file_
        )
        self.map_paths_to_reqs.setdefault(
            path_to_source_file_, OrderedSet()
        ).add(sdoc_node)

    @staticmethod
    def connect_source_node_requirements(
        source_node: SourceNode,
        sdoc_node: SDocNode,
        traceability_index: "TraceabilityIndex",
    ) -> None:
        """
        Connect auto-generated requirement with function marker and with marker target requirement.

        If function comment has @relation(REQ, scope=function), connections shall become
        [REQ] <-parent- [auto-generated/merged sdoc_node] -file-> [function marker]

        Here we link REQ and sdoc_node bidirectional.
        """
        if (
            sdoc_node.reserved_uid is not None
            and not traceability_index.graph_database.has_link(
                link_type=GraphLinkType.UID_TO_NODE,
                lhs_node=sdoc_node.reserved_uid,
                rhs_node=sdoc_node,
            )
        ):
            traceability_index.graph_database.create_link(
                link_type=GraphLinkType.UID_TO_NODE,
                lhs_node=sdoc_node.reserved_uid,
                rhs_node=sdoc_node,
            )

        # A merge procedure may have overwritten the MID,
        # in which case the graph database and search index needs an update.
        if "MID" in sdoc_node.ordered_fields_lookup != sdoc_node.reserved_mid:
            sdoc_mid_field = sdoc_node.get_field_by_name("MID").get_text_value()
            if sdoc_mid_field != sdoc_node.reserved_mid:
                # TODO:
                # If we really want to support changing the auto-assigned MID,
                # at least the graph database and the document search index need an update (remove old MID, add new MID).
                # I currently struggle to update the search index.
                parent_document = sdoc_node.get_parent_or_including_document()
                sdoc_node.reserved_mid = MID(sdoc_mid_field)
                if parent_document.config.enable_mid:
                    sdoc_node.mid_permanent = True

        if not traceability_index.graph_database.has_link(
            link_type=GraphLinkType.MID_TO_NODE,
            lhs_node=sdoc_node.reserved_mid,
            rhs_node=sdoc_node,
        ):
            traceability_index.graph_database.create_link(
                link_type=GraphLinkType.MID_TO_NODE,
                lhs_node=sdoc_node.reserved_mid,
                rhs_node=sdoc_node,
            )

        for marker_ in source_node.markers:
            if not isinstance(marker_, FunctionRangeMarker):
                continue
            for req_ in marker_.reqs:
                node = traceability_index.get_node_by_uid_weak2(req_)
                if not traceability_index.graph_database.has_link(
                    link_type=GraphLinkType.NODE_TO_PARENT_NODES,
                    lhs_node=sdoc_node,
                    rhs_node=node,
                ):
                    traceability_index.graph_database.create_link(
                        link_type=GraphLinkType.NODE_TO_PARENT_NODES,
                        lhs_node=sdoc_node,
                        rhs_node=node,
                    )
                if not traceability_index.graph_database.has_link(
                    link_type=GraphLinkType.NODE_TO_CHILD_NODES,
                    lhs_node=node,
                    rhs_node=sdoc_node,
                ):
                    traceability_index.graph_database.create_link(
                        link_type=GraphLinkType.NODE_TO_CHILD_NODES,
                        lhs_node=node,
                        rhs_node=sdoc_node,
                    )
