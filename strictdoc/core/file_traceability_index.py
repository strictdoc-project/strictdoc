# mypy: disable-error-code="arg-type,attr-defined,no-any-return,no-untyped-def"
from typing import Any, Dict, Iterator, List, Optional, Set, Tuple, Union

from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.backend.sdoc.models.reference import FileReference, Reference
from strictdoc.backend.sdoc_source_code.constants import FunctionAttribute
from strictdoc.backend.sdoc_source_code.models.function import Function
from strictdoc.backend.sdoc_source_code.models.function_range_marker import (
    ForwardFunctionRangeMarker,
    FunctionRangeMarker,
    RangeMarkerType,
)
from strictdoc.backend.sdoc_source_code.models.range_marker import (
    ForwardRangeMarker,
    LineMarker,
    RangeMarker,
)
from strictdoc.backend.sdoc_source_code.models.requirement_marker import Req
from strictdoc.backend.sdoc_source_code.reader import (
    SourceFileTraceabilityInfo,
)
from strictdoc.core.source_tree import SourceFile
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.exception import StrictDocException
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

        self.map_reqs_uids_to_line_range_file_refs: Dict[
            str, List[Tuple[str, Tuple[int, int]]]
        ] = {}
        self.map_file_function_names_to_reqs_uids: Dict[
            str, Dict[str, List[str]]
        ] = {}
        self.map_file_class_names_to_reqs_uids: Dict[
            str, Dict[str, List[str]]
        ] = {}

        # This is only public non-static functions from languages like C.
        self.map_all_function_names_to_definition_functions: Dict[
            str, List[Function]
        ] = {}

        # "file.py" -> (
        #   general_requirements: [SDocNode],  # noqa: ERA001
        #   range_requirements: [SDocNode]  # noqa: ERA001
        # )  # noqa: ERA001
        self.source_file_reqs_cache = {}

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
    ) -> List[Tuple[str, Optional[List[RangeMarker]]]]:
        if requirement.reserved_uid not in self.map_reqs_uids_to_paths:
            return []

        matching_links_with_opt_ranges: List[
            Tuple[str, Optional[List[RangeMarker]]]
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
            if not markers:
                matching_links_with_opt_ranges.append(
                    (requirement_source_path_, None)
                )
                continue
            matching_links_with_opt_ranges.append(
                (requirement_source_path_, markers)
            )

        return matching_links_with_opt_ranges

    def indexed_source_files(self) -> Iterator[SourceFile]:
        for _, sfti in self.map_paths_to_source_file_traceability_info.items():
            if sfti.source_file is not None:
                yield sfti.source_file

    def get_source_file_reqs(
        self, source_file_rel_path: str
    ) -> Tuple[Optional[List[SDocNode]], Optional[List[SDocNode]]]:
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
            self.source_file_reqs_cache[source_file_rel_path] = (None, None)
            return None, None
        requirements = self.map_paths_to_reqs[source_file_rel_path]
        assert len(requirements) > 0
        general_requirements = []
        range_requirements = []

        for requirement in requirements:
            if (
                requirement.reserved_uid
                in source_file_traceability_info.ng_map_reqs_to_markers
                or requirement.reserved_uid
                in self.map_reqs_uids_to_line_range_file_refs
            ):
                range_requirements.append(requirement)
            else:
                general_requirements.append(requirement)
        self.source_file_reqs_cache[source_file_rel_path] = (
            general_requirements,
            range_requirements,
        )
        return general_requirements, range_requirements

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

    def validate_and_resolve(self, traceability_index):
        for requirement_uid, file_links in self.map_reqs_uids_to_paths.items():
            for file_link in file_links:
                source_file_traceability_info: Optional[
                    SourceFileTraceabilityInfo
                ] = self.map_paths_to_source_file_traceability_info.get(
                    file_link
                )
                if source_file_traceability_info is None:
                    raise StrictDocException(
                        f"Requirement {requirement_uid} references a file"
                        f" that does not exist: {file_link}."
                    )

        for (
            requirement_uid_,
            file_range_pairs_,
        ) in self.map_reqs_uids_to_line_range_file_refs.items():
            for file_range_pair_ in file_range_pairs_:
                path_to_file = file_range_pair_[0]
                file_range = file_range_pair_[1]

                source_file_info = (
                    self.map_paths_to_source_file_traceability_info[
                        path_to_file
                    ]
                )

                start_marker = ForwardRangeMarker(
                    start_or_end=True,
                    reqs_objs=[Req(parent=None, uid=requirement_uid_)],
                )
                start_marker.ng_range_line_begin = file_range[0]
                start_marker.ng_source_line_begin = file_range[0]
                start_marker.ng_range_line_end = file_range[1]

                end_marker = ForwardRangeMarker(
                    start_or_end=False,
                    reqs_objs=[Req(parent=None, uid=requirement_uid_)],
                )
                end_marker.ng_source_line_begin = file_range[1]
                end_marker.ng_range_line_begin = file_range[0]
                end_marker.ng_range_line_end = file_range[1]

                source_file_info.ng_map_reqs_to_markers.setdefault(
                    requirement_uid_, []
                ).append(start_marker)

                source_file_info.markers.append(start_marker)
                source_file_info.markers.append(end_marker)

        """
        Resolve definitions to declarations (only applicable for C and C++).
        """

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
                            function_marker = ForwardFunctionRangeMarker(
                                parent=None,
                                reqs_objs=marker_.reqs_objs,
                                scope="function",
                            )
                            function_marker.ng_source_line_begin = (
                                definition_function_.line_begin
                            )
                            function_marker.ng_source_column_begin = 1
                            function_marker.ng_range_line_begin = (
                                definition_function_.line_begin
                            )
                            function_marker.ng_range_line_end = (
                                definition_function_.line_end
                            )
                            function_marker.ng_marker_line = (
                                definition_function_.line_begin
                            )
                            function_marker.ng_marker_column = 1
                            function_marker.set_description(
                                f"function {function_.display_name}"
                            )

                            for req_uid_ in marker_.reqs:
                                markers = definition_function_trace_info.ng_map_reqs_to_markers.setdefault(
                                    req_uid_, []
                                )
                                markers.append(function_marker)

                                path_to_info = reversed_trace_info[
                                    definition_function_trace_info
                                ]
                                self.map_reqs_uids_to_paths.setdefault(
                                    req_uid_, OrderedSet()
                                )
                                self.map_reqs_uids_to_paths[req_uid_].add(
                                    path_to_info
                                )

                                node = traceability_index.get_node_by_uid(
                                    req_uid_
                                )
                                self.map_paths_to_reqs.setdefault(
                                    path_to_info, OrderedSet()
                                )
                                self.map_paths_to_reqs[path_to_info].add(node)

                            definition_function_trace_info.markers.append(
                                function_marker
                            )

        for (
            traceability_info_
        ) in self.map_paths_to_source_file_traceability_info.values():

            def marker_comparator(marker):
                return marker.ng_range_line_begin

            sorted_markers = sorted(
                traceability_info_.markers, key=marker_comparator
            )

            traceability_info_.markers = sorted_markers
            # Finding how many lines are covered by the requirements in the file.
            # Quick and dirty: https://stackoverflow.com/a/15273749/598057
            merged_ranges: List[List[Any]] = []
            marker: Union[
                FunctionRangeMarker, LineMarker, RangeMarker, ForwardRangeMarker
            ]
            for marker in traceability_info_.markers:
                assert isinstance(
                    marker,
                    (
                        FunctionRangeMarker,
                        ForwardRangeMarker,
                        RangeMarker,
                        LineMarker,
                    ),
                ), marker
                if marker.ng_is_nodoc:
                    continue
                if not marker.is_begin():
                    continue
                begin, end = (
                    assert_cast(marker.ng_range_line_begin, int),
                    assert_cast(marker.ng_range_line_end, int),
                )
                if merged_ranges and merged_ranges[-1][1] >= (begin - 1):
                    merged_ranges[-1][1] = max(merged_ranges[-1][1], end)
                else:
                    merged_ranges.append([begin, end])
            coverage = 0
            for merged_range in merged_ranges:
                coverage += merged_range[1] - merged_range[0] + 1
            traceability_info_.set_coverage_stats(
                traceability_info_.ng_lines_total, coverage
            )

            for markers_ in traceability_info_.ng_map_reqs_to_markers.values():

                def marker_comparator(marker):
                    return marker.ng_range_line_begin, marker.ng_range_line_end

                markers_.sort(key=marker_comparator)

        # Sort by keys alphabetically.
        for paths_ in self.map_reqs_uids_to_paths.values():
            paths_.sort()

    def create_requirement(self, requirement: SDocNode) -> None:
        assert requirement.reserved_uid is not None

        # A requirement can have multiple File references, and this function is
        # called for every File reference.
        if requirement.reserved_uid in self.map_reqs_uids_to_paths:
            return

        ref: Reference
        for ref in requirement.relations:
            if isinstance(ref, FileReference):
                file_reference: FileReference = ref
                requirements = self.map_paths_to_reqs.setdefault(
                    file_reference.get_posix_path(), OrderedSet()
                )
                requirements.add(requirement)

                paths = self.map_reqs_uids_to_paths.setdefault(
                    requirement.reserved_uid, OrderedSet()
                )
                paths.add(ref.get_posix_path())

                if file_reference.g_file_entry.function is not None:
                    one_file_function_name_to_reqs_uids = (
                        self.map_file_function_names_to_reqs_uids.setdefault(
                            file_reference.get_posix_path(), {}
                        )
                    )
                    function_name_to_reqs_uids = (
                        one_file_function_name_to_reqs_uids.setdefault(
                            file_reference.g_file_entry.function, []
                        )
                    )
                    function_name_to_reqs_uids.append(requirement.reserved_uid)
                elif file_reference.g_file_entry.clazz is not None:
                    one_file_class_name_to_reqs_uids = (
                        self.map_file_class_names_to_reqs_uids.setdefault(
                            file_reference.get_posix_path(), {}
                        )
                    )
                    class_name_to_reqs_uids = (
                        one_file_class_name_to_reqs_uids.setdefault(
                            file_reference.g_file_entry.clazz, []
                        )
                    )
                    class_name_to_reqs_uids.append(requirement.reserved_uid)
                elif file_reference.g_file_entry.line_range is not None:
                    assert requirement.reserved_uid is not None
                    req_uid_to_line_range_file_refs = (
                        self.map_reqs_uids_to_line_range_file_refs.setdefault(
                            requirement.reserved_uid, []
                        )
                    )
                    req_uid_to_line_range_file_refs.append(
                        (
                            file_reference.get_posix_path(),
                            file_reference.g_file_entry.line_range,
                        )
                    )

    def create_traceability_info(
        self,
        source_file: SourceFile,
        traceability_info: SourceFileTraceabilityInfo,
        traceability_index,
    ) -> None:
        assert isinstance(traceability_info, SourceFileTraceabilityInfo)
        traceability_info.source_file = source_file
        self.map_paths_to_source_file_traceability_info[
            source_file.in_doctree_source_file_rel_path_posix
        ] = traceability_info

        for function_ in traceability_info.functions:
            marker_type: RangeMarkerType

            if FunctionAttribute.DEFINITION in function_.attributes:
                if function_.is_public():
                    self.map_all_function_names_to_definition_functions.setdefault(
                        function_.name, []
                    )
                    self.map_all_function_names_to_definition_functions[
                        function_.name
                    ].append(function_)

            if (
                source_file.in_doctree_source_file_rel_path_posix
                in self.map_file_function_names_to_reqs_uids
            ):
                # FIXME: Using display_name, not name. A separate exercise is
                #        to disambiguate forward links to C++ overloaded functions.
                reqs_uids = self.map_file_function_names_to_reqs_uids[
                    source_file.in_doctree_source_file_rel_path_posix
                ].get(function_.display_name, None)

                if reqs_uids is not None:
                    marker_type = RangeMarkerType.FUNCTION
                else:
                    continue
            elif (
                source_file.in_doctree_source_file_rel_path_posix
                in self.map_file_class_names_to_reqs_uids
            ):
                reqs_uids = self.map_file_class_names_to_reqs_uids[
                    source_file.in_doctree_source_file_rel_path_posix
                ].get(function_.name, None)
                if reqs_uids is not None:
                    marker_type = RangeMarkerType.CLASS
                else:
                    continue
            else:
                continue

            reqs = []
            for req_uid_ in reqs_uids:
                req = Req(None, req_uid_)
                reqs.append(req)

            function_marker = ForwardFunctionRangeMarker(
                parent=None, reqs_objs=reqs, scope=marker_type.value
            )
            function_marker.ng_source_line_begin = function_.line_begin
            function_marker.ng_source_column_begin = 1
            function_marker.ng_range_line_begin = function_.line_begin
            function_marker.ng_range_line_end = function_.line_end
            function_marker.ng_marker_line = function_.line_begin
            function_marker.ng_marker_column = 1
            if marker_type == RangeMarkerType.FUNCTION:
                function_marker.set_description(
                    f"function {function_.display_name}"
                )
            elif marker_type == RangeMarkerType.CLASS:
                function_marker.set_description(f"class {function_.name}")

            for req_uid_ in reqs_uids:
                markers = traceability_info.ng_map_reqs_to_markers.setdefault(
                    req_uid_, []
                )
                markers.append(function_marker)

            traceability_info.markers.append(function_marker)

        validated_requirement_uids: Set[str] = set()
        for marker_ in traceability_info.markers:
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

                paths = self.map_reqs_uids_to_paths.setdefault(
                    requirement_uid_, OrderedSet()
                )
                paths.add(source_file.in_doctree_source_file_rel_path_posix)

                requirement_paths = self.map_paths_to_reqs.setdefault(
                    source_file.in_doctree_source_file_rel_path_posix,
                    OrderedSet(),
                )

                node_id = traceability_index.get_node_by_uid(requirement_uid_)
                requirement_paths.add(node_id)
