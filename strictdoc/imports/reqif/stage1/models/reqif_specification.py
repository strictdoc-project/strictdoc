class ReqIFSpecification:
    def __init__(self, identifier, long_name, children):
        self.identifier = identifier
        self.long_name = long_name
        self.children = children

    def __repr__(self):
        return (
            f"ReqIFSpecification("
            f"identifier: {self.identifier},"
            f"children: {self.children},"
            f")"
        )
