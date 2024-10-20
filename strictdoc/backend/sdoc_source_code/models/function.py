from typing import Any, List

from strictdoc.helpers.auto_described import auto_described


@auto_described
class Function:
    def __init__(self, parent: Any, name: str, parts: List[Any]):
        self.parent = parent
        self.name = name
        self.parts: List[Any] = parts
        self.line_begin = -1
        self.line_end = -1
