from strictdoc.helpers.mid import MID


class InlineLink:
    def __init__(self, parent, value):
        self.parent = parent
        self.link = value

        self.mid: MID = MID.create()

    def parent_node(self):
        return self.parent.parent
