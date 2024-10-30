# mypy: disable-error-code="no-untyped-def,type-arg"
from typing import List, Optional

from strictdoc.backend.sdoc_source_code.models.requirement_marker import Req
from strictdoc.helpers.auto_described import auto_described


@auto_described
class FunctionRangeMarker:
    def __init__(self, parent, reqs_objs: List[Req]):
        assert isinstance(reqs_objs, list)
        self.parent = parent
        self.reqs_objs: List[Req] = reqs_objs
        self.reqs: List[str] = list(map(lambda req: req.uid, reqs_objs))

        # Line number of the marker in the source code.
        self.ng_source_line_begin: Optional[int] = None
        self.ng_source_column_begin: Optional[int] = None

        # Line number of the marker range in the source code:
        # TODO: Improve description.
        # For Begin ranges:
        #   ng_range_line_begin == ng_source_line_begin  # noqa: ERA001
        #   ng_range_line_end == ng_source_line_begin of the End marker  # noqa: ERA001, E501
        # For End ranges:
        #   ng_range_line_begin == ng_range_line_begin of the Begin marker  # noqa: ERA001, E501
        #   ng_range_line_end == ng_source_line_begin  # noqa: ERA001
        self.ng_range_line_begin: Optional[int] = None
        self.ng_range_line_end: Optional[int] = None

        self.ng_marker_line: Optional[int] = None
        self.ng_marker_column: Optional[int] = None

        self.ng_is_nodoc = "nosdoc" in self.reqs

    def is_range_marker(self) -> bool:
        return True

    def is_line_marker(self) -> bool:
        return False

    def is_begin(self) -> bool:
        return True

    def is_end(self) -> bool:
        return False


@auto_described
class ForwardFunctionRangeMarker(FunctionRangeMarker):
    def __init__(self, parent, reqs_objs: List[Req]):
        super().__init__(parent, reqs_objs)