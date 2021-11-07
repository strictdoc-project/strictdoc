from typing import Set, Optional

from strictdoc.backend.dsl.models.config_special_field import ConfigSpecialField


class DocumentConfig:
    @staticmethod
    def default_config(document):
        return DocumentConfig(document, None, None, None, None, None)

    def __init__(
        self,
        parent,
        version,
        number,
        special_fields,
        markup: Optional[str],
        auto_levels: Optional[str],
    ):
        self.parent = parent
        self.version = version
        self.number = number
        self.special_fields: [ConfigSpecialField] = special_fields
        self.markup = markup
        self.auto_levels: bool = (
            True if (auto_levels is None or auto_levels == "On") else False
        )
        self.ng_auto_levels_specified = auto_levels is not None

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
