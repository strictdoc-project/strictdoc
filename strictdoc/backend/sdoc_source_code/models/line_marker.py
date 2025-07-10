"""
@relation(SDOC-SRS-124, scope=file)
"""

from typing import Any, List, Optional

from strictdoc.backend.sdoc_source_code.models.requirement_marker import Req
from strictdoc.helpers.auto_described import auto_described


@auto_described
class LineMarker:
    def __init__(
        self, parent: Any, reqs_objs: List[Req], role: Optional[str] = None
    ) -> None:
        assert isinstance(reqs_objs, list)
        self.parent = parent
        self.reqs_objs: List[Req] = reqs_objs
        self.reqs: List[str] = list(map(lambda req: req.uid, reqs_objs))
        self.role: Optional[str] = (
            role if role is not None and len(role) > 0 else None
        )

        # Line number of the marker in the source code.
        self.ng_source_line_begin: Optional[int] = None
        self.ng_source_column_begin: Optional[int] = None

        self.ng_range_line_begin: Optional[int] = None
        self.ng_range_line_end: Optional[int] = None

        self.ng_is_nodoc: bool = "nosdoc" in self.reqs
        self.begin_or_end = True

    def is_begin(self) -> bool:
        return True

    def is_end(self) -> bool:
        return False

    def is_range_marker(self) -> bool:
        return False

    def is_line_marker(self) -> bool:
        return True

    def is_forward(self) -> bool:
        return False

    def get_description(self) -> Optional[str]:
        return "line"
