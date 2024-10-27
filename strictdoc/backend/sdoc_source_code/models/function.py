from typing import Any, List

from strictdoc.helpers.auto_described import auto_described


@auto_described
class Function:
    def __init__(
        self,
        parent: Any,
        name: str,
        line_begin: int,
        line_end: int,
        parts: List[Any],
    ):
        self.parent = parent
        self.name = name
        self.parts: List[Any] = parts
        self.line_begin = line_begin
        self.line_end = line_end
