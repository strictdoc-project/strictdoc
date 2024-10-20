# mypy: disable-error-code="no-untyped-def,type-arg"
from typing import List

from strictdoc.backend.sdoc_source_code.models.requirement_marker import Req
from strictdoc.helpers.auto_described import auto_described


@auto_described
class RangeMarker:
    def __init__(self, parent, begin_or_end, reqs_objs: List[Req]):
        assert isinstance(reqs_objs, list)
        self.parent = parent
        self.begin_or_end = begin_or_end
        self.reqs_objs: List[Req] = reqs_objs
        self.reqs: List[str] = list(map(lambda req: req.uid, reqs_objs))

        # Line number of the marker in the source code.
        self.ng_source_line_begin = None

        # Line number of the marker range in the source code:
        # TODO: Improve description.
        # For Begin ranges:
        #   ng_range_line_begin == ng_source_line_begin  # noqa: ERA001
        #   ng_range_line_end == ng_source_line_begin of the End marker  # noqa: ERA001, E501
        # For End ranges:
        #   ng_range_line_begin == ng_range_line_begin of the Begin marker  # noqa: ERA001, E501
        #   ng_range_line_end == ng_source_line_begin  # noqa: ERA001
        self.ng_range_line_begin = None
        self.ng_range_line_end = None

        self.ng_is_nodoc = "nosdoc" in self.reqs

    def is_begin(self):
        return self.begin_or_end == "["

    def is_end(self):
        return self.begin_or_end == "[/"

    def is_range_marker(self):
        return True

    def is_line_marker(self):
        return False


@auto_described
class LineMarker:
    def __init__(self, parent, reqs_objs):
        assert isinstance(reqs_objs, list)
        self.parent = parent
        self.reqs_objs = reqs_objs
        self.reqs = list(map(lambda req: req.uid, reqs_objs))

        # Line number of the marker in the source code.
        self.ng_source_line_begin = None

        self.ng_range_line_begin = None
        self.ng_range_line_end = None

        self.ng_is_nodoc = "nosdoc" in self.reqs

    def is_begin(self):
        return True

    def is_end(self):
        return False

    def is_range_marker(self):
        return False

    def is_line_marker(self):
        return True


@auto_described
class ForwardRangeMarker:
    def __init__(self, start_or_end: bool, reqs_objs: List):
        assert len(reqs_objs) > 0
        self.start_or_end: bool = start_or_end

        self.reqs_objs = reqs_objs

        # Line number of the marker in the source code.
        self.ng_source_line_begin = None

        self.ng_range_line_begin = None
        self.ng_range_line_end = None

    def is_begin(self):
        return self.start_or_end

    def is_end(self):
        return not self.start_or_end

    def is_range_marker(self):
        return True

    def is_line_marker(self):
        return False
