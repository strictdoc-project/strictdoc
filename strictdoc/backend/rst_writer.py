# TODO: create something like this later:
# https://github.com/sphinx-contrib/restbuilder
# https://stackoverflow.com/questions/19523151/is-there-a-way-to-create-an-intermediate-output-from-sphinx-extensions/19526851#19526851
# also this: https://stackoverflow.com/questions/61666809/parse-and-write-rst-using-docutils

import docutils
from docutils.nodes import NodeVisitor

from strictdoc.backend.meta import MetaInfoNode

class RSTWriteVisitor(NodeVisitor):
    output = []

    level = 0

    def unknown_visit(self, node: docutils.nodes.Node) -> None:
        """Called for all other node types."""
        # print("unknown_visit:")
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
            text = node.astext()
            self.output.append(text)
            if self.level == 1:
                self.output.append('='.ljust(len(text), '='))
            elif self.level == 2:
                self.output.append('-'.ljust(len(text), '-'))

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


def write_rst(rstdoc):
    visitor = RSTWriteVisitor(rstdoc)
    rstdoc.walkabout(visitor)

    return visitor.get_output()

