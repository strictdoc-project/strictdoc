import functools
import os
import sys

from strictdoc.backend.dsl.models import Document
from strictdoc.backend.dsl.reader import SDReader
from strictdoc.core.document_tree import FileTree, DocumentTree
from strictdoc.helpers.sorting import alphanumeric_sort


class DocumentFinder:
    @staticmethod
    def find_sdoc_content(path_to_single_file_or_doc_root):
        if os.path.isfile(path_to_single_file_or_doc_root):
            raise NotImplemented
        if not os.path.isdir(path_to_single_file_or_doc_root):
            sys.stdout.flush()
            err = "error: Provided path is neither a single document or a document folder: '{}'".format(
                path_to_single_file_or_doc_root
            )
            print(err)
            exit(1)

        file_tree = DocumentFinder._build_file_tree(path_to_single_file_or_doc_root)
        document_tree = DocumentFinder._build_document_tree(file_tree)

        return document_tree

    @staticmethod
    def _build_document_tree(file_tree):
        reader = SDReader()

        document_list, document_map = [], {}

        task_list = [file_tree]
        while len(task_list) > 0:
            current_tree = task_list.pop(0)

            for doc_file in current_tree.files:
                doc_full_path = doc_file.get_full_path()

                document = reader.read_from_file(doc_full_path)
                assert isinstance(document, Document)
                document_list.append(document)
                document_map[doc_full_path] = document

            task_list.extend(current_tree.subfolder_trees)

        return DocumentTree(file_tree, document_list, document_map)

    @staticmethod
    def _build_file_tree(path_to_doc_root):
        root_tree = FileTree()
        file_tree_list = [root_tree]
        for root, dirs, files in os.walk(path_to_doc_root):
            current_tree = file_tree_list.pop(0)
            files.sort(key=alphanumeric_sort)
            dirs.sort(key=alphanumeric_sort)
            current_tree.set(root, files, dirs)
            file_tree_list.extend(current_tree.subfolder_trees)

        return root_tree
