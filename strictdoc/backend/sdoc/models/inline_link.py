# mypy: disable-error-code="no-untyped-call,no-untyped-def"
from typing import Any

from strictdoc.helpers.auto_described import auto_described
from strictdoc.helpers.mid import MID


@auto_described()
class InlineLink:
    def __init__(self, parent: Any, value: str) -> None:
        self.parent: Any = parent
        self.link: str = value

        # FIXME: Remove either mid or reserved_mid.
        self.mid: MID = MID.create()
        self.reserved_mid: MID = self.mid

    def parent_node(self) -> Any:
        return self.parent.parent
