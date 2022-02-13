from typing import Optional


class DocumentConfig:  # pylint: disable=too-many-instance-attributes
    @staticmethod
    def default_config(document):
        return DocumentConfig(document, None, None, None, None)

    def __init__(  # pylint: disable=too-many-arguments
        self,
        parent,
        version,
        number,
        markup: Optional[str],
        auto_levels: Optional[str],
    ):
        self.parent = parent
        self.version = version
        self.number = number
        self.markup = markup
        self.auto_levels: bool = auto_levels is None or auto_levels == "On"
        self.ng_auto_levels_specified = auto_levels is not None
