from typing import Set

from strictdoc.backend.dsl.models.config_special_field import ConfigSpecialField


class DocumentConfig:
    def __init__(self, parent, version, number, special_fields):
        self.parent = parent
        self.version = version
        self.number = number
        self.special_fields: [ConfigSpecialField] = special_fields
        self.special_fields_set: Set[str] = set()
        self.special_fields_required: [str] = []
        if special_fields:
            for user_field in self.special_fields:
                self.special_fields_set.add(user_field.field_name)
                if (
                    user_field.field_required
                    and user_field.field_required == "Yes"
                ):
                    self.special_fields_required.append(user_field.field_name)
