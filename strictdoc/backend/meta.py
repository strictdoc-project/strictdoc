import os

from collections import OrderedDict

from docutils import nodes
from docutils.parsers.rst import Directive
from docutils.parsers.rst import directives
from docutils.statemachine import StringList

supported_categories = [
    'field1',
    'field2',
    'field3',
    'field4',
    'field5',
    'field6',
]

categories_spec = OrderedDict()

for category in supported_categories:
    categories_spec[category] = directives.unchanged_required


class MetaInfoNode(nodes.General, nodes.Element):
    meta_information = None

    def __init__(self, meta_information):
        assert meta_information
        super(MetaInfoNode, self).__init__()
        self.meta_information = meta_information

    def get_meta_information(self):
        return self.meta_information


class StdNodeDirective(Directive):
    has_content = True

    option_spec = categories_spec

    def run(self):
        meta_information = OrderedDict()

        if not self.options:
            raise SystemExit(1)

        for option in self.option_spec:
            if option not in self.options.keys():
                continue

            if option not in meta_information:
                meta_information[option] = []

            values = self.options.get(option, '').split(',')
            values = [v.strip() for v in values]

            meta_information[option].extend(values)

        paragraph_nodes = []

        current_paragraph_lines = []
        for line in self.content:
            print("----- line: {}".format(line))

            if line == '':
                node_text = nodes.Text('\n'.join(current_paragraph_lines))
                current_paragraph_lines.clear()
                node_paragraph = nodes.paragraph()
                node_paragraph.append(node_text)
                paragraph_nodes.append(node_paragraph)
                continue

            current_paragraph_lines.append(line)

        node_text = nodes.Text('\n'.join(current_paragraph_lines))
        node_paragraph = nodes.paragraph()
        node_paragraph.append(node_text)
        paragraph_nodes.append(node_paragraph)

        container = MetaInfoNode(meta_information)

        for paragraph_node in paragraph_nodes:
            container.append(paragraph_node)

        return [container]


directives.register_directive("std-node", StdNodeDirective)
