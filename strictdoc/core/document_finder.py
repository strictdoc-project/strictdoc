import datetime
import functools
import os
import sys
import time

from strictdoc.backend.dsl.models import Document
from strictdoc.backend.dsl.reader import SDReader
from strictdoc.core.document_meta import DocumentMeta
from strictdoc.core.document_tree import FileTree, DocumentTree
from strictdoc.helpers.sorting import alphanumeric_sort


class DocumentFinder:
    @staticmethod
    def find_sdoc_content(paths_to_files_or_docs, output_root_html):
        for paths_to_files_or_doc in paths_to_files_or_docs:
            if os.path.isfile(paths_to_files_or_doc):
                raise NotImplementedError
            if not os.path.isdir(paths_to_files_or_doc):
                sys.stdout.flush()
                err = "error: Provided path is neither a single document or a document folder: '{}'".format(
                    paths_to_files_or_doc
                )
                print(err)
                exit(1)

        file_tree, asset_dirs = DocumentFinder._build_file_tree(paths_to_files_or_docs)
        document_tree = DocumentFinder._build_document_tree(file_tree,
                                                            output_root_html)

        return document_tree, asset_dirs

    @staticmethod
    def _build_document_tree(file_trees, output_root_html):
        assert isinstance(file_trees, list)
        reader = SDReader()

        document_list, map_docs_by_paths, map_relpaths_by_docs = [], {}, {}

        for file_tree in file_trees:
            task_list = [file_tree]

            file_tree_mount_folder = os.path.basename(file_tree.root_path)

            while len(task_list) > 0:
                current_tree = task_list.pop(0)

                for doc_file in current_tree.files:
                    doc_full_path = doc_file.get_full_path()
                    document = reader.read_from_file(doc_full_path)
                    assert isinstance(document, Document)
                    document_list.append(document)

                    doc_relative_path = os.path.relpath(doc_full_path, file_tree.root_path)
                    doc_relative_path_folder = os.path.dirname(doc_relative_path)

                    document_relpath_folder = '{}/{}'.format(
                        file_tree_mount_folder,
                        doc_relative_path_folder
                    ) if doc_relative_path_folder else file_tree_mount_folder

                    document_filename = os.path.basename(doc_full_path)
                    document_filename_base = os.path.splitext(document_filename)[0]

                    document_full_html_out_path = '{}/{}'.format(
                        output_root_html, document_relpath_folder
                    )

                    document_meta = DocumentMeta(doc_file.level,
                                                 doc_full_path,
                                                 document_full_html_out_path,
                                                 document_relpath_folder,
                                                 document_filename_base)

                    document.assign_meta(document_meta)

                    map_docs_by_paths[doc_full_path] = document
                task_list.extend(current_tree.subfolder_trees)

        return DocumentTree(file_trees,
                            document_list,
                            map_docs_by_paths)

    @staticmethod
    def _build_file_tree(paths_to_files_or_docs):
        asset_dirs = []
        root_trees = []

        for path_to_doc_root in paths_to_files_or_docs:
            path_to_doc_root_base = os.path.dirname(path_to_doc_root)
            root_level = path_to_doc_root.count(os.sep)

            tree_map = {path_to_doc_root: FileTree(path_to_doc_root, 0)}

            for current_root_path, dirs, files in os.walk(path_to_doc_root, topdown=False):
                if os.path.basename(current_root_path) == '_assets':
                    asset_dirs.append({
                        'full_path': current_root_path,
                        'relative_path': os.path.relpath(current_root_path, path_to_doc_root_base)
                    })

                current_root_path_level = current_root_path.count(os.sep) - root_level

                if current_root_path not in tree_map:
                    tree_map[current_root_path] = FileTree(current_root_path, current_root_path_level)
                current_tree = tree_map[current_root_path]

                current_tree.sort_subfolder_trees()

                files = [f for f in files if f.endswith('.sdoc')]
                if len(files) > 0:
                    files.sort(key=alphanumeric_sort)
                    current_tree.set(files)

                    if current_root_path == path_to_doc_root:
                        continue

                    current_parent_path = os.path.dirname(current_root_path)
                    if current_parent_path not in tree_map:
                        tree_map[current_parent_path] = FileTree(current_parent_path, current_root_path_level - 1)
                    current_parent_tree = tree_map[current_parent_path]
                    current_parent_tree.add_subfolder_tree(current_tree)

            root_trees.append(tree_map[path_to_doc_root])
        return root_trees, asset_dirs
