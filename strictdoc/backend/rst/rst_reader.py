import docutils.frontend
import docutils.nodes
import docutils.parsers.rst
import docutils.utils
from docutils.nodes import NodeVisitor

from strictdoc.backend.rst.rst_parser import RSTParser
from strictdoc.backend.rst.rst_document import RSTDocument


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


class RSTReader:
    @staticmethod
    def read_rst(text: str) -> RSTDocument:
        rst_document = RSTParser.parse_rst(text)

        visitor = RSTReadVisitor(rst_document)
        rst_document.walkabout(visitor)

        lines = visitor.get_lines()
        return RSTDocument(rst_document, lines)

