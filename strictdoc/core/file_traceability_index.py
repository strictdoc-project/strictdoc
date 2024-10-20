# mypy: disable-error-code="arg-type,attr-defined,no-any-return,no-untyped-def"
from typing import Any, Dict, List, Optional, Tuple

from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.backend.sdoc.models.reference import FileReference, Reference
from strictdoc.backend.sdoc_source_code.models.range_marker import (
    ForwardRangeMarker,
    RangeMarker,
)
from strictdoc.backend.sdoc_source_code.models.requirement_marker import Req
from strictdoc.backend.sdoc_source_code.reader import (
    SourceFileTraceabilityInfo,
)
from strictdoc.helpers.exception import StrictDocException


class FileTraceabilityIndex:
    def __init__(self):
        # "file.py" -> List[SDocNode]
        self.map_paths_to_reqs: Dict[str, List[SDocNode]] = {}

        # "REQ-001" -> List[FileReference]
        self.map_reqs_uids_to_paths: Dict[str, List[FileReference]] = {}

        # "file.py" -> SourceFileTraceabilityInfo
        self.map_paths_to_source_file_traceability_info: Dict[
            str, SourceFileTraceabilityInfo
        ] = {}

        self.map_reqs_uids_to_line_range_file_refs: Dict[str, List[Any]] = {}

        # "file.py" -> (
        #   general_requirements: [SDocNode],  # noqa: ERA001
        #   range_requirements: [SDocNode]  # noqa: ERA001
        # )  # noqa: ERA001
        self.source_file_reqs_cache = {}

    def has_source_file_reqs(self, source_file_rel_path: str) -> bool:
        return self.map_paths_to_reqs.get(source_file_rel_path) is not None

    def get_requirement_file_links(
        self, requirement: SDocNode
    ) -> List[Tuple[FileReference, Optional[List[RangeMarker]]]]:
        if requirement.reserved_uid not in self.map_reqs_uids_to_paths:
            return []

        matching_links_with_opt_ranges: List[
            Tuple[FileReference, Optional[List[RangeMarker]]]
        ] = []
        file_links: List[FileReference] = self.map_reqs_uids_to_paths[
            requirement.reserved_uid
        ]
        for file_link in file_links:
            source_file_traceability_info: Optional[
                SourceFileTraceabilityInfo
            ] = self.map_paths_to_source_file_traceability_info.get(
                file_link.get_posix_path()
            )
            assert source_file_traceability_info is not None, (
                f"Requirement {requirement.reserved_uid} references a file"
                f" that does not exist: {file_link.get_posix_path()}."
            )
            markers = source_file_traceability_info.ng_map_reqs_to_markers.get(
                requirement.reserved_uid
            )
            if not markers:
                matching_links_with_opt_ranges.append((file_link, None))
                continue
            matching_links_with_opt_ranges.append((file_link, markers))

        return matching_links_with_opt_ranges

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
        for (
            req_uid
        ) in source_file_traceability_info.ng_map_reqs_to_markers.keys():
            if req_uid not in self.map_reqs_uids_to_paths:
                raise StrictDocException(
                    f"Source file {source_file_rel_path} references "
                    f"a requirement that does not exist: {req_uid}."
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

    def validate(self):
        for requirement_uid, file_links in self.map_reqs_uids_to_paths.items():
            for file_link in file_links:
                source_file_traceability_info: Optional[
                    SourceFileTraceabilityInfo
                ] = self.map_paths_to_source_file_traceability_info.get(
                    file_link.get_posix_path()
                )
                if source_file_traceability_info is None:
                    raise StrictDocException(
                        f"Requirement {requirement_uid} references a file"
                        f" that does not exist: {file_link.get_posix_path()}."
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

        # assert 0, self.map_reqs_uids_to_line_range_file_refs

    def create_requirement(self, requirement: SDocNode) -> None:
        # A requirement can have multiple File references, and this function is
        # called for every File reference.
        if requirement.reserved_uid in self.map_reqs_uids_to_paths:
            return

        ref: Reference
        for ref in requirement.relations:
            if isinstance(ref, FileReference):
                file_reference: FileReference = ref
                requirements = self.map_paths_to_reqs.setdefault(
                    file_reference.get_posix_path(), []
                )
                requirements.append(requirement)

                paths = self.map_reqs_uids_to_paths.setdefault(
                    requirement.reserved_uid, []
                )
                paths.append(ref)

                if file_reference.g_file_entry.line_range is not None:
                    requirements = (
                        self.map_reqs_uids_to_line_range_file_refs.setdefault(
                            requirement.reserved_uid, []
                        )
                    )
                    requirements.append(
                        (
                            file_reference.get_posix_path(),
                            file_reference.g_file_entry.line_range,
                        )
                    )

    def create_traceability_info(
        self,
        source_file_rel_path: str,
        traceability_info: SourceFileTraceabilityInfo,
    ) -> None:
        assert isinstance(traceability_info, SourceFileTraceabilityInfo)
        self.map_paths_to_source_file_traceability_info[
            source_file_rel_path
        ] = traceability_info
