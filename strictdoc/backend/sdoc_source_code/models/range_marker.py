# mypy: disable-error-code="no-untyped-def,type-arg"
from typing import Any, List, Optional

from strictdoc.backend.sdoc_source_code.models.requirement_marker import Req
from strictdoc.helpers.auto_described import auto_described


@auto_described
class RangeMarker:
    def __init__(
        self,
        parent: Any,
        begin_or_end: str,
        reqs_objs: List[Req],
        scope: str = "",
        role: Optional[str] = None,
    ):
        assert isinstance(reqs_objs, list)
        self.parent: Any = parent
        assert len(begin_or_end) > 0 or scope is not None

        self.begin_or_end: str
        if len(begin_or_end) > 0:
            self.begin_or_end = begin_or_end
        else:
            assert scope in ("range_start", "range_end")
            self.begin_or_end = "[" if scope == "range_start" else "[/"
            self.ng_new_relation_keyword = True

        self.reqs_objs: List[Req] = reqs_objs
        self.reqs: List[str] = list(map(lambda req: req.uid, reqs_objs))
        self.role: Optional[str] = (
            role if role is not None and len(role) > 0 else None
        )

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

        self.ng_is_nodoc: bool = "nosdoc" in self.reqs
        self.ng_new_relation_keyword = scope is not None and len(scope) > 0

    def is_begin(self) -> bool:
        return self.begin_or_end == "["

    def is_end(self) -> bool:
        return self.begin_or_end == "[/"

    def is_range_marker(self) -> bool:
        return True

    def is_line_marker(self) -> bool:
        return False

    def is_forward(self) -> bool:
        return False

    def get_description(self) -> Optional[str]:
        return "range"


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


@auto_described
class ForwardRangeMarker:
    def __init__(
        self, start_or_end: bool, reqs_objs: List, role: Optional[str] = None
    ):
        assert len(reqs_objs) > 0
        self.start_or_end: bool = start_or_end

        self.reqs_objs: List[str] = reqs_objs
        self.reqs: List[str] = list(map(lambda req: req.uid, reqs_objs))

        self.role: Optional[str] = (
            role if role is not None and len(role) > 0 else None
        )

        # Line number of the marker in the source code.
        self.ng_source_line_begin: Optional[int] = None

        self.ng_range_line_begin: Optional[int] = None
        self.ng_range_line_end: Optional[int] = None

        self.ng_is_nodoc: bool = False

    def is_begin(self) -> bool:
        return self.start_or_end

    def is_end(self) -> bool:
        return not self.start_or_end

    def is_range_marker(self) -> bool:
        return True

    def is_line_marker(self) -> bool:
        return False

    def get_description(self) -> Optional[str]:
        return "range"

    def is_forward(self) -> bool:
        return True


@auto_described
class ForwardFileMarker(ForwardRangeMarker):
    def __init__(self, reqs_objs: List, role: Optional[str] = None):
        super().__init__(True, reqs_objs, role)

    def get_description(self) -> Optional[str]:
        return "entire file"

    def is_forward(self) -> bool:
        return True
