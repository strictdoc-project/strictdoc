from datetime import datetime
from typing import Dict, List, Optional, Set

from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.models.requirement import Requirement
from strictdoc.backend.sdoc_source_code.reader import (
    SourceFileTraceabilityInfo,
)
from strictdoc.core.document_iterator import DocumentCachingIterator
from strictdoc.core.document_tree import DocumentTree
from strictdoc.core.file_traceability_index import FileTraceabilityIndex
from strictdoc.core.tree_cycle_detector import TreeCycleDetector
from strictdoc.helpers.auto_described import auto_described
from strictdoc.helpers.sorting import alphanumeric_sort


@auto_described
class RequirementConnections:
    def __init__(  # pylint: disable=too-many-arguments
        self,
        requirement: Requirement,
        document: Document,
        parents: List[Requirement],
        parents_uids: List[str],
        children: List[Requirement],
    ):
        self.requirement: Requirement = requirement
        self.document: Document = document
        self.parents: List[Requirement] = parents
        self.parents_uids: List[str] = parents_uids
        self.children: List[Requirement] = children


class TraceabilityIndex:  # pylint: disable=too-many-public-methods, too-many-instance-attributes  # noqa: E501
    def __init__(  # pylint: disable=too-many-arguments
        self,
        document_iterators: Dict[Document, DocumentCachingIterator],
        requirements_parents: Dict[str, RequirementConnections],
        tags_map,
        document_parents_map: Dict[Document, Set[Document]],
        document_children_map: Dict[Document, Set[Document]],
        file_traceability_index: FileTraceabilityIndex,
        map_id_to_node,
    ):
        self._document_iterators: Dict[
            Document, DocumentCachingIterator
        ] = document_iterators
        self._requirements_parents: Dict[
            str, RequirementConnections
        ] = requirements_parents
        self._tags_map = tags_map
        self._document_parents_map: Dict[
            Document, Set[Document]
        ] = document_parents_map
        self._document_children_map: Dict[
            Document, Set[Document]
        ] = document_children_map
        self._file_traceability_index = file_traceability_index
        self._map_id_to_node = map_id_to_node

        self.document_tree: Optional[DocumentTree] = None
        self.asset_dirs = None
        self.index_last_updated = datetime.today()
        self.strictdoc_last_update = None

    def has_requirements(self):
        return len(self.requirements_parents.keys()) > 0

    @property
    def document_iterators(self):
        return self._document_iterators

    @property
    def requirements_parents(self) -> Dict[str, RequirementConnections]:
        return self._requirements_parents

    @property
    def tags_map(self):
        return self._tags_map

    def get_document_iterator(self, document) -> DocumentCachingIterator:
        return self.document_iterators[document]

    def get_parent_requirements(self, requirement: Requirement):
        assert isinstance(requirement, Requirement)
        if not isinstance(requirement.reserved_uid, str):
            return []

        if len(requirement.reserved_uid) == 0:
            return []

        parent_requirements = self.requirements_parents[
            requirement.reserved_uid
        ].parents
        return parent_requirements

    def has_parent_requirements(self, requirement: Requirement):
        assert isinstance(requirement, Requirement)
        if not isinstance(requirement.reserved_uid, str):
            return False

        if len(requirement.reserved_uid) == 0:
            return False

        parent_requirements = self.requirements_parents[
            requirement.reserved_uid
        ].parents
        return len(parent_requirements) > 0

    def has_children_requirements(self, requirement: Requirement):
        assert isinstance(requirement, Requirement)
        if not isinstance(requirement.reserved_uid, str):
            return False

        if len(requirement.reserved_uid) == 0:
            return False

        children_requirements = self.requirements_parents[
            requirement.reserved_uid
        ].children
        return len(children_requirements) > 0

    def get_children_requirements(
        self, requirement: Requirement
    ) -> List[Requirement]:
        assert isinstance(requirement, Requirement)
        if not isinstance(requirement.reserved_uid, str):
            return []

        if len(requirement.reserved_uid) == 0:
            return []

        children_requirements = self.requirements_parents[
            requirement.reserved_uid
        ].children
        return children_requirements

    def has_tags(self, document):
        if document.title not in self.tags_map:
            return False
        tags_bag = self.tags_map[document.title]
        return len(tags_bag.keys())

    def get_tags(self, document):
        assert document.title in self.tags_map
        tags_bag = self.tags_map[document.title]
        if not tags_bag:
            yield []
            return

        tags = sorted(tags_bag.keys(), key=alphanumeric_sort)
        for tag in tags:
            yield tag, tags_bag[tag]

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
        return self._requirements_parents[uid].requirement

    def attach_traceability_info(
        self,
        source_file_rel_path: str,
        traceability_info: SourceFileTraceabilityInfo,
    ):
        assert isinstance(traceability_info, SourceFileTraceabilityInfo)
        self._file_traceability_index.attach_traceability_info(
            source_file_rel_path, traceability_info
        )

    def get_document_children(self, document) -> Set[Document]:
        return self._document_children_map[document]

    def get_document_parents(self, document) -> Set[Document]:
        return self._document_parents_map[document]

    def get_node_by_id(self, node_id):
        assert isinstance(node_id, str), f"{node_id}"
        return self._map_id_to_node[node_id]

    def mut_add_uid_to_a_requirement_if_needed(self, requirement: Requirement):
        if requirement.reserved_uid is None:
            return
        self.requirements_parents[
            requirement.reserved_uid
        ] = RequirementConnections(
            requirement=requirement,
            document=requirement.document,
            parents=[],
            parents_uids=[],
            children=[],
        )

    def mut_rename_uid_to_a_requirement(
        self, requirement: Requirement, old_uid: Optional[str]
    ) -> None:
        if old_uid is None:
            self.mut_add_uid_to_a_requirement_if_needed(requirement)
            return

        existing_entry = self.requirements_parents[old_uid]
        del self.requirements_parents[old_uid]
        if requirement.reserved_uid is not None:
            self.requirements_parents[requirement.reserved_uid] = existing_entry

    def update_requirement_parent_uid(
        self, requirement: Requirement, parent_uid: str
    ) -> None:
        assert requirement.reserved_uid is not None
        assert isinstance(parent_uid, str), parent_uid
        requirement_connections: RequirementConnections = (
            self._requirements_parents[requirement.reserved_uid]
        )
        # If the parent uid already exists, there is nothing to do.
        if parent_uid in requirement_connections.parents_uids:
            return
        parent_requirement_connections: RequirementConnections = (
            self._requirements_parents[parent_uid]
        )

        parent_requirement = parent_requirement_connections.requirement
        document = requirement.document
        parent_requirement_document = parent_requirement.document

        requirement_connections.parents_uids.append(parent_uid)
        requirement_connections.parents.append(parent_requirement)
        parent_requirement_connections.children.append(requirement)
        self._document_parents_map[document].add(parent_requirement_document)
        self._document_children_map[parent_requirement_document].add(document)
        cycle_detector = TreeCycleDetector(self.requirements_parents)
        cycle_detector.check_node(
            requirement.reserved_uid,
            lambda requirement_id: self.requirements_parents[
                requirement_id
            ].parents_uids,
        )

        # Mark document and parent document (if different) for re-generation.
        document.ng_needs_generation = True
        if parent_requirement_document != document:
            parent_requirement_document.ng_needs_generation = True

    def remove_requirement_parent_uid(
        self, requirement: Requirement, parent_uid: str
    ) -> None:
        assert requirement.reserved_uid is not None
        assert isinstance(parent_uid, str), parent_uid
        requirement_connections: RequirementConnections = (
            self._requirements_parents[requirement.reserved_uid]
        )
        parent_requirement_connections: RequirementConnections = (
            self._requirements_parents[parent_uid]
        )

        parent_requirement = parent_requirement_connections.requirement
        document = requirement.document
        parent_requirement_document = parent_requirement.document

        requirement_connections.parents_uids.remove(parent_uid)
        requirement_connections.parents.remove(parent_requirement)
        parent_requirement_connections.children.remove(requirement)

        # If there are no requirements linking with the parent document,
        # remove the link.
        should_disconnect_documents = True
        for node in self.document_iterators[document].all_content():
            if not node.is_requirement:
                continue
            requirement_node: Requirement = node
            if requirement_node in parent_requirement_connections.children:
                should_disconnect_documents = False
                break

        if should_disconnect_documents:
            self._document_parents_map[document].remove(
                parent_requirement_document
            )
            self._document_children_map[parent_requirement_document].remove(
                document
            )

        # Mark document and parent document (if different) for re-generation.
        document.ng_needs_generation = True
        if parent_requirement_document != document:
            parent_requirement_document.ng_needs_generation = True
