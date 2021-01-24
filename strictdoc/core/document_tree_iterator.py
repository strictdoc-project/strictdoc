import collections

from strictdoc.core.document_tree import FileTree, DocumentTree, File


class DocumentTreeIterator:
    def __init__(self, document_tree):
        assert isinstance(document_tree, DocumentTree)
        self.document_tree = document_tree

    def iterator(self):
        task_list = collections.deque(self.document_tree.file_tree)

        while task_list:
            file_tree_or_file = task_list.popleft()
            if isinstance(file_tree_or_file, File):
                yield file_tree_or_file
            elif isinstance(file_tree_or_file, FileTree):
                if not file_tree_or_file.has_sdoc_content:
                    continue
                yield file_tree_or_file
                task_list.extendleft(reversed(file_tree_or_file.files))
                task_list.extendleft(
                    reversed(file_tree_or_file.subfolder_trees)
                )
