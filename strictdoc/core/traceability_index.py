from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Union

from strictdoc.backend.sdoc.models.anchor import Anchor
from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.models.inline_link import InlineLink
from strictdoc.backend.sdoc.models.requirement import Requirement
from strictdoc.backend.sdoc.models.section import Section
from strictdoc.backend.sdoc_source_code.reader import (
    SourceFileTraceabilityInfo,
)
from strictdoc.core.commands.validation_error import (
    SingleValidationError,
)
from strictdoc.core.document_iterator import DocumentCachingIterator
from strictdoc.core.document_tree import DocumentTree
from strictdoc.core.file_traceability_index import FileTraceabilityIndex
from strictdoc.core.graph_database import GraphDatabase, LinkType
from strictdoc.core.tree_cycle_detector import TreeCycleDetector
from strictdoc.helpers.auto_described import auto_described
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.mid import MID
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


class GraphLinkType(LinkType):
    SECTIONS_TO_INCOMING_LINKS = 1


class TraceabilityIndex:  # pylint: disable=too-many-public-methods, too-many-instance-attributes  # noqa: E501
    def __init__(  # pylint: disable=too-many-arguments
        self,
        document_iterators: Dict[Document, DocumentCachingIterator],
        requirements_parents: Dict[str, RequirementConnections],
        tags_map,
        document_parents_map: Dict[Document, Set[Document]],
        document_children_map: Dict[Document, Set[Document]],
        file_traceability_index: FileTraceabilityIndex,
        map_id_to_node: Dict[MID, Any],
        graph_database: GraphDatabase,
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
        self._map_id_to_node: Dict[MID, Any] = map_id_to_node

        self.graph_database: GraphDatabase = graph_database
        self.document_tree: Optional[DocumentTree] = None
        self.asset_dirs = None
        self.index_last_updated = datetime.today()
        self.strictdoc_last_update = None

    def is_small_project(self):
        """
        This method helps to decide if StrictDoc will precompile Jinja templates
        to Python files or not. Precompilation may take half a second time, so
        it is only worth doing it when a project is relatively large.

        Below, making some assumptions about what makes a small or larger
        project.
        """

        if len(self.document_tree.document_list) >= 3:
            return False
        for document_ in self.document_tree.document_list:
            if len(document_.section_contents) > 5:
                return False
        return len(self._requirements_parents) <= 10

    def get_node_by_mid(self, node_id: MID) -> Any:
        assert isinstance(node_id, MID), node_id
        return self._map_id_to_node[node_id]

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

    def get_file_traceability_index(self) -> FileTraceabilityIndex:
        return self._file_traceability_index

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

    def get_coverage_info(
        self, source_file_rel_path
    ) -> SourceFileTraceabilityInfo:
        return self._file_traceability_index.get_coverage_info(
            source_file_rel_path
        )

    def get_node_by_uid(self, uid):
        return self._requirements_parents[uid].requirement

    def find_node_by_uid_weak(
        self, uid
    ) -> Union[Document, Section, Requirement, None]:
        for document in self.document_tree.document_list:
            document_iterator = DocumentCachingIterator(document)
            for node in document_iterator.all_content():
                if isinstance(node, Document):
                    if node.config.uid == uid:
                        return node
                elif isinstance(node, Section):
                    if node.reserved_uid == uid:
                        return node
                elif isinstance(node, Requirement):
                    if node.reserved_uid == uid:
                        return node
                else:
                    raise NotImplementedError
        return None

    def get_section_by_uid_weak(self, uid):
        if uid not in self._requirements_parents:
            return None
        return self._requirements_parents[uid].requirement

    def get_anchor_by_uid_weak(self, uid) -> Optional[Anchor]:
        anchor = self.graph_database.get_node_by_uid_weak(uid)
        if anchor is not None:
            return assert_cast(anchor, Anchor)
        return None

    def get_linkable_node_by_uid_weak(
        self, uid
    ) -> Union[Section, Anchor, None]:
        linked_to_node: Union[
            Section, Anchor, None
        ] = self.get_section_by_uid_weak(uid)
        if linked_to_node is None:
            linked_to_node = self.get_anchor_by_uid_weak(uid)
        return linked_to_node

    def find_node_with_duplicate_anchor(
        self, anchor_uid: str
    ) -> Union[Document, Section]:
        for document in self.document_tree.document_list:
            if len(document.free_texts) > 0:
                for part in document.free_texts[0].parts:
                    if isinstance(part, Anchor) and part.value == anchor_uid:
                        return document
            document_iterator = DocumentCachingIterator(document)
            for node in document_iterator.all_content():
                if not isinstance(node, (Document, Section)):
                    continue
                if len(node.free_texts) > 0:
                    for part in node.free_texts[0].parts:
                        if (
                            isinstance(part, Anchor)
                            and part.value == anchor_uid
                        ):
                            return node
        raise NotImplementedError(
            f"Could not find a node with an anchor by anchor UID: {anchor_uid}"
        )

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

    def update_last_updated(self):
        self.index_last_updated = datetime.today()

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

    def create_inline_link(self, new_link: InlineLink):
        assert isinstance(new_link, InlineLink)

        # InlineLink points to a section.
        if new_link.link in self.requirements_parents:
            section_connections: RequirementConnections = assert_cast(
                self.requirements_parents[new_link.link], RequirementConnections
            )
            self.graph_database.add_link(
                link_type=GraphLinkType.SECTIONS_TO_INCOMING_LINKS,
                lhs_node=section_connections.requirement,
                rhs_node=new_link,
            )
        elif self.graph_database.node_with_uid_exists(uid=new_link.link):
            anchor = assert_cast(
                self.graph_database.get_node_by_uid(new_link.link), Anchor
            )
            self.graph_database.add_link(
                link_type=GraphLinkType.SECTIONS_TO_INCOMING_LINKS,
                lhs_node=anchor,
                rhs_node=new_link,
            )
        else:
            raise NotImplementedError

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

    def remove_inline_link(self, inline_link: InlineLink) -> None:
        sections_with_incoming_links = (
            self.graph_database.get_link_values_reverse_weak(
                link_type=GraphLinkType.SECTIONS_TO_INCOMING_LINKS,
                rhs_node=inline_link,
            )
        )
        for section_with_incoming_links in sections_with_incoming_links:
            self.graph_database.remove_link(
                link_type=GraphLinkType.SECTIONS_TO_INCOMING_LINKS,
                lhs_node=section_with_incoming_links,
                rhs_node=inline_link,
                remove_lhs_node=False,
                remove_rhs_node=True,
            )

    def validate_node_against_anchors(
        self, *, node: Union[Document, Section, None], new_anchors: List[Anchor]
    ):
        assert node is None or isinstance(node, (Document, Section))
        assert isinstance(new_anchors, list)

        # Check that this node does not have duplicated anchors.
        new_anchor_uids = set()
        for anchor in new_anchors:
            if anchor.value in new_anchor_uids:
                raise SingleValidationError(
                    "A node cannot have two anchors with "
                    f"the same identifier: {anchor.value}."
                )
            new_anchor_uids.add(anchor.value)

        # If the node is new, the validation is easier: we just need to make
        # sure that there are no existing anchors with the UIDs brought
        # by the new anchors.
        if node is None:
            for anchor_uid in new_anchor_uids:
                if self.graph_database.node_with_uid_exists(uid=anchor_uid):
                    raise SingleValidationError(
                        "A node contains an anchor that already exists: "
                        f"{anchor_uid}."
                    )
            return

        # If the node is an existing node, we need to check that:
        # 1) If some of the new anchors already exist in the project tree, we
        #    need to ensure that they exist in the current node, otherwise we
        #    raise a duplication validation error.
        # 2) If the new anchors do not contain some of the existing node's
        #    current anchors, this means these anchors are being removed. In
        #    that case, we need to check if these anchors are used by any LINKs,
        #    raising a validation if they do.
        existing_node_anchor_uids = set()
        if len(node.free_texts) > 0:
            for part in node.free_texts[0].parts:
                if isinstance(part, Anchor):
                    existing_node_anchor_uids.add(part.value)

        # Validation 1: Assert all UIDs either:
        #               a) new
        #               b) exist in this node
        #               c) raise a duplication error.
        for anchor_uid in new_anchor_uids:
            if (
                self.graph_database.node_with_uid_exists(uid=anchor_uid)
                and anchor_uid not in existing_node_anchor_uids
            ):
                node_with_duplicate_anchor = (
                    self.find_node_with_duplicate_anchor(anchor_uid)
                )
                node_type = (
                    "Document"
                    if isinstance(node_with_duplicate_anchor, Document)
                    else "Section"
                )
                raise SingleValidationError(
                    "Another node contains an anchor with the same UID: "
                    f"{anchor_uid}. Node: {node_type} with title "
                    f"'{node_with_duplicate_anchor.title}'."
                )

        # Validation 2: Check that removed anchors do not have any incoming
        # links.
        to_be_removed_anchor_uids = existing_node_anchor_uids - new_anchor_uids
        document: Document
        for document in self.document_tree.document_list:
            document_iterator = DocumentCachingIterator(document)
            for node_ in document_iterator.all_content():
                if not isinstance(node_, (Document, Section)):
                    continue
                if len(node_.free_texts) > 0:
                    for part in node_.free_texts[0].parts:
                        if (
                            isinstance(part, InlineLink)
                            and part.link in to_be_removed_anchor_uids
                        ):
                            node_with_duplicate_anchor = (
                                self.find_node_with_duplicate_anchor(part.link)
                            )
                            node_type = (
                                "Document"
                                if isinstance(
                                    node_with_duplicate_anchor, Document
                                )
                                else "Section"
                            )

                            raise SingleValidationError(
                                f"Cannot remove anchor with UID "
                                f"'{part.link}' because it has incoming "
                                f"links. Containing node: "
                                f"{node_type} with title "
                                f"'{node_with_duplicate_anchor.title}'."
                            )

    def validate_section_can_remove_uid(self, *, section: Section):
        section_incoming_links: Optional[
            List[InlineLink]
        ] = self.get_section_incoming_links(section)
        if section_incoming_links is None or len(section_incoming_links) == 0:
            return

        unique_incoming_link_parent_nodes = []
        for section_incoming_link in section_incoming_links:
            unique_incoming_link_parent_nodes.append(
                section_incoming_link.parent.parent
            )
        incoming_link_parent_titles = map(
            lambda n: f"'{n.title}'", unique_incoming_link_parent_nodes
        )
        incoming_links_sources_string = ", ".join(incoming_link_parent_titles)
        raise SingleValidationError(
            f"Cannot remove a section UID "
            f"'{section.reserved_uid}' because there are "
            f"existing LINKs referencing this "
            "section. The incoming links are located in these "
            f"nodes: {incoming_links_sources_string}."
        )

    def validate_can_create_uid(self, uid: str):
        assert isinstance(uid, str), uid
        assert len(uid) > 0, uid

        existing_node_with_uid: Union[
            Document, Section, Requirement, None
        ] = self.find_node_by_uid_weak(uid)

        if existing_node_with_uid is None:
            return

        raise SingleValidationError(
            "UID uniqueness validation error: "
            "There is already an existing node "
            f"with this UID: {existing_node_with_uid.get_title()}."
        )

    def get_section_incoming_links(
        self, section: Section
    ) -> Optional[List[InlineLink]]:
        section_incoming_links = self.graph_database.get_link_values_weak(
            link_type=GraphLinkType.SECTIONS_TO_INCOMING_LINKS,
            lhs_node=section,
        )
        return section_incoming_links

    def update_with_anchor(self, anchor: Anchor):
        # By this time, we know that the validations have passed just before.
        existing_anchor: Optional[
            Anchor
        ] = self.graph_database.get_node_by_uid_weak(uid=anchor.value)
        if existing_anchor is not None:
            self.graph_database.remove_node_by_mid(existing_anchor.mid)

        self.graph_database.add_node_by_mid(
            mid=anchor.mid, uid=anchor.value, node=anchor
        )
