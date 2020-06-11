import docutils
from docutils.nodes import NodeVisitor

from strictdoc.backend.rst.meta import MetaInfoNode
from strictdoc.backend.rst.rst_constants import STRICTDOC_ATTR_LEVEL


class HTMLWriteVisitor(NodeVisitor):
    def __init__(self, document):
        super(HTMLWriteVisitor, self).__init__(document)

        self.output = []

    def unknown_visit(self, node: docutils.nodes.Node) -> None:
        """Called for all other node types."""
        print("HTMLWriteVisitor.unknown_visit:")

        print(type(node))
        print(node.pformat())

        if isinstance(node, docutils.nodes.document):
            return

        if isinstance(node, docutils.nodes.section):
            return

        if isinstance(node, docutils.nodes.title):
            assert isinstance(node.parent, docutils.nodes.section)
            assert node.parent.hasattr(STRICTDOC_ATTR_LEVEL)

            level = node.parent[STRICTDOC_ATTR_LEVEL]

            text = node.astext()

            self.output.append('')

            if level == 1:
                self.output.append('<h1>{}</h1>'.format(text))
            elif level == 2:
                self.output.append('<h2>{}</h2>'.format(text))
            elif level == 3:
                self.output.append('<h3>{}</h3>'.format(text))
            elif level == 4:
                self.output.append('<h4>{}</h4>'.format(text))
            return

        if isinstance(node, docutils.nodes.paragraph):
            self.output.append('')

            text = ''
            if isinstance(node.parent, MetaInfoNode):
                for child in node.children:
                    lines = child.astext().splitlines()

                    text = '\n'.join('    ' + line for line in lines)
            else:
                for child in node.children:
                    if isinstance(child, docutils.nodes.Text):
                        text += child.astext()
            if len(text) > 0:
                self.output.append(text)

            return

        if isinstance(node, docutils.nodes.Text):
            return

        if isinstance(node, MetaInfoNode):
            self.output.append('')

            self.output.append('.. std-node::')

            for field in node.meta_information:
                values = ', '.join(node.meta_information[field])
                self.output.append('    :{}: {}'.format(field, values))

            return

        if isinstance(node, docutils.nodes.reference):
            url = node.get('refuri')
            text = node.astext()

            link = '<a href="{url}">{text}</a>'.format(url=url, text=text)
            self.output.append(link)

            return

        return

    def unknown_departure(self, node):
        if isinstance(node, docutils.nodes.section):
            print("departure section: {}".format(node))
            return

        return

    def get_output(self):
        self.output.append('')

        return '\n'.join(self.output).lstrip()
