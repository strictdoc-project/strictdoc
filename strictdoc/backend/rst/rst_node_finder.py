import docutils.nodes

from strictdoc.backend.rst.rst_constants import STRICTDOC_ATTR_LEVEL

LEVEL_MAX = 1000

class RSTNodeFinder:
    @staticmethod
    def find_new_parent(root, new_level):
        assert isinstance(root, docutils.nodes.section)
        indexes = {}

        cursor = root
        while cursor:
            parent = cursor.parent
            if not parent:
                return cursor, indexes[cursor]

            index = parent.index(cursor)
            indexes[cursor.parent] = index

            for child in reversed(parent[:index + 1]):
                if child == root:
                    continue

                if isinstance(child, docutils.nodes.section):
                    if child[STRICTDOC_ATTR_LEVEL] < new_level:
                        # A match node is found but we want to check if it maybe
                        # has even more matching children.
                        child_cursor = child
                        while child_cursor:

                            # We might be digging into the same level where the
                            # root is located. In this case we only want to
                            # reverse-iterate everyone before the root.
                            index = child_cursor.index(root) \
                                if child_cursor == root.parent \
                                else len(child_cursor.children) - 1

                            for idx, child_child in enumerate(reversed(child_cursor.children[:index + 1])):
                                if not isinstance(child_child, docutils.nodes.section):
                                    continue
                                if child_child == root:
                                    continue
                                if child_child[STRICTDOC_ATTR_LEVEL] < new_level:
                                    child_cursor = child_child
                                    break
                            else:
                                break
                        return child_cursor, -1
            else:
                if isinstance(cursor, docutils.nodes.document):
                    return cursor, indexes[cursor]
                if new_level == LEVEL_MAX and parent[STRICTDOC_ATTR_LEVEL] < new_level:
                    return parent, index

                cursor = cursor.parent
        return cursor, indexes[cursor]

    @staticmethod
    def find_parent_of_level(root, level):
        assert isinstance(root, docutils.nodes.section)

        cursor = root
        while cursor[STRICTDOC_ATTR_LEVEL] > level:
            if cursor.parent == root.document:
                return cursor
            cursor = cursor.parent

        return cursor

