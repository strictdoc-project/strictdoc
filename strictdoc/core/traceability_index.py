from strictdoc.backend.dsl.models.reference import Reference
from strictdoc.backend.dsl.models.requirement import Requirement
from strictdoc.backend.source_file_syntax.reader import (
    SourceFileTraceabilityInfo,
)
from strictdoc.helpers.sorting import alphanumeric_sort


class FileTraceabilityIndex:
    def __init__(self):
        self.map_paths_to_reqs = {}
        self.map_reqs_uids_to_paths = {}
        self.map_paths_to_source_file_traceability_info = {}
        self.source_file_reqs_cache = {}

    def register(self, requirement):
        if requirement.uid in self.map_reqs_uids_to_paths:
            return

        ref: Reference
        for ref in requirement.references:
            if ref.ref_type == "File":
                requirements = self.map_paths_to_reqs.setdefault(ref.path, [])
                requirements.append(requirement)

                paths = self.map_reqs_uids_to_paths.setdefault(
                    requirement.uid, []
                )
                paths.append(ref.path)

    def get_requirement_file_links(self, requirement):
        if requirement.uid not in self.map_reqs_uids_to_paths:
            return []

        matching_links_with_opt_ranges = []
        file_links = self.map_reqs_uids_to_paths[requirement.uid]
        for file_link in file_links:
            source_file_traceability_info: SourceFileTraceabilityInfo = (
                self.map_paths_to_source_file_traceability_info.get(file_link)
            )
            if not source_file_traceability_info:
                print(
                    f"warning: Requirement {requirement.uid} references "
                    f"a file that does not exist: {file_link}"
                )
                matching_links_with_opt_ranges.append((file_link, None))
                continue
            pragmas = source_file_traceability_info.ng_map_reqs_to_pragmas.get(
                requirement.uid
            )
            if not pragmas:
                matching_links_with_opt_ranges.append((file_link, None))
                continue
            matching_links_with_opt_ranges.append((file_link, pragmas))
        return matching_links_with_opt_ranges

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
                print(
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
                requirement.uid
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


class TraceabilityIndex:
    def __init__(
        self,
        document_iterators,
        requirements_parents,
        tags_map,
        documents_ref_depth_map,
        file_traceability_index: FileTraceabilityIndex,
    ):
        self._document_iterators = document_iterators
        self._requirements_parents = requirements_parents
        self._tags_map = tags_map
        self._documents_ref_depth_map = documents_ref_depth_map
        self._file_traceability_index = file_traceability_index

    def has_requirements(self):
        return len(self.requirements_parents.keys()) > 0

    @property
    def document_iterators(self):
        return self._document_iterators

    @property
    def requirements_parents(self):
        return self._requirements_parents

    @property
    def tags_map(self):
        return self._tags_map

    @property
    def documents_ref_depth_map(self):
        return self._documents_ref_depth_map

    def get_document_iterator(self, document):
        return self.document_iterators[document]

    def get_parent_requirements(self, requirement: Requirement):
        assert isinstance(requirement, Requirement)
        if not isinstance(requirement.uid, str):
            return []

        if not requirement.uid or len(requirement.uid) == 0:
            return []

        if not self.requirements_parents:
            return []

        parent_requirements = self.requirements_parents[requirement.uid][
            "parents"
        ]
        return parent_requirements

    def has_parent_requirements(self, requirement: Requirement):
        assert isinstance(requirement, Requirement)
        if not isinstance(requirement.uid, str):
            return False

        if not requirement.uid or len(requirement.uid) == 0:
            return False

        if len(self.requirements_parents) == 0:
            return False

        parent_requirements = self.requirements_parents[requirement.uid][
            "parents"
        ]
        return len(parent_requirements) > 0

    def has_children_requirements(self, requirement: Requirement):
        assert isinstance(requirement, Requirement)
        if not isinstance(requirement.uid, str):
            return False

        if not requirement.uid or len(requirement.uid) == 0:
            return False

        if not self.requirements_parents:
            return False

        children_requirements = self.requirements_parents[requirement.uid][
            "children"
        ]
        return len(children_requirements) > 0

    def get_children_requirements(self, requirement: Requirement):
        assert isinstance(requirement, Requirement)
        if not isinstance(requirement.uid, str):
            return []

        if len(requirement.uid) == 0:
            return []

        if not self.requirements_parents:
            return []

        children_requirements = self.requirements_parents[requirement.uid][
            "children"
        ]
        return children_requirements

    def get_link(self, requirement):
        document = self.requirements_parents[requirement.uid]["document"]
        return "{} - Traceability.html#{}".format(
            document.name, requirement.uid
        )

    def get_deep_link(self, requirement):
        document = self.requirements_parents[requirement.uid]["document"]
        return "{} - Traceability Deep.html#{}".format(
            document.name, requirement.uid
        )

    def has_tags(self, document):
        if document.name not in self.tags_map:
            return False
        tags_bag = self.tags_map[document.name]
        return len(tags_bag.keys())

    def get_tags(self, document):
        assert document.name in self.tags_map
        tags_bag = self.tags_map[document.name]
        if not tags_bag:
            yield []
            return

        tags = sorted(tags_bag.keys(), key=alphanumeric_sort)
        for tag in tags:
            yield tag, tags_bag[tag]

    def get_max_ref_depth(self, document):
        return self.documents_ref_depth_map[document]

    def get_requirement_file_links(self, requirement):
        return self._file_traceability_index.get_requirement_file_links(
            requirement
        )

    def get_source_file_reqs(self, source_file_rel_path):
        return self._file_traceability_index.get_source_file_reqs(
            source_file_rel_path
        )

    def get_coverage_info(self, source_file_rel_path):
        return self._file_traceability_index.get_coverage_info(
            source_file_rel_path
        )

    def get_node_by_uid(self, uid):
        return self._requirements_parents[uid]["requirement"]

    def attach_traceability_info(
        self,
        source_file_rel_path: str,
        traceability_info: SourceFileTraceabilityInfo,
    ):
        assert isinstance(traceability_info, SourceFileTraceabilityInfo)
        self._file_traceability_index.attach_traceability_info(
            source_file_rel_path, traceability_info
        )
