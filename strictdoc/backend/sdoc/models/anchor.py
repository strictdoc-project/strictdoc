from typing import Optional

from strictdoc.helpers.auto_described import auto_described
from strictdoc.helpers.mid import MID


@auto_described
class Anchor:
    def __init__(self, parent, value: str, title: Optional[str]):
        # In the grammar, the title is optional but textX passes it as an empty
        # string. Putting an assert to monitor the regressions/changes if the
        # grammar gets changed.
        assert title is not None
        self.parent = parent
        self.value: str = value

        has_title = len(title) > 0
        self.title: str = title if has_title else value
        self.has_title = has_title

        self.mid: MID = MID.create()

    @property
    def document(self):
        if self.parent.parent.__class__.__name__ == "Document":
            return self.parent.parent
        return self.parent.parent.document
