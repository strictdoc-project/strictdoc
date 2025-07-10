"""
@relation(SDOC-SRS-28, scope=file)
"""

# mypy: disable-error-code="attr-defined,no-untyped-call,no-untyped-def,union-attr"
import datetime
from copy import deepcopy
from typing import Any, Dict, Generator, List, Optional, Tuple, Union

from strictdoc.backend.sdoc.document_reference import DocumentReference
from strictdoc.backend.sdoc.models.anchor import Anchor
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_config import DocumentConfig
from strictdoc.backend.sdoc.models.inline_link import InlineLink
from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.backend.sdoc.models.section import SDocSection
from strictdoc.backend.sdoc_source_code.reader import (
    SourceFileTraceabilityInfo,
)
from strictdoc.core.asset_manager import AssetManager
from strictdoc.core.constants import GraphLinkType
from strictdoc.core.document_iterator import DocumentCachingIterator
from strictdoc.core.document_meta import DocumentMeta
from strictdoc.core.document_tree import DocumentTree
from strictdoc.core.file_dependency_manager import FileDependencyManager
from strictdoc.core.file_traceability_index import FileTraceabilityIndex
from strictdoc.core.graph.abstract_bucket import ALL_EDGES
from strictdoc.core.graph_database import GraphDatabase
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.source_tree import SourceFile
from strictdoc.core.transforms.validation_error import (
    SingleValidationError,
)
from strictdoc.core.tree_cycle_detector import TreeCycleDetector
from strictdoc.helpers.cast import assert_cast, assert_optional_cast
from strictdoc.helpers.file_modification_time import set_file_modification_time
from strictdoc.helpers.mid import MID
from strictdoc.helpers.ordered_set import OrderedSet
from strictdoc.helpers.paths import SDocRelativePath
from strictdoc.helpers.sorting import alphanumeric_sort


class TraceabilityIndex:
    def __init__(
        self,
        document_iterators: Dict[SDocDocument, DocumentCachingIterator],
        file_traceability_index: FileTraceabilityIndex,
        graph_database: GraphDatabase,
        file_dependency_manager: FileDependencyManager,
    ):
        self._document_iterators: Dict[
            SDocDocument, DocumentCachingIterator
        ] = document_iterators
        self._file_traceability_index: FileTraceabilityIndex = (
            file_traceability_index
        )

        self.graph_database: GraphDatabase = graph_database
        self.document_tree: Optional[DocumentTree] = None
        self.asset_manager: Optional[AssetManager] = None
        self.file_dependency_manager: FileDependencyManager = (
            file_dependency_manager
        )
        self.index_last_updated = datetime.datetime.today()
        self.contains_included_documents = False
        self.strictdoc_last_update: datetime.datetime = (
            datetime.datetime.fromtimestamp(0)
        )

    @property
    def document_iterators(self) -> Dict[SDocDocument, DocumentCachingIterator]:
        return self._document_iterators

    def is_small_project(self) -> bool:
        """
        Check if project is small to control feature availability.

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
        return (
            self.graph_database.get_count(
                link_type=GraphLinkType.NODE_TO_PARENT_NODES
            )
            <= 10
        )

    def has_parent_requirements(self, requirement: SDocNode) -> bool:
        assert isinstance(requirement, SDocNode)
        if not isinstance(requirement.reserved_uid, str):
            return False

        parent_requirements = self.graph_database.get_link_values(
            link_type=GraphLinkType.NODE_TO_PARENT_NODES,
            lhs_node=requirement,
            edge=ALL_EDGES,
        )
        return len(parent_requirements) > 0

    def has_children_requirements(self, requirement: SDocNode) -> bool:
        assert isinstance(requirement, SDocNode)
        if not isinstance(requirement.reserved_uid, str):
            return False

        children_requirements = self.graph_database.get_link_values(
            link_type=GraphLinkType.NODE_TO_CHILD_NODES,
            lhs_node=requirement,
            edge=ALL_EDGES,
        )
        return len(children_requirements) > 0

    def has_source_file_reqs(self, source_file_rel_path):
        return self._file_traceability_index.has_source_file_reqs(
            source_file_rel_path
        )

    def has_node_connections(self, node_uid: str) -> bool:
        assert isinstance(node_uid, str), node_uid
        return self.graph_database.has_link(
            link_type=GraphLinkType.UID_TO_NODE,
            lhs_node=node_uid,
        )

    def get_node_by_mid(self, node_mid: MID) -> Any:
        assert isinstance(node_mid, MID), node_mid
        return self.graph_database.get_link_value(
            link_type=GraphLinkType.MID_TO_NODE, lhs_node=node_mid
        )

    def get_node_by_mid_weak(self, node_mid: MID) -> Optional[Any]:
        assert isinstance(node_mid, MID), node_mid
        return self.graph_database.get_link_value_weak(
            link_type=GraphLinkType.MID_TO_NODE, lhs_node=node_mid
        )

    def get_file_traceability_index(self) -> FileTraceabilityIndex:
        return self._file_traceability_index

    def get_document_iterator(self, document) -> DocumentCachingIterator:
        return self.document_iterators[document]

    def get_parent_requirements(self, requirement: SDocNode) -> List[SDocNode]:
        assert isinstance(requirement, SDocNode)
        if not isinstance(requirement.reserved_uid, str):
            return []

        return list(
            self.graph_database.get_link_values(
                link_type=GraphLinkType.NODE_TO_PARENT_NODES,
                lhs_node=requirement,
                edge=ALL_EDGES,
            )
        )

    def get_parent_relations_with_roles(self, requirement: SDocNode):
        assert isinstance(requirement, SDocNode)
        if requirement.reserved_uid is None:
            return

        return list(
            self.graph_database.get_link_values_with_edges(
                link_type=GraphLinkType.NODE_TO_PARENT_NODES,
                lhs_node=requirement,
                edge=ALL_EDGES,
            )
        )

    def get_parent_relations_with_role(
        self, requirement: SDocNode, role: Optional[str]
    ) -> List[Any]:  # FIXME: Make Any->SDocNode.
        assert isinstance(requirement, SDocNode)
        if requirement.reserved_uid is None:
            return []

        return list(
            self.graph_database.get_link_values_with_edges(
                link_type=GraphLinkType.NODE_TO_PARENT_NODES,
                lhs_node=requirement,
                edge=role,
            )
        )

    def get_child_relations_with_roles(
        self, requirement: SDocNode
    ) -> List[Any]:  # FIXME: Make Any->SDocNode.
        assert isinstance(requirement, SDocNode)
        if requirement.reserved_uid is None:
            return []

        return list(
            self.graph_database.get_link_values_with_edges(
                link_type=GraphLinkType.NODE_TO_CHILD_NODES,
                lhs_node=requirement,
                edge=ALL_EDGES,
            )
        )

    def get_child_relations_with_role(
        self, requirement: SDocNode, role: Optional[str]
    ) -> List[Any]:  # FIXME: Make Any->SDocNode
        assert isinstance(requirement, SDocNode)
        if requirement.reserved_uid is None:
            return []

        return list(
            self.graph_database.get_link_values_with_edges(
                link_type=GraphLinkType.NODE_TO_CHILD_NODES,
                lhs_node=requirement,
                edge=role,
            )
        )

    def get_children_requirements(
        self, requirement: SDocNode
    ) -> List[SDocNode]:
        assert isinstance(requirement, SDocNode)
        if not isinstance(requirement.reserved_uid, str):
            return []

        return list(
            self.graph_database.get_link_values(
                link_type=GraphLinkType.NODE_TO_CHILD_NODES,
                lhs_node=requirement,
                edge=ALL_EDGES,
            )
        )

    def has_tags(self, document: SDocDocument) -> bool:
        return self.graph_database.has_link(
            link_type=GraphLinkType.DOCUMENT_TO_TAGS,
            lhs_node=document.reserved_mid,
        )

    def get_counted_tags(
        self, document: SDocDocument
    ) -> Generator[Tuple[str, int], None, None]:
        document_tags_or_none = self.graph_database.get_link_value(
            link_type=GraphLinkType.DOCUMENT_TO_TAGS,
            lhs_node=document.reserved_mid,
        )
        document_tags: Dict[str, int] = assert_cast(document_tags_or_none, dict)

        tags = sorted(document_tags.keys(), key=alphanumeric_sort)
        for tag in tags:
            yield tag, document_tags[tag]

    def get_requirement_file_links(self, requirement):
        return self._file_traceability_index.get_requirement_file_links(
            requirement
        )

    def get_source_file_reqs(
        self, source_file_rel_path
    ) -> Optional[List[SDocNode]]:
        return self._file_traceability_index.get_source_file_reqs(
            source_file_rel_path
        )

    def get_coverage_info(
        self, source_file_rel_path: str
    ) -> SourceFileTraceabilityInfo:
        return self._file_traceability_index.get_coverage_info(
            source_file_rel_path
        )

    def get_coverage_info_weak(
        self, source_file_rel_path: str
    ) -> Optional[SourceFileTraceabilityInfo]:
        return self._file_traceability_index.get_coverage_info_weak(
            source_file_rel_path
        )

    def get_node_by_uid(self, uid: str):
        assert isinstance(uid, str) and len(uid) > 0, uid
        return self.graph_database.get_link_value(
            link_type=GraphLinkType.UID_TO_NODE, lhs_node=uid
        )

    def get_node_by_uid_weak2(self, uid: str):
        """
        FIXME: This can likely replace _weak below with no problem.
        """
        assert isinstance(uid, str) and len(uid) > 0, uid
        return self.graph_database.get_link_value_weak(
            link_type=GraphLinkType.UID_TO_NODE, lhs_node=uid
        )

    def get_linkable_node_by_uid(
        self, uid
    ) -> Union[SDocDocument, SDocNode, SDocSection, Anchor]:
        return assert_cast(
            self.get_node_by_uid(uid),
            (SDocDocument, SDocNode, SDocSection, Anchor),
        )

    def get_node_by_uid_weak(
        self, uid: str
    ) -> Union[SDocDocument, SDocSection, SDocNode, None]:
        assert isinstance(uid, str), uid
        for document in self.document_tree.document_list:
            document_iterator = DocumentCachingIterator(document)
            for node, _ in document_iterator.all_content(print_fragments=False):
                if isinstance(node, SDocDocument):
                    if node.config.uid == uid:
                        return node
                elif isinstance(node, SDocSection):
                    if node.reserved_uid == uid:
                        return node
                elif isinstance(node, SDocNode):
                    if node.reserved_uid == uid:
                        return node
                else:
                    raise NotImplementedError
        return None

    def get_linkable_node_by_uid_weak(
        self, uid
    ) -> Union[SDocDocument, SDocNode, SDocSection, Anchor, None]:
        return assert_optional_cast(
            self.graph_database.get_link_value_weak(
                link_type=GraphLinkType.UID_TO_NODE, lhs_node=uid
            ),
            (SDocDocument, SDocNode, SDocSection, Anchor),
        )

    def get_incoming_links(
        self, node: Union[SDocDocument, SDocNode, SDocSection, Anchor]
    ) -> Optional[List[InlineLink]]:
        incoming_links = self.graph_database.get_link_values(
            link_type=GraphLinkType.NODE_TO_INCOMING_LINKS,
            lhs_node=node.reserved_mid,
        )
        if incoming_links is None or len(incoming_links) == 0:
            return None
        # FIXME: Should the graph database return OrderedSet or a copied list()?
        return list(incoming_links)

    def create_traceability_info(
        self,
        source_file: SourceFile,
        traceability_info: SourceFileTraceabilityInfo,
    ):
        self._file_traceability_index.create_traceability_info(
            source_file, traceability_info
        )

    def create_document(self, document: SDocDocument) -> None:
        assert isinstance(document, SDocDocument)
        if document.reserved_uid is not None:
            self.graph_database.create_link(
                link_type=GraphLinkType.UID_TO_NODE,
                lhs_node=document.reserved_uid,
                rhs_node=document,
            )
        self.graph_database.create_link(
            link_type=GraphLinkType.MID_TO_NODE,
            lhs_node=document.reserved_mid,
            rhs_node=document,
        )

    def create_section(self, section: SDocSection) -> None:
        assert isinstance(section, SDocSection)
        if section.reserved_uid is not None:
            self.graph_database.create_link(
                link_type=GraphLinkType.UID_TO_NODE,
                lhs_node=section.reserved_uid,
                rhs_node=section,
            )
        self.graph_database.create_link(
            link_type=GraphLinkType.MID_TO_NODE,
            lhs_node=section.reserved_mid,
            rhs_node=section,
        )

    def create_inline_link(self, new_link: InlineLink):
        assert isinstance(new_link, InlineLink)

        # InlineLink points to a section, node or to anchor.
        assert self.graph_database.has_link(
            link_type=GraphLinkType.UID_TO_NODE, lhs_node=new_link.link
        )

        node_or_anchor: Union[SDocDocument, SDocNode, SDocSection, Anchor] = (
            assert_cast(
                self.graph_database.get_link_value(
                    link_type=GraphLinkType.UID_TO_NODE,
                    lhs_node=new_link.link,
                ),
                (SDocDocument, SDocNode, SDocSection, Anchor),
            )
        )
        self.graph_database.create_link(
            link_type=GraphLinkType.NODE_TO_INCOMING_LINKS,
            lhs_node=node_or_anchor.reserved_mid,
            rhs_node=new_link,
        )
        self.graph_database.create_link(
            link_type=GraphLinkType.MID_TO_NODE,
            lhs_node=new_link.reserved_mid,
            rhs_node=new_link,
        )

    def update_last_updated(self) -> None:
        """
        Update the index's last updated date to the current time.

        This is a rather broad way of signalling that all documents of the index
        need to be re-generated when they are opened next time. Several UI
        actions use this method to ensure a complete re-generation of all
        documents.
        """
        self.index_last_updated = datetime.datetime.today()

    def create_requirement(self, requirement: SDocNode):
        assert isinstance(requirement, SDocNode), requirement

        self.graph_database.create_link(
            link_type=GraphLinkType.MID_TO_NODE,
            lhs_node=requirement.reserved_mid,
            rhs_node=requirement,
        )
        if requirement.reserved_uid is not None:
            self.graph_database.create_link(
                link_type=GraphLinkType.UID_TO_NODE,
                lhs_node=requirement.reserved_uid,
                rhs_node=requirement,
            )

    def update_requirement_uid(
        self, requirement: SDocNode, old_uid: Optional[str]
    ) -> None:
        if old_uid is None:
            if requirement.reserved_uid:
                self.graph_database.create_link(
                    link_type=GraphLinkType.UID_TO_NODE,
                    lhs_node=requirement.reserved_uid,
                    rhs_node=requirement,
                )
            return

        self.graph_database.delete_link(
            link_type=GraphLinkType.UID_TO_NODE,
            lhs_node=old_uid,
            rhs_node=requirement,
        )

        if requirement.reserved_uid is not None:
            self.graph_database.create_link(
                link_type=GraphLinkType.UID_TO_NODE,
                lhs_node=requirement.reserved_uid,
                rhs_node=requirement,
            )

    def update_requirement_parent_uid(
        self, requirement: SDocNode, parent_uid: str, role: Optional[str]
    ) -> None:
        assert requirement.reserved_uid is not None
        assert isinstance(parent_uid, str), parent_uid
        assert role is None or len(role) > 0, role
        parent_nodes: OrderedSet[SDocNode] = (
            self.graph_database.get_link_values(
                link_type=GraphLinkType.NODE_TO_PARENT_NODES,
                lhs_node=requirement,
                edge=role,
            )
        )
        # If a relation to the parent uid through a given role already exists,
        # there is nothing to do.
        if any(node_.reserved_uid == parent_uid for node_ in parent_nodes):
            return

        parent_requirement: SDocNode = self.graph_database.get_link_value(
            link_type=GraphLinkType.UID_TO_NODE,
            lhs_node=parent_uid,
        )

        document = assert_cast(requirement.get_document(), SDocDocument)
        parent_requirement_document = assert_cast(
            parent_requirement.get_document(), SDocDocument
        )

        self.graph_database.create_link(
            link_type=GraphLinkType.NODE_TO_PARENT_NODES,
            lhs_node=requirement,
            rhs_node=parent_requirement,
            edge=role,
        )
        self.graph_database.create_link(
            link_type=GraphLinkType.NODE_TO_CHILD_NODES,
            lhs_node=parent_requirement,
            rhs_node=requirement,
            edge=role,
        )

        cycle_detector = TreeCycleDetector()

        def parent_cycle_traverse_(node_id):
            node = self.graph_database.get_link_value(
                link_type=GraphLinkType.UID_TO_NODE,
                lhs_node=node_id,
            )
            return list(
                map(
                    lambda node_: node_.reserved_uid,
                    self.graph_database.get_link_values(
                        link_type=GraphLinkType.NODE_TO_PARENT_NODES,
                        lhs_node=node,
                    ),
                )
            )

        cycle_detector.check_node(
            requirement.reserved_uid,
            parent_cycle_traverse_,
        )

        # Mark document and parent document (if different) for re-generation.
        set_file_modification_time(
            document.meta.input_doc_full_path, datetime.datetime.today()
        )
        if parent_requirement_document != document:
            set_file_modification_time(
                parent_requirement_document.meta.input_doc_full_path,
                datetime.datetime.today(),
            )

    def update_requirement_child_uid(
        self, requirement: SDocNode, child_uid: str, role: Optional[str]
    ) -> None:
        assert requirement.reserved_uid is not None
        assert isinstance(child_uid, str), child_uid
        assert role is None or len(role) > 0, role
        child_nodes: OrderedSet[SDocNode] = self.graph_database.get_link_values(
            link_type=GraphLinkType.NODE_TO_CHILD_NODES,
            lhs_node=requirement,
            edge=role,
        )

        # If a relation to the parent uid through a given role already exists,
        # there is nothing to do.
        if any(node_.reserved_uid == child_uid for node_ in child_nodes):
            return
        child_requirement = self.graph_database.get_link_value(
            link_type=GraphLinkType.UID_TO_NODE,
            lhs_node=child_uid,
        )

        document = assert_cast(requirement.get_document(), SDocDocument)
        child_requirement_document = assert_cast(
            child_requirement.get_document(), SDocDocument
        )

        self.graph_database.create_link(
            link_type=GraphLinkType.NODE_TO_PARENT_NODES,
            lhs_node=child_requirement,
            rhs_node=requirement,
            edge=role,
        )
        self.graph_database.create_link(
            link_type=GraphLinkType.NODE_TO_CHILD_NODES,
            lhs_node=requirement,
            rhs_node=child_requirement,
            edge=role,
        )

        cycle_detector = TreeCycleDetector()

        def child_cycle_traverse_(node_id):
            node = self.graph_database.get_link_value(
                link_type=GraphLinkType.UID_TO_NODE,
                lhs_node=node_id,
            )
            return list(
                map(
                    lambda node_: node_.reserved_uid,
                    self.graph_database.get_link_values(
                        link_type=GraphLinkType.NODE_TO_CHILD_NODES,
                        lhs_node=node,
                    ),
                )
            )

        cycle_detector.check_node(
            requirement.reserved_uid,
            child_cycle_traverse_,
        )

        # Mark document and parent document (if different) for re-generation.
        set_file_modification_time(
            document.meta.input_doc_full_path, datetime.datetime.today()
        )
        if child_requirement_document != document:
            set_file_modification_time(
                child_requirement_document.meta.input_doc_full_path,
                datetime.datetime.today(),
            )

    def update_with_anchor(self, anchor: Anchor):
        # By this time, we know that the validations have passed just before.
        existing_anchor: Optional[Anchor] = (
            self.graph_database.get_link_value_weak(
                link_type=GraphLinkType.UID_TO_NODE,
                lhs_node=anchor.value,
            )
        )
        if existing_anchor is not None:
            self.graph_database.delete_link(
                link_type=GraphLinkType.MID_TO_NODE,
                lhs_node=existing_anchor.mid,
                rhs_node=existing_anchor,
            )
            self.graph_database.delete_link(
                link_type=GraphLinkType.UID_TO_NODE,
                lhs_node=existing_anchor.value,
                rhs_node=existing_anchor,
            )

        self.graph_database.create_link(
            link_type=GraphLinkType.MID_TO_NODE,
            lhs_node=anchor.mid,
            rhs_node=anchor,
        )
        self.graph_database.create_link(
            link_type=GraphLinkType.UID_TO_NODE,
            lhs_node=anchor.value,
            rhs_node=anchor,
        )

    def update_disconnect_two_documents_if_no_links_left(
        self, document: SDocDocument, other_document: SDocDocument
    ):
        assert document != other_document

        for node, _ in self.document_iterators[document].all_content(
            print_fragments=False
        ):
            if not isinstance(node, SDocNode):
                continue

            requirement_node: SDocNode = node

            # If a requirement has no UID, it cannot contribute to any relation-based
            # connection between any two documents.
            if requirement_node.reserved_uid is None:
                continue

            requirement_parents: OrderedSet[SDocNode] = (
                self.graph_database.get_link_values(
                    link_type=GraphLinkType.NODE_TO_PARENT_NODES,
                    lhs_node=requirement_node,
                )
            )

            # If at least one parent or child relation points to the other
            # document, terminate, not deleting the link between documents.
            for parent_requirement in requirement_parents:
                parent_requirement_document: SDocDocument = assert_cast(
                    parent_requirement.get_document(), SDocDocument
                )
                if parent_requirement_document == other_document:
                    return

            requirement_children = self.graph_database.get_link_values(
                link_type=GraphLinkType.NODE_TO_CHILD_NODES,
                lhs_node=requirement_node,
            )

            for child_requirement_, _ in requirement_children:
                if child_requirement_.document == other_document:
                    return

    def delete_document(self, document: SDocDocument) -> None:
        assert isinstance(document, SDocDocument), document

        self.graph_database.delete_link(
            link_type=GraphLinkType.MID_TO_NODE,
            lhs_node=document.reserved_mid,
            rhs_node=document,
        )
        if document.reserved_uid is not None:
            self.graph_database.delete_link(
                link_type=GraphLinkType.UID_TO_NODE,
                lhs_node=document.reserved_uid,
                rhs_node=document,
            )

    def delete_section(self, section: SDocSection) -> None:
        assert isinstance(section, SDocSection), section

        self.graph_database.delete_link(
            link_type=GraphLinkType.MID_TO_NODE,
            lhs_node=section.reserved_mid,
            rhs_node=section,
        )
        if section.reserved_uid is not None:
            self.graph_database.delete_link(
                link_type=GraphLinkType.UID_TO_NODE,
                lhs_node=section.reserved_uid,
                rhs_node=section,
            )

    def delete_requirement(self, requirement: SDocNode) -> None:
        assert isinstance(requirement, SDocNode), SDocNode

        self.graph_database.delete_link(
            link_type=GraphLinkType.MID_TO_NODE,
            lhs_node=requirement.reserved_mid,
            rhs_node=requirement,
        )
        if requirement.reserved_uid is not None:
            self.graph_database.delete_link(
                link_type=GraphLinkType.UID_TO_NODE,
                lhs_node=requirement.reserved_uid,
                rhs_node=requirement,
            )
            self.graph_database.delete_all_links(
                link_type=GraphLinkType.NODE_TO_PARENT_NODES,
                lhs_node=requirement,
            )
            self.graph_database.delete_all_links(
                link_type=GraphLinkType.NODE_TO_CHILD_NODES,
                lhs_node=requirement,
            )

    def remove_requirement_parent_uid(
        self, requirement: SDocNode, parent_uid: str, role: Optional[str]
    ) -> None:
        assert requirement.reserved_uid is not None
        assert isinstance(parent_uid, str), parent_uid
        assert role is None or len(role) > 0, role

        parent_requirement: SDocNode = self.graph_database.get_link_value(
            link_type=GraphLinkType.UID_TO_NODE,
            lhs_node=parent_uid,
        )

        self.graph_database.delete_link(
            link_type=GraphLinkType.NODE_TO_PARENT_NODES,
            lhs_node=requirement,
            rhs_node=parent_requirement,
            edge=role,
        )
        self.graph_database.delete_link(
            link_type=GraphLinkType.NODE_TO_CHILD_NODES,
            lhs_node=parent_requirement,
            rhs_node=requirement,
            edge=role,
        )

        document = assert_cast(requirement.get_document(), SDocDocument)
        parent_requirement_document = assert_cast(
            parent_requirement.get_document(), SDocDocument
        )

        # If there are no requirements linking between the documents,
        # remove the link.
        if document != parent_requirement_document:
            self.update_disconnect_two_documents_if_no_links_left(
                document, parent_requirement_document
            )

        # Mark document and parent document (if different) for re-generation.
        set_file_modification_time(
            document.meta.input_doc_full_path, datetime.datetime.today()
        )
        if parent_requirement_document != document:
            set_file_modification_time(
                parent_requirement_document.meta.input_doc_full_path,
                datetime.datetime.today(),
            )

    def remove_requirement_child_uid(
        self, requirement: SDocNode, child_uid: str, role: Optional[str]
    ) -> None:
        assert requirement.reserved_uid is not None
        assert isinstance(child_uid, str), child_uid
        assert role is None or len(role) > 0, role

        child_requirement: SDocNode = self.graph_database.get_link_value(
            link_type=GraphLinkType.UID_TO_NODE,
            lhs_node=child_uid,
        )
        document: SDocDocument = assert_cast(
            requirement.get_document(), SDocDocument
        )
        child_requirement_document: SDocDocument = assert_cast(
            child_requirement.get_document(), SDocDocument
        )

        self.graph_database.delete_link(
            link_type=GraphLinkType.NODE_TO_CHILD_NODES,
            lhs_node=requirement,
            rhs_node=child_requirement,
            edge=role,
        )
        self.graph_database.delete_link(
            link_type=GraphLinkType.NODE_TO_PARENT_NODES,
            lhs_node=child_requirement,
            rhs_node=requirement,
            edge=role,
        )

        # If there are no requirements linking between the documents,
        # remove the link.
        if document != child_requirement_document:
            self.update_disconnect_two_documents_if_no_links_left(
                document, child_requirement_document
            )

        # Mark document and parent document (if different) for re-generation.
        set_file_modification_time(
            document.meta.input_doc_full_path, datetime.datetime.today()
        )
        if child_requirement_document != document:
            set_file_modification_time(
                child_requirement_document.meta.input_doc_full_path,
                datetime.datetime.today(),
            )

    def remove_inline_link(self, inline_link: InlineLink) -> None:
        sections_with_incoming_links = (
            self.graph_database.get_link_values_reverse(
                link_type=GraphLinkType.NODE_TO_INCOMING_LINKS,
                rhs_node=inline_link,
            )
        )

        for node_with_incoming_links in list(sections_with_incoming_links):
            self.graph_database.delete_link(
                link_type=GraphLinkType.NODE_TO_INCOMING_LINKS,
                lhs_node=node_with_incoming_links,
                rhs_node=inline_link,
            )

        self.graph_database.delete_link(
            link_type=GraphLinkType.MID_TO_NODE,
            lhs_node=inline_link.reserved_mid,
            rhs_node=inline_link,
        )

    def remove_anchor_by_uid(self, anchor_uid: str):
        anchor: Anchor = self.graph_database.get_link_value(
            link_type=GraphLinkType.UID_TO_NODE,
            lhs_node=anchor_uid,
        )
        self.graph_database.delete_link(
            link_type=GraphLinkType.MID_TO_NODE,
            lhs_node=anchor.mid,
            rhs_node=anchor,
        )
        self.graph_database.delete_link(
            link_type=GraphLinkType.UID_TO_NODE,
            lhs_node=anchor_uid,
            rhs_node=anchor,
        )

    def validate_node_against_anchors(
        self,
        *,
        node: Union[SDocDocument, SDocSection, SDocNode, None],
        new_anchors: List[Anchor],
    ) -> None:
        assert node is None or isinstance(
            node, (SDocDocument, SDocSection, SDocNode)
        )
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
                if self.graph_database.has_link(
                    link_type=GraphLinkType.UID_TO_NODE, lhs_node=anchor_uid
                ):
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

        # FIXME: No test reaches this for Section or Document.
        assert isinstance(node, SDocNode)
        for node_anchor_ in node.get_anchors():
            existing_node_anchor_uids.add(node_anchor_.value)

        #
        # Validation 1: Assert all UIDs are either:
        # a) new
        # b) exist in this node
        # c) raise a duplication error.
        #
        for anchor_uid in new_anchor_uids:
            if (
                self.graph_database.has_link(
                    link_type=GraphLinkType.UID_TO_NODE, lhs_node=anchor_uid
                )
                and anchor_uid not in existing_node_anchor_uids
            ):
                duplicate_anchor: Anchor = self.graph_database.get_link_value(
                    link_type=GraphLinkType.UID_TO_NODE, lhs_node=anchor_uid
                )
                node_with_duplicate_anchor: SDocNode = assert_cast(
                    duplicate_anchor.parent_node(), SDocNode
                )
                raise SingleValidationError(
                    "Another node contains an anchor with the same UID: "
                    f"{anchor_uid}. {node_with_duplicate_anchor.get_display_node_type()}: "
                    f"{node_with_duplicate_anchor.get_display_title()}."
                )

        #
        # Validation 2: Check that removed anchors do not have any incoming
        # links.
        #
        to_be_removed_anchor_uids = existing_node_anchor_uids - new_anchor_uids
        for to_be_removed_anchor_uid_ in to_be_removed_anchor_uids:
            to_be_removed_anchor: Anchor = self.graph_database.get_link_value(
                link_type=GraphLinkType.UID_TO_NODE,
                lhs_node=to_be_removed_anchor_uid_,
            )
            incoming_links = self.graph_database.get_link_values(
                link_type=GraphLinkType.NODE_TO_INCOMING_LINKS,
                lhs_node=to_be_removed_anchor.reserved_mid,
            )
            if incoming_links is not None and len(incoming_links) > 0:
                incoming_link: InlineLink = incoming_links[0]
                incoming_link_parent_node = incoming_link.parent_node()
                raise SingleValidationError(
                    f"Cannot remove anchor with UID "
                    f"'{incoming_link.link}' because it has incoming "
                    f"links. Containing node: "
                    f"{incoming_link_parent_node.get_display_node_type()}: "
                    f"'{incoming_link_parent_node.get_display_title()}'."
                )

    def validate_can_remove_node(
        self, *, node: Union[SDocNode, Anchor]
    ) -> None:
        incoming_links: Optional[List[InlineLink]] = self.get_incoming_links(
            node
        )
        if incoming_links is not None and len(incoming_links) > 0:
            link_list_message = ", ".join(
                map(
                    lambda l_: f"'{l_.parent_node().get_display_title()}' -> '{l_.link}'",
                    incoming_links,
                )
            )
            raise SingleValidationError(
                f"Cannot remove node '{node.get_display_title()}' with incoming LINKs from: {link_list_message}."
            )
        if isinstance(node, SDocNode):
            child_nodes: List[SDocNode] = self.get_children_requirements(node)
            if child_nodes is not None and len(child_nodes) > 0:
                nodes_list_message = ", ".join(
                    map(
                        lambda n_: "'" + n_.get_display_title() + "'",
                        child_nodes,
                    )
                )
                raise SingleValidationError(
                    f"Cannot remove node '{node.get_display_title()}' "
                    f"with incoming relations from:\n{nodes_list_message}."
                )

    def validate_section_can_remove_uid(self, *, section: SDocSection):
        section_incoming_links: Optional[List[InlineLink]] = (
            self.get_incoming_links(section)
        )
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

    def validate_can_create_uid(
        self, uid: str, existing_node_mid: Optional[MID]
    ):
        assert isinstance(uid, str), uid
        assert len(uid) > 0, uid

        existing_node_with_uid: Union[
            SDocDocument, SDocSection, SDocNode, None
        ] = self.get_node_by_uid_weak(uid)

        if existing_node_with_uid is None:
            return

        if existing_node_mid is not None:
            if existing_node_with_uid.reserved_mid == existing_node_mid:
                return

        raise SingleValidationError(
            "UID uniqueness validation error: "
            "There is already an existing node "
            f"with this UID: {existing_node_with_uid.get_display_title()}."
        )

    def clone_to_bundle_document(
        self, project_config: ProjectConfig
    ) -> Tuple["TraceabilityIndex", SDocDocument]:
        """
        Clone this traceability index and create a new bundle document.

        The only use case for this method is the generation of a bundle document.
        Since the bundle document does not exist on file system, some parameters
        are set artificially:
        - The bundle is assumed to be an input file in the root input folder.
        - The bundle is generated to the root of the output folder (level=0).
        - Some variables do not contribute (yet) to the final result, so they
          are marked as NOT_RELEVANT.
        """
        traceability_index_copy = deepcopy(self)
        bundle_document = SDocDocument(
            mid=None,
            title=project_config.project_title,
            config=None,
            view=None,
            grammar=None,
            section_contents=[],
            is_bundle_document=True,
        )
        bundle_document.config = DocumentConfig.default_config(bundle_document)

        if (
            project_config.bundle_document_version is not None
            and len(project_config.bundle_document_version) > 0
        ):
            bundle_document.config.version = (
                project_config.bundle_document_version
            )

        if (
            project_config.bundle_document_date is not None
            and len(project_config.bundle_document_date) > 0
        ):
            bundle_document.config.date = project_config.bundle_document_date

        bundle_document.meta = DocumentMeta(
            level=0,
            file_tree_mount_folder="NOT_RELEVANT",
            document_filename="bundle.sdoc",
            document_filename_base="bundle",
            input_doc_full_path="NOT_RELEVANT",
            input_doc_rel_path=SDocRelativePath("bundle.sdoc"),
            input_doc_dir_rel_path=SDocRelativePath(""),
            input_doc_assets_dir_rel_path=SDocRelativePath("NOT_RELEVANT"),
            output_document_dir_full_path=project_config.export_output_html_root,
            output_document_dir_rel_path=SDocRelativePath(""),
        )
        traceability_index_copy.document_iterators[bundle_document] = (
            DocumentCachingIterator(bundle_document)
        )
        for document_ in traceability_index_copy.document_tree.document_list:
            # Ignore all included documents. They are anyway included by
            # the including documents.
            if document_.document_is_included():
                continue

            document_.ng_including_document_reference.set_document(
                bundle_document
            )
            bundle_document.section_contents.append(document_)
        traceability_index_copy.document_tree.document_list = [bundle_document]
        bundle_document.ng_including_document_reference = DocumentReference()
        return traceability_index_copy, bundle_document
