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
        # In the grammar, the title is optional but textX passes it as an empty
        # string. Putting an assert to monitor the regressions/changes if the
        # grammar gets changed.
        assert title is not None
        # FIXME: Cannot enable this assert because the parent can also be
        #        FreeTextContainer. Refactor the types.
        # assert isinstance(parent, SDocNodeFieldIF), parent  # noqa: ERA001

        self.parent: SDocNodeFieldIF = parent
        self.value: str = value

        has_title = len(title) > 0
        self.title: str = title if has_title else value
        self.has_title = has_title

        # FIXME: Remove either mid or reserved_mid.
        self.mid: MID = MID.create()
        self.reserved_mid: MID = self.mid

    def get_display_title(
        self,
        include_toc_number: bool = True,  # noqa: ARG002
    ) -> str:
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

    # FIXME: Remove this. Use get_parent_or_including_document() instead.
    @property
    def parent_or_including_document(self) -> SDocDocumentIF:
        return self.get_parent_or_including_document()

    def get_including_document(self) -> Optional[SDocDocumentIF]:
        return self.parent_node().get_including_document()

    def parent_node(self) -> SDocNodeIF:
        # Anchor -> SDocField -> SDocNode
        parent_node: SDocNodeIF = assert_cast(self.parent.parent, SDocNodeIF)
        return parent_node
