from collections import OrderedDict

from docutils import nodes
from docutils.parsers.rst import Directive

from saturn.backend.rst.directives.document_metadata import DocumentMetadataNode
from saturn.backend.rst.rst_parser_shared_state import RSTParserSharedState


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

    option_spec = RSTParserSharedState.categories_spec

    def run(self):
        meta_information = OrderedDict()

        if not self.options:
            raise RuntimeError("problem with options")

        document_metadata_node = self.state_machine.document.children[0]
        assert isinstance(document_metadata_node, DocumentMetadataNode)

        document_metadata = document_metadata_node.get_metadata()

        for option in self.option_spec:
            if option not in self.options.keys():
                continue

            if not document_metadata.has_field(option, 'string'):
                raise RuntimeError("Wrong field: {}".format(option))

            # for array types
            # if option not in meta_information:
            #     meta_information[option] = []
            # values = self.options.get(option, '').split(',')
            value = self.options.get(option, '')

            meta_information[option] = value

        paragraph_nodes = []

        current_paragraph_lines = []
        for line in self.content:
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
