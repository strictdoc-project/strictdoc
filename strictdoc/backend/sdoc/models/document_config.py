from typing import Optional

from strictdoc.helpers.auto_described import auto_described


@auto_described
class DocumentConfig:  # pylint: disable=too-many-instance-attributes
    @staticmethod
    def default_config(document):
        return DocumentConfig(
            parent=document,
            version=None,
            uid=None,
            classification=None,
            markup=None,
            auto_levels=None,
            requirement_style=None,
            requirement_in_toc=None,
        )

    def __init__(  # pylint: disable=too-many-arguments
        self,
        *,
        parent,
        version: Optional[str],
        uid: Optional[str],
        classification: Optional[str],
        markup: Optional[str],
        auto_levels: Optional[str],
        requirement_style: Optional[str],
        requirement_in_toc: Optional[str],
    ):
        self.parent = parent
        self.version: Optional[str] = version
        self.uid: Optional[str] = uid
        self.classification: Optional[str] = classification
        self.markup = markup
        self.auto_levels: bool = auto_levels is None or auto_levels == "On"
        self.requirement_style: Optional[str] = requirement_style
        self.requirement_in_toc: Optional[str] = requirement_in_toc
        self.ng_auto_levels_specified = auto_levels is not None

    def is_inline_requirements(self):
        return (
            self.requirement_style is None or self.requirement_style == "Inline"
        )

    def is_requirement_in_toc(self):
        return (
            self.requirement_in_toc is None or self.requirement_in_toc == "True"
        )

    def has_meta(self):
        # TODO: When OPTIONS are not provided to a document, the self.number and
        # self.version are both None. Otherwise, they become empty strings "".
        # This issue might deserve a bug report to TextX.
        return (self.uid is not None and len(self.uid) > 0) or (
            self.version is not None and len(self.version) > 0
        )
