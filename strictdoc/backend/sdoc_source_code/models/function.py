"""
@relation(SDOC-SRS-142, scope=file)
"""

from typing import Any, List, Set

from strictdoc.backend.sdoc_source_code.constants import FunctionAttribute
from strictdoc.backend.sdoc_source_code.models.function_range_marker import (
    FunctionRangeMarker,
)
from strictdoc.helpers.auto_described import auto_described


@auto_described
class Function:
    def __init__(
        self,
        parent: Any,
        name: str,
        display_name: str,
        line_begin: int,
        line_end: int,
        child_functions: List[Any],
        markers: List[FunctionRangeMarker],
        attributes: Set[FunctionAttribute],
    ):
        assert parent is not None
        self.parent = parent
        self.name = name
        self.display_name = display_name

        # Child functions are supported in programming languages that can nest
        # functions, for example, Python.
        self.child_functions: List[Function] = child_functions
        self.markers: List[FunctionRangeMarker] = markers
        self.line_begin = line_begin
        self.line_end = line_end
        self.attributes: Set[FunctionAttribute] = attributes

    def is_declaration(self) -> bool:
        return FunctionAttribute.DECLARATION in self.attributes

    def is_definition(self) -> bool:
        return FunctionAttribute.DEFINITION in self.attributes

    def is_public(self) -> bool:
        return FunctionAttribute.STATIC not in self.attributes
