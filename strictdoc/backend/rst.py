import docutils.nodes
import docutils.parsers.rst
import docutils.utils
import docutils.frontend

from docutils.parsers.rst import directives

from strictdoc.backend.meta import StdNodeDirective
from strictdoc.backend.rst_writer import write_rst


def parse_rst(text: str) -> docutils.nodes.document:
    parser = docutils.parsers.rst.Parser()
    components = (docutils.parsers.rst.Parser,)
    settings = docutils.frontend.OptionParser(components=components).get_default_values()

    document = docutils.utils.new_document('<rst-doc>', settings=settings)
    parser.parse(text, document)
    return document


directives.register_directive("std-node", StdNodeDirective)

from docutils.core import publish_string


def dump_pretty(input_rst):
    # How to print a reStructuredText node tree?
    # https://stackoverflow.com/a/20914785/598057
    print('dump_pretty:')
    doc = parse_rst(input_rst)
    print(doc.pformat())
    # print(publish_string(input_rst))


def dump_rst(input_rst):
    # How to print a reStructuredText node tree?
    # https://stackoverflow.com/a/20914785/598057
    print('*** dump_rst: ***')
    doc = parse_rst(input_rst)

    rst = write_rst(doc)
    print(rst)
    return rst

