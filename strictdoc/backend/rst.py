import docutils.nodes
import docutils.parsers.rst
import docutils.utils
import docutils.frontend

from docutils import nodes
from docutils.parsers.rst import directives
from docutils.parsers.rst import Directive
from docutils.statemachine import StringList, ViewList


def parse_rst(text: str) -> docutils.nodes.document:
    parser = docutils.parsers.rst.Parser()
    components = (docutils.parsers.rst.Parser,)
    settings = docutils.frontend.OptionParser(components=components).get_default_values()

    document = docutils.utils.new_document('<rst-doc>', settings=settings)
    parser.parse(text, document)
    return document


class MyVisitor(docutils.nodes.NodeVisitor):
    def visit_reference(self, node: docutils.nodes.reference) -> None:
        """Called for "reference" nodes."""
        print("REFERENCE")
        print(node)

    def unknown_visit(self, node: docutils.nodes.Node) -> None:
        """Called for all other node types."""
        print("unknown_visit:")
        print(node)
        pass

supported_categories = [
    'types',
    'keywords',
    'languages',
    'industries',
    'standards',
    'companies',
    'people'
]

categories_spec = {
    category: directives.unchanged_required
    for category in supported_categories
}


class MetaInfoNode(nodes.General, nodes.Element):
    meta_information = None

    def __init__(self, meta_information):
        assert meta_information
        super(MetaInfoNode, self).__init__()
        self.meta_information = meta_information

    def get_meta_information(self):
        return self.meta_information


class ASCMetaDirective(Directive):
    has_content = True

    option_spec = categories_spec

    def run(self):
        meta_information = {}

        if not self.options:
            raise SystemExit(1)

        for option in self.options.keys():
            if option not in meta_information:
                meta_information[option] = []

            values = self.options.get(option, '').split(',')
            values = [v.strip() for v in values]

            meta_information[option].extend(values)

        content_to_rst = StringList()
        for line in self.content:
            content_to_rst.append(line, self.name)
        node_need_content = nodes.paragraph()
        node_need_content.document = self.state.document

        container = MetaInfoNode(meta_information)
        for foo in node_need_content.children:
            container.append(foo)

        return [container]


directives.register_directive("aws-meta", ASCMetaDirective)


def dump(input_rst):
    doc = parse_rst(input_rst)
    visitor = MyVisitor(doc)
    doc.walk(visitor)
