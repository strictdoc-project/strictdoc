from typing import Union

from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.models.section import Section
from strictdoc.core.traceability_index import (
    TraceabilityIndex,
)
from strictdoc.helpers.cast import assert_cast


class DeleteSectionCommand:
    def __init__(
        self,
        section: Section,
        traceability_index: TraceabilityIndex,
    ):
        self.section: Section = section
        self.traceability_index: TraceabilityIndex = traceability_index

    def perform(self):
        section: Section = self.section
        section_parent: Union[Section, Document] = assert_cast(
            section.parent, (Section, Document)
        )
        section_parent.section_contents.remove(section)

        section.parent = None
