from typing import List, Union

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.model import (
    SDocDocumentIF,
    SDocNodeIF,
    SDocSectionIF,
)
from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.core.document_iterator import DocumentCachingIterator
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.core.transforms.validation_error import (
    MultipleValidationErrorAsList,
    SingleValidationError,
)
from strictdoc.helpers.cast import assert_cast


class DeleteRequirementCommand:
    def __init__(
        self,
        requirement: SDocNode,
        traceability_index: TraceabilityIndex,
    ):
        self.requirement: SDocNode = requirement
        self.traceability_index: TraceabilityIndex = traceability_index

    def validate(self) -> None:
        errors: List[str] = []
        document: SDocDocument = assert_cast(
            self.requirement.get_document(), SDocDocument
        )
        document_iterator = DocumentCachingIterator(document=document)
        for document_node_, _ in document_iterator.all_node_content(
            self.requirement,
            print_fragments=True,
        ):
            if not isinstance(document_node_, SDocNode):
                continue
            nodes_with_incoming_links = [
                document_node_
            ] + document_node_.get_anchors()
            for node_ in nodes_with_incoming_links:
                try:
                    self.traceability_index.validate_can_remove_node(node=node_)
                except SingleValidationError as exception_:
                    errors.append(exception_.args[0])
        if len(errors) > 0:
            raise MultipleValidationErrorAsList("NOT_RELEVANT", errors)

    def perform(self) -> None:
        self.validate()

        self.traceability_index.delete_requirement(self.requirement)

        requirement_parent: Union[SDocSectionIF, SDocDocumentIF, SDocNodeIF] = (
            self.requirement.parent
        )

        requirement_parent.section_contents.remove(self.requirement)

        self.traceability_index.update_last_updated()
