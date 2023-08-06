from strictdoc.helpers.auto_described import auto_described
from strictdoc.helpers.mid import MID


@auto_described()
class InlineLink:
    def __init__(self, parent, value):
        self.parent = parent
        self.link = value

        self.mid: MID = MID.create()

    def parent_node(self):
        return self.parent.parent
