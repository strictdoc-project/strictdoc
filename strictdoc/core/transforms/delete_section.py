# mypy: disable-error-code="no-untyped-call,no-untyped-def"
from typing import Union

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.section import SDocSection
from strictdoc.core.traceability_index import (
    TraceabilityIndex,
)
from strictdoc.core.transforms.validation_error import (
    MultipleValidationErrorAsList,
)
from strictdoc.helpers.cast import assert_cast


class DeleteSectionCommand:
    def __init__(
        self,
        section: SDocSection,
        traceability_index: TraceabilityIndex,
    ):
        self.section: SDocSection = section
        self.traceability_index: TraceabilityIndex = traceability_index

    def validate(self):
        incoming_links = self.traceability_index.get_incoming_links(
            self.section
        )
        if incoming_links is not None and len(incoming_links) > 0:
            raise MultipleValidationErrorAsList(
                "NOT_RELEVANT",
                errors=[
                    "This section cannot be removed because it contains incoming links."
                ],
            )

    def perform(self):
        self.validate()

        section: SDocSection = self.section
        section_parent: Union[SDocSection, SDocDocument] = assert_cast(
            section.parent, (SDocSection, SDocDocument)
        )
        section_parent.section_contents.remove(section)

        section.parent = None

        self.traceability_index.update_last_updated()
