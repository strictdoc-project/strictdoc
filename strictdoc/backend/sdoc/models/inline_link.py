from strictdoc.helpers.auto_described import auto_described
from strictdoc.helpers.mid import MID


@auto_described()
class InlineLink:
    def __init__(self, parent, value):
        self.parent = parent
        self.link = value

        # FIXME: Remove either mid or reserved_mid.
        self.mid: MID = MID.create()
        self.reserved_mid: MID = self.mid

    def parent_node(self):
        return self.parent.parent
