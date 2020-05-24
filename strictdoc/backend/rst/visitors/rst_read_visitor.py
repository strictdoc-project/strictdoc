import docutils.frontend
import docutils.nodes
import docutils.parsers.rst
import docutils.utils
from docutils.nodes import NodeVisitor

from strictdoc.backend.rst.rst_constants import STRICTDOC_ATTR_LEVEL


class RSTReadVisitor(NodeVisitor):
    lines = []
    level = 0

    def __init__(self, document, starting_header_level = 0):
        super(RSTReadVisitor, self).__init__(document)
        self.lines = []
        self.level = starting_header_level

    def unknown_visit(self, node: docutils.nodes.Node) -> None:
        if isinstance(node, docutils.nodes.document):
            return

        if isinstance(node, docutils.nodes.section):
            self.level += 1

            node[STRICTDOC_ATTR_LEVEL] = self.level

            return

        if isinstance(node, docutils.nodes.title):
            self.lines.append(node)
            return

        if isinstance(node, docutils.nodes.paragraph):
            self.lines.append(node)
            return

        return

    def unknown_departure(self, node):
        if isinstance(node, docutils.nodes.section):
            self.level -= 1

            return

        pass

    def get_lines(self):
        return self.lines
