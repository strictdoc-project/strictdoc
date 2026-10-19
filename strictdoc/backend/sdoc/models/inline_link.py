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
        if title is not None and len(title) > 0:
            self.title = title.strip('"')

        # FIXME: Remove either mid or reserved_mid.
        self.mid: MID = MID.create()
        self.reserved_mid: MID = self.mid

    def parent_node(self) -> Any:
        return self.parent.get_owning_node()

    def get_source_value(self) -> str:
        if self.title is None:
            return f"[LINK: {self.link}]"
        title = self.title
        if "," in title or "]" in title:
            title = f'"{title}"'
        return f"[LINK: {self.link}, {title}]"
