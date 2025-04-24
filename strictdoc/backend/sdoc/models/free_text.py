from typing import Any, List, Optional


class FreeTextContainer:
    def __init__(self, parts: List[Any]) -> None:
        assert isinstance(parts, list)
        self.parts = parts
        self.ng_level = None
        self.ng_line_start: Optional[int] = None
        self.ng_line_end: Optional[int] = None
        self.ng_col_start: Optional[int] = None
        self.ng_col_end: Optional[int] = None
        self.ng_byte_start: Optional[int] = None
        self.ng_byte_end: Optional[int] = None
