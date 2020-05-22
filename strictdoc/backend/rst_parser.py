import docutils.frontend
import docutils.parsers.rst
import docutils.utils

from docutils.nodes import document


def observe(message):
    # docutils.nodes.system_message
    print((message.astext()))
    exit(1)


class RSTParser:

    @staticmethod
    def parse_rst(text: str) -> docutils.nodes.document:
        parser = docutils.parsers.rst.Parser()
        components = (docutils.parsers.rst.Parser,)
        settings = docutils.frontend.OptionParser(components=components).get_default_values()

        rst_document = docutils.utils.new_document('<rst-doc>', settings=settings)
        rst_document.reporter.attach_observer(observe)

        parser.parse(text, rst_document)

        return rst_document
