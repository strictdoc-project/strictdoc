from typing import List

from strictdoc.backend.sdoc.models.inline_link import InlineLink


class FreeText:
    def __init__(self, parent, parts: List):
        assert isinstance(parts, list)
        self.parent = parent
        self.parts = parts
        self.ng_level = None

    def __str__(self):
        return f"FreeText(parts={self.parts})"

    def __repr__(self):
        return self.__str__()

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
