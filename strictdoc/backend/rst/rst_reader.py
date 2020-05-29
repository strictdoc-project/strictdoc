import docutils.frontend
import docutils.nodes
import docutils.parsers.rst
import docutils.utils
from docutils.nodes import NodeVisitor

from strictdoc.backend.rst.visitors.rst_read_visitor import RSTReadVisitor
from strictdoc.backend.rst.rst_parser import RSTParser
from strictdoc.backend.rst.rst_document import RSTDocument


class RSTReader:
    @staticmethod
    def read_rst(text: str) -> RSTDocument:
        rst_document = RSTParser.parse_rst(text)

        visitor = RSTReadVisitor(rst_document, text)
        rst_document.walkabout(visitor)

        lines = visitor.get_lines()
        return RSTDocument(rst_document, lines)

