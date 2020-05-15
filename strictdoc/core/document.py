import docutils.nodes
import docutils.parsers.rst
import docutils.utils
import docutils.frontend

from docutils.parsers.rst import directives
from docutils.nodes import system_message

from strictdoc.backend.meta import StdNodeDirective
from strictdoc.backend.rst_writer import write_rst


def observe(message):
    # docutils.nodes.system_message
    print((message.astext()))
    exit(1)


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
