import collections
from typing import Iterator

from strictdoc.core.document_tree import DocumentTree
from strictdoc.core.file_tree import File, FileOrFolderEntry, Folder


class DocumentTreeIterator:
    def __init__(self, document_tree: DocumentTree) -> None:
        assert isinstance(document_tree, DocumentTree)
        self.document_tree: DocumentTree = document_tree

    def is_empty_tree(self) -> bool:
        return len(self.document_tree.document_list) == 0

    def iterator_files_first(self) -> Iterator[FileOrFolderEntry]:
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
            else:  # pragma: no cover
                raise AssertionError
