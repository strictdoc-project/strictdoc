import docutils.frontend
import docutils.parsers.rst
import docutils.utils

from docutils.nodes import document
from docutils.parsers.rst import directives

from strictdoc.backend.rst.directives.metadata import StdNodeDirective
from strictdoc.backend.rst.directives.document_metadata import (
    DocumentMetadataDirective
)
from strictdoc.backend.rst.rst_parser_shared_state import RSTParserSharedState


def observe(message):
    # docutils.nodes.system_message
    print((message.astext()))
    exit(1)


class RSTParser:

    @staticmethod
    def parse_rst(text: str) -> docutils.nodes.document:
        RSTParserSharedState.reset()

        directives.register_directive("metadata", StdNodeDirective)
        directives.register_directive("document-metadata", DocumentMetadataDirective)

        parser = docutils.parsers.rst.Parser(rfc2822=False)
        components = (docutils.parsers.rst.Parser,)
        settings = docutils.frontend.OptionParser(components=components).get_default_values()

        rst_document = docutils.utils.new_document('<rst-doc>', settings=settings)
        rst_document.reporter.attach_observer(observe)

        parser.parse(text, rst_document)

        return rst_document
