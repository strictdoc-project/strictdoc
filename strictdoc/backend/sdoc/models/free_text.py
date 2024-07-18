from typing import Any, List, Optional

from strictdoc.backend.sdoc.models.anchor import Anchor
from strictdoc.backend.sdoc.models.inline_link import InlineLink
from strictdoc.helpers.auto_described import auto_described


@auto_described
class FreeText:
    def __init__(self, parent: Any, parts: List[Any]) -> None:
        assert isinstance(parts, list)
        self.parent = parent
        self.parts = parts
        self.ng_level = None
        self.ng_line_start: Optional[int] = None
        self.ng_line_end: Optional[int] = None
        self.ng_col_start: Optional[int] = None
        self.ng_col_end: Optional[int] = None
        self.ng_byte_start: Optional[int] = None
        self.ng_byte_end: Optional[int] = None

    @property
    def parent_or_including_document(self) -> Optional[Any]:
        return self.parent.parent_or_including_document

    @property
    def is_requirement(self) -> bool:
        return False

    @property
    def is_section(self) -> bool:
        return False

    def get_parts_as_text(self) -> str:
        # [LINK: SECTION-CUSTOM-GRAMMARS]
        text = ""
        for part in self.parts:
            if isinstance(part, str):
                text += part
            elif isinstance(part, InlineLink):
                text += "[LINK: "
                text += part.link
                text += "]"
            elif isinstance(part, Anchor):
                text += "[ANCHOR: "
                text += part.value
                if part.has_title:
                    text += ", "
                    text += part.title
                text += "]"
                text += "\n"
                text += "\n"
            else:
                raise NotImplementedError(part)
        return text


class FreeTextContainer(FreeText):
    def __init__(self, parts: List[Any]) -> None:
        super().__init__(None, parts)
