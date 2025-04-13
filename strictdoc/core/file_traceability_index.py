# mypy: disable-error-code="arg-type,attr-defined,no-any-return,no-untyped-def"
from copy import copy
from typing import Any, Dict, Iterator, List, Optional, Set, Tuple, Union

from strictdoc.backend.sdoc.error_handling import StrictDocSemanticError
from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.backend.sdoc.models.reference import FileReference
from strictdoc.backend.sdoc.models.type_system import FileEntry
from strictdoc.backend.sdoc_source_code.constants import FunctionAttribute
from strictdoc.backend.sdoc_source_code.models.function import Function
from strictdoc.backend.sdoc_source_code.models.function_range_marker import (
    ForwardFunctionRangeMarker,
    FunctionRangeMarker,
    RangeMarkerType,
)
from strictdoc.backend.sdoc_source_code.models.range_marker import (
    ForwardFileMarker,
    ForwardRangeMarker,
    LineMarker,
    RangeMarker,
)
from strictdoc.backend.sdoc_source_code.models.requirement_marker import Req
from strictdoc.backend.sdoc_source_code.reader import (
    SourceFileTraceabilityInfo,
)
from strictdoc.core.constants import GraphLinkType
from strictdoc.core.source_tree import SourceFile
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.exception import StrictDocException
from strictdoc.helpers.google_test import convert_function_name_to_gtest_macro
from strictdoc.helpers.ordered_set import OrderedSet


class FileTraceabilityIndex:
    def __init__(self):
        # "file.py" -> List[SDocNode]
        self.map_paths_to_reqs: Dict[str, OrderedSet[SDocNode]] = {}

        # "REQ-001" -> {"file.py", ...}
        self.map_reqs_uids_to_paths: Dict[str, OrderedSet[str]] = {}

        # "file.py" -> SourceFileTraceabilityInfo
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
    ) -> List[Tuple[str, List[RangeMarker]]]:
        if requirement.reserved_uid not in self.map_reqs_uids_to_paths:
            return []

        matching_links_with_markers: List[Tuple[str, List[RangeMarker]]] = []
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
            if not markers:
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

    def get_source_file_markers(self, source_file_rel_path: str) -> List[Any]:
        trace_info = self.map_paths_to_source_file_traceability_info[
            source_file_rel_path
        ]
        return trace_info.markers

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

    def validate_and_resolve(self, traceability_index):
        """
        This is a method that finalizes/resolves all the source code
        traceability collected as the traceability index was built.
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
                if FunctionAttribute.DEFINITION in function_.attributes:
                    if function_.is_public():
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
                                f"Could not find a matching Google Test function: {possible_gtest_functions}"
                            )
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

            validated_requirement_uids: Set[str] = set()
            marker_: Union[
                FunctionRangeMarker, LineMarker, RangeMarker, ForwardRangeMarker
            ]
            for marker_ in copy(trace_info_.markers):
                # FIXME: Is this 'continue' needed here?
                if isinstance(marker_, ForwardRangeMarker):
                    continue
                for requirement_uid_ in marker_.reqs:
                    if requirement_uid_ not in validated_requirement_uids:
                        node = traceability_index.get_node_by_uid_weak2(
                            requirement_uid_
                        )
                        if node is None:
                            raise StrictDocException(
                                f"Source file {source_file.in_doctree_source_file_rel_path_posix} references "
                                f"a requirement that does not exist: {requirement_uid_}."
                            )
                        validated_requirement_uids.add(requirement_uid_)

                    self.map_reqs_uids_to_paths.setdefault(
                        requirement_uid_, OrderedSet()
                    ).add(source_file.in_doctree_source_file_rel_path_posix)

                    node_id = traceability_index.get_node_by_uid(
                        requirement_uid_
                    )

                    self.map_paths_to_reqs.setdefault(
                        source_file.in_doctree_source_file_rel_path_posix,
                        OrderedSet(),
                    ).add(node_id)

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
                    FunctionAttribute.DECLARATION in function_.attributes
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
        # STEP: For each trace info object:
        #       - Sort the markers according to their source location.
        #       - Calculate coverage information.
        #
        for (
            path,
            traceability_info_,
        ) in self.map_paths_to_source_file_traceability_info.items():

            def marker_comparator(marker):
                return marker.ng_range_line_begin

            sorted_markers = sorted(
                traceability_info_.markers, key=marker_comparator
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

                def marker_comparator(marker):
                    return marker.ng_range_line_begin, marker.ng_range_line_end

                markers_.sort(key=marker_comparator)

                # validate here, SDocNode.relations doesn't track marker roles
                node = traceability_index.get_node_by_uid(req_uid_)
                assert node.document and node.document.grammar
                grammar_element = node.document.grammar.elements_by_type[
                    node.node_type
                ]
                for marker in markers_:
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

            def compare_sdocnode_by_uid(node_) -> str:
                return assert_cast(node_.reserved_uid, str)

            path_requirements_.sort(key=compare_sdocnode_by_uid)

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
        self, rel_path_posix, name
    ) -> Optional[List[Tuple[str, Optional[str]]]]:
        if rel_path_posix in self.map_file_function_names_to_reqs_uids:
            return self.map_file_function_names_to_reqs_uids[
                rel_path_posix
            ].get(name, None)
        return None

    def get_req_uids_by_class_name(
        self, rel_path_posix, name
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
    ):
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
        function_marker.ng_source_column_begin = 1
        function_marker.ng_range_line_begin = function.line_begin
        function_marker.ng_range_line_end = function.line_end
        function_marker.ng_marker_line = function.line_begin
        function_marker.ng_marker_column = 1
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
