import docutils
from docutils.nodes import NodeVisitor

from strictdoc.backend.rst.meta import MetaInfoNode


class HTMLWriteVisitor(NodeVisitor):
    output = None

    level = 0

    def __init__(self, document):
        super(HTMLWriteVisitor, self).__init__(document)

        self.output = []
        self.level = 0

    def unknown_visit(self, node: docutils.nodes.Node) -> None:
        """Called for all other node types."""
        print("unknown_visit:")

        print(type(node))
        print(node.pformat())

        if isinstance(node, docutils.nodes.document):
            return

        if isinstance(node, docutils.nodes.section):
            self.level += 1
            return

        if isinstance(node, docutils.nodes.title):
            text = node.astext()

            self.output.append('')

            if self.level == 1:
                self.output.append('<h1>{}</h1>'.format(text))
            elif self.level == 2:
                self.output.append('<h2>{}</h2>'.format(text))
            elif self.level == 3:
                self.output.append('<h3>{}</h3>'.format(text))
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

            self.level -= 1

            return

        return

    def get_output(self):
        self.output.append('')

        return '\n'.join(self.output).lstrip()


class HTMLWriter:
    @staticmethod
    def create_new_doc():
        components = (docutils.parsers.rst.Parser,)
        settings = docutils.frontend.OptionParser(components=components).get_default_values()

        document = docutils.utils.new_document('<rst-doc>', settings=settings)
        return document

    def write_document(self, rst_document):
        visitor = HTMLWriteVisitor(rst_document)
        rst_document.walkabout(visitor)

        html_output = visitor.get_output()

        return html_output

    def write_fragment(self, rst_fragment):
        print(rst_fragment)
        print(type(rst_fragment))

        children = []
        if isinstance(rst_fragment, list):
            for node in rst_fragment:
                children.append(node.deepcopy())
        else:
            children.append(rst_fragment)

        document_wrapper = HTMLWriter.create_new_doc()
        document_wrapper.children = children

        return self.write_document(document_wrapper)
