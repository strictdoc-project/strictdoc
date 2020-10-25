import docutils.frontend
import docutils.nodes
import docutils.parsers.rst
import docutils.utils
from docutils.nodes import NodeVisitor

from saturn.backend.rst.rst_constants import SATURN_ATTR_LEVEL

HEADER_LEVELS = {
  '=': 1,
  '-': 2,
  '~': 3,
  '^': 4
}


class RSTReadVisitor(NodeVisitor):
    lines = []
    source_lines = None

    def __init__(self, document, source_text=None):
        super(RSTReadVisitor, self).__init__(document)
        self.source_lines = source_text.split('\n') if source_text else None
        self.lines = []
        document[SATURN_ATTR_LEVEL] = 0

    def unknown_visit(self, node: docutils.nodes.Node) -> None:
        if isinstance(node, docutils.nodes.document):
            return

        if isinstance(node, docutils.nodes.section):
            if not self.source_lines:
                return

            assert node.line > 0
            assert node.line <= len(self.source_lines)

            header_line = self.source_lines[node.line - 1]
            assert len(header_line) > 0

            header_line_char = header_line[0]

            node[SATURN_ATTR_LEVEL] = self._get_header_level(header_line_char)

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
            return

        pass

    def get_lines(self):
        return self.lines

    @staticmethod
    def _get_header_level(char):
        level = HEADER_LEVELS[char]
        return level
