import docutils.frontend
import docutils.nodes
import docutils.parsers.rst
import docutils.utils
from docutils.nodes import NodeVisitor

from strictdoc.backend.rst_writer import write_rst


def observe(message):
    # docutils.nodes.system_message
    print((message.astext()))
    exit(1)


class RSTReadVisitor(NodeVisitor):
    lines = []

    def unknown_visit(self, node: docutils.nodes.Node) -> None:
        if isinstance(node, docutils.nodes.document):
            return

        if isinstance(node, docutils.nodes.section):
            return

        if isinstance(node, docutils.nodes.title):
            text = node.astext()
            self.lines.append(text)
            return

        if isinstance(node, docutils.nodes.paragraph):
            text = node.astext()
            self.lines.append(text)
            return

        return

    def unknown_departure(self, node):
        pass

    def get_lines(self):
        return self.lines


class Document:
    rst_document = None

    def __init__(self, rst_document):
        assert rst_document

        self.rst_document = rst_document

    @staticmethod
    def create_from_rst(text: str):
        rst_document = Document.parse_rst(text)
        return Document(rst_document)

    @staticmethod
    def parse_rst(text: str) -> docutils.nodes.document:
        parser = docutils.parsers.rst.Parser()
        components = (docutils.parsers.rst.Parser,)
        settings = docutils.frontend.OptionParser(components=components).get_default_values()

        document = docutils.utils.new_document('<rst-doc>', settings=settings)
        document.reporter.attach_observer(observe)

        parser.parse(text, document)

        return document

    def get_as_list(self):
        visitor = RSTReadVisitor(self.rst_document)
        self.rst_document.walkabout(visitor)

        lines = visitor.get_lines()
        return lines

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
