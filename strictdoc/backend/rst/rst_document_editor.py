import docutils
from docutils.nodes import Node

from strictdoc.backend.rst.rst_constants import STRICTDOC_ATTR_LEVEL
from strictdoc.backend.rst.rst_document_validator import RSTDocumentValidator
from strictdoc.backend.rst.rst_node_finder import RSTNodeFinder
from strictdoc.backend.rst.rst_parser import RSTParser
from strictdoc.backend.rst.rst_reader import RSTReadVisitor


class RSTDocumentEditor:
    def __init__(self, rst_document):
        assert rst_document
        self.rst_document = rst_document
        self.validator = RSTDocumentValidator()

    def replace_node(self, node, new_rst_fragment):
        print("RSTDocumentEditor.replace_node:\nreplace node:\n{}\nwith:\n{}".format(node, new_rst_fragment))
        assert isinstance(node, docutils.nodes.Node)

        print("document before injection:")
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
                self._replace_section_with_paragraph(node,
                                                     top_level_node)
            elif isinstance(top_level_node, docutils.nodes.section):
                self._replace_section_with_section(node, top_level_node)
            else:
                raise NotImplementedError
        elif isinstance(node, docutils.nodes.paragraph):
            if isinstance(top_level_node, docutils.nodes.section):
                self._replace_paragraph_with_section(node, top_level_node)
            else:
                raise NotImplementedError
        else:
            raise NotImplementedError

        self.validator.validate_rst_document(self.rst_document.rst_document)

        visitor = RSTReadVisitor(self.rst_document.rst_document)
        self.rst_document.rst_document.walkabout(visitor)

        print(self.rst_document.rst_document.pformat())

        self.rst_document.lines = visitor.get_lines()

    @staticmethod
    def _replace_section_with_paragraph(section_title, paragraph):
        assert isinstance(section_title, docutils.nodes.title)
        assert isinstance(section_title.parent, docutils.nodes.section)
        assert isinstance(paragraph, docutils.nodes.paragraph)
        section_to_be_removed = section_title.parent
        section_to_be_removed.remove(section_title)

        orphan_children = section_to_be_removed.children

        (new_parent, injection_idx) = RSTNodeFinder.find_new_parent(section_to_be_removed, 10)

        section_to_be_removed.parent.remove(section_to_be_removed)
        if injection_idx != -1:
            new_parent.insert(injection_idx, paragraph)
        else:
            new_parent.append(paragraph)

        for child_idx, child in enumerate(orphan_children):
            if injection_idx != -1:
                new_parent.insert(injection_idx + 1 + child_idx, child)
            else:
                new_parent.append(child)

    @staticmethod
    def _replace_section_with_section(old_section_title, new_section):
        assert isinstance(old_section_title, docutils.nodes.title)
        assert isinstance(new_section, docutils.nodes.section)

        old_section = old_section_title.parent
        current_level = old_section[STRICTDOC_ATTR_LEVEL]
        new_level = new_section[STRICTDOC_ATTR_LEVEL]

        if new_level == current_level:
            title_node = new_section.children[0]
            assert isinstance(title_node, docutils.nodes.title)
            old_section.replace(old_section_title, title_node)
            return

        if new_level > current_level:
            split_section_index = None
            for index, child in enumerate(old_section):
                if isinstance(child, docutils.nodes.section):
                    if child[STRICTDOC_ATTR_LEVEL] <= new_level:
                        split_section_index = index
                        break

            orphan_children = []
            if split_section_index:
                for child in old_section[split_section_index:]:
                    orphan_children.append(child)

            old_section_parent = old_section.parent

            (new_parent, insert_index) = RSTNodeFinder.find_new_parent(
                old_section, new_level
            )

            if insert_index == -1:
                new_parent.append(old_section)
            else:
                new_parent.insert(insert_index + 1, old_section)

            old_section[STRICTDOC_ATTR_LEVEL] = new_level
            old_section.children[0].replace_self(new_section.children[0])
            old_section_parent.remove(old_section)

            if orphan_children:
                new_parent_section, insert_index = RSTNodeFinder.find_new_parent(
                    orphan_children[0], current_level + 1
                )

                for child in orphan_children:
                    child.parent.remove(child)
                    if insert_index == -1:
                        new_parent_section.append(child)
                    else:
                        new_parent_section.insert(insert_index, child)
        else:
            new_section_parent_section = \
                RSTNodeFinder.find_parent_of_level(old_section,
                                                   new_level)

            new_parent_section = new_section_parent_section.parent

            moving_children = []
            cursor = old_section
            while (cursor != old_section.document and
                   cursor[STRICTDOC_ATTR_LEVEL] > new_level):
                split_index = cursor.parent.index(cursor)

                for moving_child in cursor.parent[split_index + 1:]:
                    moving_children.append(moving_child)
                    cursor.parent.remove(moving_child)
                cursor = cursor.parent

            branch_index = new_parent_section.index(new_section_parent_section)

            old_section.parent.remove(old_section)
            old_section[STRICTDOC_ATTR_LEVEL] = new_level
            old_section.children[0].replace_self(new_section.children[0])

            new_parent_section.insert(branch_index + 1, old_section)
            for moving_child in moving_children:
                old_section.append(moving_child)

    @staticmethod
    def _replace_paragraph_with_section(old_paragraph, new_section):
        old_parent = old_paragraph.parent
        split_index = old_parent.index(old_paragraph)

        old_level = old_parent[STRICTDOC_ATTR_LEVEL]
        new_level = new_section[STRICTDOC_ATTR_LEVEL]

        # Step: When a paragraph becomes a new section, it inherits all children
        # which are of higher level.
        moving_children = []
        for old_parent_child in old_parent[split_index + 1:]:
            if (isinstance(old_parent_child, docutils.nodes.section) and
                    old_parent_child[STRICTDOC_ATTR_LEVEL] <= new_level):
                break
            moving_children.append(old_parent_child)
            old_parent.remove(old_parent_child)

        if new_level > old_level:
            old_paragraph.parent.replace(old_paragraph, new_section)
            for moving_child in moving_children:
                new_section.append(moving_child)
        else:
            old_top_level_parent = RSTNodeFinder.find_parent_of_level(
                old_paragraph.parent, new_level
            )
            new_parent = old_top_level_parent.parent

            old_paragraph.parent.remove(old_paragraph)
            idx = new_parent.index(old_top_level_parent)

            new_parent.insert(idx + 1, new_section)
            for moving_child in moving_children:
                new_section.append(moving_child)
