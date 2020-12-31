class ConfigSpecialField:
    def __init__(self, parent, field_name, field_type, field_required):
        self.parent = parent
        self.field_name = field_name
        self.field_type = field_type
        self.field_required = field_required

    def __str__(self):
        return (
            "{}: <field_name: {}, field_type: {}, field_required: {}>".format(
                self.__class__.__name__,
                self.field_name,
                self.field_type,
                self.field_required,
            )
        )

    def __repr__(self):
        return self.__str__()
