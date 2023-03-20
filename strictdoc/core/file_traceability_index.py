from typing import Dict, List, Optional, Tuple

from strictdoc.backend.sdoc.models.reference import FileReference, Reference
from strictdoc.backend.sdoc_source_code.models.range_pragma import RangePragma
from strictdoc.backend.sdoc_source_code.reader import (
    SourceFileTraceabilityInfo,
)


class FileTraceabilityIndex:
    def __init__(self):
        self.map_paths_to_reqs = {}
        self.map_reqs_uids_to_paths: Dict[str, List[FileReference]] = {}
        self.map_paths_to_source_file_traceability_info: Dict[
            str, SourceFileTraceabilityInfo
        ] = {}
        self.source_file_reqs_cache = {}

    def register(self, requirement):
        if requirement.reserved_uid in self.map_reqs_uids_to_paths:
            return

        ref: Reference
        for ref in requirement.references:
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

    def get_requirement_file_links(self, requirement):
        if requirement.reserved_uid not in self.map_reqs_uids_to_paths:
            return []

        matching_links_with_opt_ranges: List[
            Tuple[FileReference, Optional[List[RangePragma]]]
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
            if not source_file_traceability_info:
                print(  # noqa: T201
                    "warning: "
                    f"Requirement {requirement.reserved_uid} references a file"
                    f" that does not exist: {file_link.get_posix_path()}"
                )
                matching_links_with_opt_ranges.append((file_link, None))
                continue
            pragmas = source_file_traceability_info.ng_map_reqs_to_pragmas.get(
                requirement.reserved_uid
            )
            if not pragmas:
                matching_links_with_opt_ranges.append((file_link, None))
                continue
            matching_links_with_opt_ranges.append((file_link, pragmas))
        return matching_links_with_opt_ranges

    def has_source_file_reqs(self, source_file_rel_path):
        return self.map_paths_to_reqs.get(source_file_rel_path) is not None

    def get_source_file_reqs(self, source_file_rel_path):
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
        ) in source_file_traceability_info.ng_map_reqs_to_pragmas.keys():
            if req_uid not in self.map_reqs_uids_to_paths:
                print(  # noqa: T201
                    f"warning: source file {source_file_rel_path} references "
                    f"a requirement that does not exist: {req_uid}"
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
                not in source_file_traceability_info.ng_map_reqs_to_pragmas
            ):
                general_requirements.append(requirement)
            else:
                range_requirements.append(requirement)
        self.source_file_reqs_cache[source_file_rel_path] = (
            general_requirements,
            range_requirements,
        )
        return general_requirements, range_requirements

    def get_coverage_info(self, source_file_rel_path):
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

    def attach_traceability_info(
        self,
        source_file_rel_path: str,
        traceability_info: SourceFileTraceabilityInfo,
    ):
        assert isinstance(traceability_info, SourceFileTraceabilityInfo)
        self.map_paths_to_source_file_traceability_info[
            source_file_rel_path
        ] = traceability_info
