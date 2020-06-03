import docutils

from docutils.nodes import Node, section

from strictdoc.backend.rst.rst_constants import STRICTDOC_ATTR_LEVEL
from strictdoc.backend.rst.rst_reader import RSTReadVisitor
from strictdoc.backend.rst.rst_parser import RSTParser


class RSTDocumentEditor:
    rst_document = None

    def __init__(self, rst_document):
        assert rst_document
        self.rst_document = rst_document

    def replace_node(self, node, new_rst_fragment):
        print("RSTDocumentEditor.replace_node:\nreplace node:\n{}\nwith:\n{}".format(node, new_rst_fragment))
        assert isinstance(node, docutils.nodes.Node)

        print("before injection:")
        print(self.rst_document.rst_document.pformat())

        new_fragment_rst_doc = RSTParser.parse_rst(new_rst_fragment)
        print(new_fragment_rst_doc)

        visitor = RSTReadVisitor(new_fragment_rst_doc, new_rst_fragment)
        new_fragment_rst_doc.walkabout(visitor)

        print("new_rst_fragment:\n{}".format(new_rst_fragment))
        top_level_node = new_fragment_rst_doc.children[0]
        assert top_level_node

        if isinstance(node, docutils.nodes.title):
            if isinstance(top_level_node, docutils.nodes.paragraph):
                assert isinstance(node.parent, docutils.nodes.section)
                section_to_be_removed = node.parent
                section_to_be_removed.remove(node)

                orphan_children = section_to_be_removed.children

                new_parent = node.parent.parent

                injection_idx = new_parent.index(section_to_be_removed) + 1

                new_parent.replace(section_to_be_removed, top_level_node)

                for child_idx, child in enumerate(orphan_children):
                    new_parent.insert(injection_idx + child_idx, child)
            elif isinstance(top_level_node, docutils.nodes.section):
                title_node = top_level_node.children[0]
                assert isinstance(title_node, docutils.nodes.title)
                node.parent.replace(node, title_node)
            else:
                assert 0, "Should not reach here"
        elif isinstance(node, docutils.nodes.paragraph):
            if isinstance(top_level_node, docutils.nodes.section):
                node.parent.replace(node, top_level_node)
            else:
                assert 0, "Should not reach here"
        else:
            assert 0, "Should not reach here"

        visitor = RSTReadVisitor(self.rst_document.rst_document)
        self.rst_document.rst_document.walkabout(visitor)

        print("after injection:")
        print(self.rst_document.rst_document.pformat())

        self.rst_document.lines = visitor.get_lines()
        print("new lines: {}".format(self.rst_document.lines))
