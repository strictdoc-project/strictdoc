from strictdoc.helpers.auto_described import auto_described


@auto_described
class RangePragma:
    def __init__(self, parent, begin_or_end, reqs_objs):
        assert isinstance(reqs_objs, list)
        self.parent = parent
        self.begin_or_end = begin_or_end
        self.reqs_objs = reqs_objs
        self.reqs = list(map(lambda req: req.uid, reqs_objs))

        # Line number of the pragma in the source code.
        self.ng_source_line_begin = None

        # Line number of the pragma range in the source code:
        # For Begin pragmas:
        #   ng_range_line_begin == ng_source_line_begin
        #   ng_range_line_end == ng_source_line_begin of the End pragma
        # For End pragmas:
        #   ng_range_line_begin == ng_range_line_begin of the Begin pragma
        #   ng_range_line_end == ng_source_line_begin
        self.ng_range_line_begin = None
        self.ng_range_line_end = None

    def is_begin(self):
        return self.begin_or_end == "["

    def is_end(self):
        return self.begin_or_end == "[/"
