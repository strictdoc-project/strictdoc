class SpecialField:
    def __init__(self, parent, field_name, field_value):
        self.parent = parent
        self.field_name = field_name
        self.field_value = field_value

    def __str__(self):
        return "{}({}: {})".format(
            self.__class__.__name__, self.field_name, self.field_value
        )

    def __repr__(self):
        return self.__str__()
