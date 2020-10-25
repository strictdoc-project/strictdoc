import docutils
from docutils.nodes import NodeVisitor

from saturn.backend.rst.directives.document_metadata import DocumentMetadataNode
from saturn.backend.rst.directives.metadata import MetaInfoNode
from saturn.backend.rst.rst_constants import SATURN_ATTR_LEVEL
from saturn.core.logger import Logger


class RSTWriteVisitor(NodeVisitor):
    logger = Logger("RSTWriteVisitor")

    def __init__(self, document):
        super(RSTWriteVisitor, self).__init__(document)
        self.output = []

    def unknown_visit(self, node: docutils.nodes.Node) -> None:
        """Called for all other node types."""
        self.logger.info(node.astext())

        if isinstance(node, docutils.nodes.document):
            return

        if isinstance(node, docutils.nodes.section):
            return

        if isinstance(node, docutils.nodes.title):
            assert isinstance(node.parent, docutils.nodes.section)
            assert node.parent.hasattr(SATURN_ATTR_LEVEL)

            level = node.parent[SATURN_ATTR_LEVEL]

            text = node.astext()

            self.output.append(text)
            if level == 1:
                self.output.append('='.ljust(len(text), '='))
            elif level == 2:
                self.output.append('-'.ljust(len(text), '-'))
            elif level == 3:
                self.output.append('~'.ljust(len(text), '~'))
            elif level == 4:
                self.output.append('^'.ljust(len(text), '^'))

            self.output.append('')

            return

        if isinstance(node, docutils.nodes.paragraph):
            if isinstance(node.parent, MetaInfoNode):
                for child in node.children:
                    lines = child.astext().splitlines()

                    text = '\n'.join('    ' + line for line in lines)
            else:
                text = node.astext()

            self.output.append(text)
            self.output.append('')

            return

        if isinstance(node, docutils.nodes.Text):
            return

        if isinstance(node, MetaInfoNode):
            self.output.append('.. metadata::')

            for field in node.meta_information:
                values = node.meta_information[field]

                self.output.append('    :{}: {}'.format(field, values))

            self.output.append('')

            return

        if isinstance(node, DocumentMetadataNode):
            self.output.append('.. document-metadata::')

            document_metadata = node.get_metadata()
            self.output.append('    :fields:')
            for field in document_metadata.fields:
                self.output.append('        - name={}, type={}'.format(field['name'], field['type']))

            self.output.append('')

            return

        return

    def unknown_departure(self, node):
        if isinstance(node, docutils.nodes.section):
            return

        return

    def get_output(self):
        return '\n'.join(self.output)
