# mypy: disable-error-code="no-untyped-def"
import collections

from strictdoc.core.document_tree import DocumentTree
from strictdoc.core.file_tree import File, Folder


class DocumentTreeIterator:
    def __init__(self, document_tree) -> None:
        assert isinstance(document_tree, DocumentTree)
        self.document_tree: DocumentTree = document_tree

    def is_empty_tree(self):
        return len(self.document_tree.document_list) == 0

    def iterator(self):
        task_list = collections.deque(
            map(
                lambda tree: tree.root_folder_or_file,
                self.document_tree.file_tree,
            )
        )

        while task_list:
            file_tree_or_file = task_list.popleft()
            if isinstance(file_tree_or_file, File):
                yield file_tree_or_file
            elif isinstance(file_tree_or_file, Folder):
                if not file_tree_or_file.has_sdoc_content:
                    continue
                yield file_tree_or_file
                task_list.extendleft(reversed(file_tree_or_file.files))
                task_list.extendleft(
                    reversed(file_tree_or_file.subfolder_trees)
                )

    def iterator_files_first(self):
        task_list = collections.deque(
            map(
                lambda tree: tree.root_folder_or_file,
                self.document_tree.file_tree,
            )
        )

        while task_list:
            file_tree_or_file = task_list.popleft()
            if isinstance(file_tree_or_file, File):
                yield file_tree_or_file
            elif isinstance(file_tree_or_file, Folder):
                if not file_tree_or_file.has_sdoc_content:
                    continue
                yield file_tree_or_file
                task_list.extendleft(
                    reversed(file_tree_or_file.subfolder_trees)
                )
                task_list.extendleft(reversed(file_tree_or_file.files))
