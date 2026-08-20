from typing import List, Union

from strictdoc.backend.sdoc.document_reference import DocumentReference
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.core.document_iterator import SDocDocumentIterator
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.core.transforms.constants import NodeCreationOrder
from strictdoc.core.transforms.validation_error import (
    SingleValidationError,
)
from strictdoc.helpers.cast import assert_cast


class MoveNodeAcrossDocumentsCommand:
    def __init__(
        self,
        moved_node: SDocNode,
        target_node: Union[SDocDocument, SDocNode],
        whereto: str,
        traceability_index: TraceabilityIndex,
    ):
        self.moved_node: SDocNode = moved_node
        self.target_node: Union[SDocDocument, SDocNode] = target_node
        self.whereto: str = whereto
        self.traceability_index: TraceabilityIndex = traceability_index

        # Populated by perform(). The router uses these to know which
        # document(s) to write to disk: this command only mutates the
        # in-memory model, it does not touch the file system.
        self.source_document: SDocDocument
        self.destination_document: SDocDocument
        self.move_was_performed: bool = False

    def validate(self) -> None:
        if not NodeCreationOrder.is_valid(self.whereto):
            raise SingleValidationError(
                f"Unsupported whereto value: {self.whereto}."
            )
        if not self.traceability_index.can_move_node_across_documents(
            self.moved_node
        ):
            raise SingleValidationError("Moving is disabled for this node.")
        if self.traceability_index.is_node_in_own_subtree(
            self.moved_node, self.target_node
        ):
            raise SingleValidationError(
                "Cannot move a node into itself or its own descendant."
            )
        if self.whereto == NodeCreationOrder.CHILD:
            if (
                isinstance(self.target_node, SDocNode)
                and not self.target_node.is_composite
            ):
                raise SingleValidationError(
                    "A non-composite node cannot contain child nodes."
                )
        elif isinstance(self.target_node, SDocDocument):
            raise SingleValidationError(
                "A document only supports moving a node inside it."
            )
        destination_document = self._get_destination_document()
        if not self.traceability_index.is_move_grammar_compatible(
            self.moved_node, destination_document
        ):
            raise SingleValidationError(
                "The destination document's grammar cannot represent "
                "the moved subtree without changes."
            )

    def perform(self) -> None:
        self.validate()

        source_document: SDocDocument = assert_cast(
            self.moved_node.get_document(), SDocDocument
        )
        destination_document = self._get_destination_document()
        self.source_document = source_document
        self.destination_document = destination_document

        if self._is_already_at_target_location():
            return

        subtree_nodes: List[SDocNode] = self._collect_subtree_nodes(
            self.moved_node
        )

        current_parent_node = self.moved_node.parent
        current_parent_node.section_contents.remove(self.moved_node)

        if self.whereto == NodeCreationOrder.CHILD:
            self.target_node.section_contents.append(self.moved_node)
            self.moved_node.parent = self.target_node
        else:
            assert isinstance(self.target_node, SDocNode)
            target_parent = self.target_node.parent
            insert_to_idx = target_parent.section_contents.index(
                self.target_node
            )
            if self.whereto == NodeCreationOrder.AFTER:
                insert_to_idx += 1
            target_parent.section_contents.insert(
                insert_to_idx, self.moved_node
            )
            self.moved_node.parent = target_parent

        if source_document is not destination_document:
            for subtree_node_ in subtree_nodes:
                # ng_document_reference is one DocumentReference instance
                # shared, by reference, across every node of a document
                # (assigned once at parse time, see
                # SDocParsingProcessor.process_requirement()). Calling
                # set_document() on it would repoint every other node of
                # the source document, not just the moved subtree. Give
                # the moved nodes their own reference instead of mutating
                # the shared one.
                new_document_reference = DocumentReference()
                new_document_reference.set_document(destination_document)
                subtree_node_.ng_document_reference = new_document_reference

                if (
                    subtree_node_.ng_including_document_reference is not None
                    and subtree_node_.ng_including_document_reference.get_document()
                    is not None
                ):
                    new_including_document_reference = DocumentReference()
                    new_including_document_reference.set_document(
                        destination_document
                    )
                    subtree_node_.ng_including_document_reference = (
                        new_including_document_reference
                    )

        self.traceability_index.update_last_updated()
        self.move_was_performed = True

    def _is_already_at_target_location(self) -> bool:
        current_parent = self.moved_node.parent
        if self.whereto == NodeCreationOrder.CHILD:
            return (
                current_parent is self.target_node
                and current_parent.section_contents[-1] is self.moved_node
            )

        assert isinstance(self.target_node, SDocNode)
        if current_parent is not self.target_node.parent:
            return False

        moved_node_index = current_parent.section_contents.index(
            self.moved_node
        )
        target_node_index = current_parent.section_contents.index(
            self.target_node
        )
        if self.whereto == NodeCreationOrder.BEFORE:
            return moved_node_index + 1 == target_node_index
        return target_node_index + 1 == moved_node_index

    def _collect_subtree_nodes(self, node: SDocNode) -> List[SDocNode]:
        document = assert_cast(node.get_document(), SDocDocument)
        document_iterator = SDocDocumentIterator(document=document)
        subtree_nodes: List[SDocNode] = []
        for document_node_, _ in document_iterator.all_node_content(
            node,
            print_fragments=True,
            update_levels=False,
        ):
            if not isinstance(document_node_, SDocNode):
                continue
            subtree_nodes.append(document_node_)
        return subtree_nodes

    def _get_destination_document(self) -> SDocDocument:
        if isinstance(self.target_node, SDocDocument):
            return self.target_node
        return assert_cast(self.target_node.get_document(), SDocDocument)
