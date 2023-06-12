from strictdoc.core.graph_database import UUID


class InlineLink:
    def __init__(self, parent, value):
        self.parent = parent
        self.link = value

        self.uuid: UUID = UUID.create()
