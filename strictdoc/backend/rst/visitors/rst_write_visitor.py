import docutils
from docutils.nodes import NodeVisitor

from strictdoc.backend.rst.meta import MetaInfoNode
from strictdoc.backend.rst.rst_constants import STRICTDOC_ATTR_LEVEL


class RSTWriteVisitor(NodeVisitor):
    output = []

    level = 0

    def __init__(self, document):
        super(RSTWriteVisitor, self).__init__(document)
        self.output = []
        self.level = 0

    def unknown_visit(self, node: docutils.nodes.Node) -> None:
        """Called for all other node types."""
        print("RSTWriteVisitor.unknown_visit:")
        print(type(node))
        print(node.astext())

        if isinstance(node, docutils.nodes.document):
            return

        if isinstance(node, docutils.nodes.section):
            self.level += 1
            print("visit section: {}".format(node))
            return

        if isinstance(node, docutils.nodes.title):
            print("visit title: {}".format(node))
            assert isinstance(node.parent, docutils.nodes.section)
            assert node.parent.hasattr(STRICTDOC_ATTR_LEVEL)

            level = node.parent[STRICTDOC_ATTR_LEVEL]

            text = node.astext()

            self.output.append(text)
            if level == 1:
                self.output.append('='.ljust(len(text), '='))
            elif level == 2:
                self.output.append('-'.ljust(len(text), '-'))
            elif level == 3:
                self.output.append('~'.ljust(len(text), '~'))

            self.output.append('')

            return

        if isinstance(node, docutils.nodes.paragraph):
            print("visit paragraph: {}".format(node))

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
            print("visit Text: {}".format(node))
            return

        if isinstance(node, MetaInfoNode):
            print("visit MetaInfoNode: {}".format(node))
            self.output.append('.. std-node::')

            for field in node.meta_information:
                values = ', '.join(node.meta_information[field])

                self.output.append('    :{}: {}'.format(field, values))

            self.output.append('')

            return

        return

    def unknown_departure(self, node):
        if isinstance(node, docutils.nodes.section):
            print("departure section: {}".format(node))

            self.level -= 1

            return

        return

    def get_output(self):
        return '\n'.join(self.output)
