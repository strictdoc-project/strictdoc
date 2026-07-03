"""
@relation(SDOC-SRS-150, scope=file)
"""

# mypy: disable-error-code="unreachable"

from typing import Optional

from strictdoc.backend.sdoc.models.model import (
    SDocDocumentIF,
    SDocNodeFieldIF,
    SDocNodeIF,
)
from strictdoc.helpers.auto_described import auto_described
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.mid import MID


@auto_described
class Anchor:
    def __init__(
        self, parent: SDocNodeFieldIF, value: str, title: Optional[str]
    ) -> None:
        # FIXME: Cannot enable this assert because the parent can also be
        #        FreeTextContainer. Refactor the types.
        # assert isinstance(parent, SDocNodeFieldIF), parent  # noqa: ERA001

        self.parent: SDocNodeFieldIF = parent
        self.value: str = value

        if title is not None and len(title) > 0:
            self.title: str = title.strip('"')
            self.has_title = True
        else:
            self.title = value
            self.has_title = False

        # FIXME: Remove either mid or reserved_mid.
        self.mid: MID = MID.create()
        self.reserved_mid: MID = self.mid

    def get_display_title(
        self,
        include_toc_number: bool = True,  # noqa: ARG002
    ) -> str:
        return self.title

    def get_source_title(self) -> str:
        if "," in self.title or "]" in self.title:
            return f'"{self.title}"'
        return self.title

    def get_document(self) -> SDocDocumentIF:
        if isinstance(self.parent.parent, SDocDocumentIF):
            return self.parent.parent
        document: SDocDocumentIF = assert_cast(
            self.parent_node().get_document(), SDocDocumentIF
        )
        return document

    def get_parent_or_including_document(self) -> SDocDocumentIF:
        return self.parent_node().get_parent_or_including_document()

    def get_including_document(self) -> Optional[SDocDocumentIF]:
        return self.parent_node().get_including_document()

    def parent_node(self) -> SDocNodeIF:
        # Anchor -> SDocField -> SDocNode.
        parent_node: SDocNodeIF = assert_cast(self.parent.parent, SDocNodeIF)
        return parent_node
