from typing import Dict


class ReqIFSpecObject:
    def __init__(self, identifier, spec_object_type, attribute_map):
        self.identifier = identifier
        self.spec_object_type = spec_object_type
        self.attribute_map: Dict[str, str] = attribute_map

    def __str__(self):
        return (
            f"ReqIFSpecObject("
            f"identifier: {self.identifier}"
            ", "
            f"spec_object_type: {self.spec_object_type}"
            ", "
            f"attribute_map: {self.attribute_map}"
            f")"
        )

    def __repr__(self):
        return self.__str__()
