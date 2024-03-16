from typing import Union

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.section import SDocSection
from strictdoc.core.traceability_index import (
    TraceabilityIndex,
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

    def perform(self):
        section: SDocSection = self.section
        section_parent: Union[SDocSection, SDocDocument] = assert_cast(
            section.parent, (SDocSection, SDocDocument)
        )
        section_parent.section_contents.remove(section)

        section.parent = None

        self.traceability_index.update_last_updated()
