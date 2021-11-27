class ConfigSpecialField:
    def __init__(self, parent, field_name, field_type, field_required):
        assert field_type == "String"
        self.parent = parent
        self.field_name = field_name
        self.field_type = field_type
        self.field_required = field_required

    def __str__(self):
        return (
            f"{self.__class__.__name__}("
            f"field_name: {self.field_name}, "
            f"field_type: {self.field_type}, "
            f"field_required: {self.field_required}"
            f")"
        )

    def __repr__(self):
        return self.__str__()
