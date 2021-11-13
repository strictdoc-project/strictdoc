class ReqIFSpecHierarchy:
    def __init__(self, identifier, spec_object, children, level):
        self.identifier = identifier
        self.spec_object = spec_object
        self.children = children

        # Not part of ReqIF, but helpful to calculate the section depth levels.
        self.level = level

    def __str__(self):
        return (
            f"ReqIFSpecHierarchy("
            f"level: {self.level}"
            f", "
            f"identifier: {self.identifier}"
            f")"
        )

    def __repr__(self):
        return self.__str__()
