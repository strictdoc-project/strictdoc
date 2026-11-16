"""
@relation(SDOC-SRS-149, scope=file)
"""

from typing import Any, Optional

from strictdoc.helpers.auto_described import auto_described
from strictdoc.helpers.mid import MID


@auto_described()
class InlineLink:
    def __init__(
        self, parent: Any, value: str, title: Optional[str] = None
    ) -> None:
        self.parent: Any = parent
        self.link: str = value

        # An optional custom link text. When it is None, the link renders
        # the display title of the linked node.
        self.title: Optional[str] = None

        # The title as written in the source, with its quotes if it has them.
        # get_source_value() writes it back as is, so that the link text keeps
        # its length. For example, a grid table with the link stays aligned.
        self.source_title: Optional[str] = None
        if title is not None and len(title) > 0:
            self.title = title.strip('"')
            self.source_title = title

        # FIXME: Remove either mid or reserved_mid.
        self.mid: MID = MID.create()
        self.reserved_mid: MID = self.mid

    def parent_node(self) -> Any:
        return self.parent.get_owning_node()

    def get_source_value(self) -> str:
        if self.source_title is None:
            return f"[LINK: {self.link}]"
        return f"[LINK: {self.link}, {self.source_title}]"
