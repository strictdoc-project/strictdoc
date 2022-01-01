from strictdoc.backend.sdoc.models.requirement import Requirement
from strictdoc.backend.source_file_syntax.reader import (
    SourceFileTraceabilityInfo,
)
from strictdoc.core.file_traceability_index import FileTraceabilityIndex
from strictdoc.helpers.sorting import alphanumeric_sort


class TraceabilityIndex:  # pylint: disable=too-many-public-methods
    def __init__(  # pylint: disable=too-many-arguments
        self,
        document_iterators,
        requirements_parents,
        tags_map,
        documents_ref_depth_map,
        document_parents_map,
        document_children_map,
        file_traceability_index: FileTraceabilityIndex,
    ):
        self._document_iterators = document_iterators
        self._requirements_parents = requirements_parents
        self._tags_map = tags_map
        self._documents_ref_depth_map = documents_ref_depth_map
        self._document_parents_map = document_parents_map
        self._document_children_map = document_children_map
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
        return f"{document.name} - Traceability.html#{requirement.uid}"

    def get_deep_link(self, requirement):
        document = self.requirements_parents[requirement.uid]["document"]
        return f"{document.name} - Traceability Deep.html#{requirement.uid}"

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

    def has_source_file_reqs(self, source_file_rel_path):
        return self._file_traceability_index.has_source_file_reqs(
            source_file_rel_path
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

    def get_document_children(self, document):
        return self._document_children_map[document]

    def get_document_parents(self, document):
        return self._document_parents_map[document]
