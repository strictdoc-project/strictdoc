from strictdoc.backend.rst_writer import write_rst


class RSTDocument:
    rst_document = None
    lines = None

    def __init__(self, rst_document, lines):
        assert rst_document
        assert lines

        self.rst_document = rst_document
        self.lines = lines

    def get_as_list(self):
        return self.lines

    def dump_pretty(self):
        # How to print a reStructuredText node tree?
        # https://stackoverflow.com/a/20914785/598057
        print('dump_pretty:')
        print(self.rst_document.pformat())
        # from docutils.core import publish_string
        # print(publish_string(input_rst))

    def dump_rst(self):
        # How to print a reStructuredText node tree?
        # https://stackoverflow.com/a/20914785/598057
        print('*** dump_rst: ***')
        rst = write_rst(self.rst_document)
        print(rst)
        return rst
