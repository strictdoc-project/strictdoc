# mypy: disable-error-code="no-untyped-def"
class ErrorObject:
    def __init__(self):
        self.errors = {}

    def any_errors(self):
        return len(self.errors)

    def has_errors(self, field_name):
        return field_name in self.errors

    def get_errors(self, field_name):
        if field_name not in self.errors:
            return []
        return self.errors[field_name]

    def add_error(self, field_name, error):
        error_container = self.errors.setdefault(field_name, [])
        error_container.append(error)
