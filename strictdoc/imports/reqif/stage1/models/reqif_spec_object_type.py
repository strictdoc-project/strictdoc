class ReqIFSpecObjectType:
    def __init__(self, identifier, long_name, attribute_map):
        self.identifier = identifier
        self.long_name = long_name
        self.attribute_map = attribute_map

    def __str__(self):
        return (
            f"ReqIFSpecObjectType("
            f"identifier: {self.identifier}"
            ", "
            f"attribute_map: {self.attribute_map}"
            f")"
        )

    def __repr__(self):
        return self.__str__()
