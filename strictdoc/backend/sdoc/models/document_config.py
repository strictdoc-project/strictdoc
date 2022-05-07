from typing import Optional


class DocumentConfig:  # pylint: disable=too-many-instance-attributes
    @staticmethod
    def default_config(document):
        return DocumentConfig(
            parent=document,
            version=None,
            number=None,
            markup=None,
            auto_levels=None,
            requirement_style=None,
        )

    def __init__(  # pylint: disable=too-many-arguments
        self,
        *,
        parent,
        version,
        number,
        markup: Optional[str],
        auto_levels: Optional[str],
        requirement_style: Optional[str],
    ):
        self.parent = parent
        self.version = version
        self.number = number
        self.markup = markup
        self.auto_levels: bool = auto_levels is None or auto_levels == "On"
        self.requirement_style: Optional[str] = requirement_style
        self.ng_auto_levels_specified = auto_levels is not None

    def is_inline_requirements(self):
        return (
            self.requirement_style is None or self.requirement_style == "Inline"
        )
