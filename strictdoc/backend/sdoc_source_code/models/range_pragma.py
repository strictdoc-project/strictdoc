from strictdoc.helpers.auto_described import auto_described


@auto_described
class RangePragma:  # pylint: disable=too-many-instance-attributes
    def __init__(self, parent, begin_or_end, reqs_objs):
        assert isinstance(reqs_objs, list)
        self.parent = parent
        self.begin_or_end = begin_or_end
        self.reqs_objs = reqs_objs
        self.reqs = list(map(lambda req: req.uid, reqs_objs))

        # Line number of the pragma in the source code.
        self.ng_source_line_begin = None

        # Line number of the pragma range in the source code:
        # TODO: Improve description.
        # For Begin pragmas:
        #   ng_range_line_begin == ng_source_line_begin  # noqa: ERA001
        #   ng_range_line_end == ng_source_line_begin of the End pragma  # noqa: ERA001, E501
        # For End pragmas:
        #   ng_range_line_begin == ng_range_line_begin of the Begin pragma  # noqa: ERA001, E501
        #   ng_range_line_end == ng_source_line_begin  # noqa: ERA001
        self.ng_range_line_begin = None
        self.ng_range_line_end = None

        self.ng_is_nodoc = "nosdoc" in self.reqs

    def is_begin(self):
        return self.begin_or_end == "["

    def is_end(self):
        return self.begin_or_end == "[/"
