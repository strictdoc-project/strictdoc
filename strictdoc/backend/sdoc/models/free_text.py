from typing import List

from strictdoc.backend.sdoc.models.inline_link import InlineLink
from strictdoc.helpers.auto_described import auto_described


@auto_described
class FreeText:
    def __init__(self, parent, parts: List):
        assert isinstance(parts, list)
        self.parent = parent
        self.parts = parts
        self.ng_level = None

    @property
    def is_requirement(self):
        return False

    @property
    def is_section(self):
        return False

    def get_parts_as_text(self):
        # [LINK: SECTION-CUSTOM-GRAMMARS]
        text = ""
        for part in self.parts:
            if isinstance(part, str):
                text += part
            elif isinstance(part, InlineLink):
                text += "[LINK: "
                text += part.link
                text += "]"
        return text


class FreeTextContainer(FreeText):
    def __init__(self, parts):
        super().__init__(None, parts)
