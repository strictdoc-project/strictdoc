from typing import Union

from strictdoc.backend.sdoc.models.model import (
    SDocCompositeNodeIF,
    SDocDocumentIF,
    SDocSectionIF,
)
from strictdoc.backend.sdoc.models.node import SDocCompositeNode, SDocNode
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.core.transforms.validation_error import (
    MultipleValidationErrorAsList,
    SingleValidationError,
)


class DeleteRequirementCommand:
    def __init__(
        self,
        requirement: SDocNode,
        traceability_index: TraceabilityIndex,
    ):
        self.requirement: SDocNode = requirement
        self.traceability_index: TraceabilityIndex = traceability_index

    def validate(self) -> None:
        nodes_with_incoming_links = [
            self.requirement
        ] + self.requirement.get_anchors()
        for node_ in nodes_with_incoming_links:
            try:
                self.traceability_index.validate_node_can_remove_uid(node=node_)
            except SingleValidationError as exception_:
                raise MultipleValidationErrorAsList(
                    "NOT_RELEVANT",
                    errors=[
                        "This node cannot be removed because it contains incoming links."
                    ],
                ) from exception_

    def perform(self) -> None:
        self.validate()

        self.traceability_index.delete_requirement(self.requirement)

        requirement_parent: Union[
            SDocSectionIF, SDocDocumentIF, SDocCompositeNodeIF
        ] = self.requirement.parent

        if isinstance(requirement_parent, SDocCompositeNode):
            assert (
                requirement_parent.requirements is not None
                and len(requirement_parent.requirements) > 0
            ), requirement_parent.requirements
            requirement_parent.requirements.remove(self.requirement)
        else:
            requirement_parent.section_contents.remove(self.requirement)

        self.traceability_index.update_last_updated()
