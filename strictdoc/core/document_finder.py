import os
import sys

from strictdoc.backend.dsl.models.document import Document
from strictdoc.backend.dsl.reader import SDReader
from strictdoc.core.document_meta import DocumentMeta
from strictdoc.core.document_tree import FileTree, DocumentTree, File
from strictdoc.helpers.sorting import alphanumeric_sort
from strictdoc.helpers.timing import measure_performance, timing_decorator


class DocumentFinder:
    @staticmethod
    @timing_decorator("Find")
    def find_sdoc_content(
        paths_to_files_or_docs, output_root_html, parallelizer
    ):
        for paths_to_files_or_doc in paths_to_files_or_docs:
            if not os.path.exists(paths_to_files_or_doc):
                sys.stdout.flush()
                err = "error: Provided path is neither a single file or a folder: '{}'".format(
                    paths_to_files_or_doc
                )
                print(err)
                exit(1)

        file_tree, asset_dirs = DocumentFinder._build_file_tree(
            paths_to_files_or_docs
        )
        document_tree = DocumentFinder._build_document_tree(
            file_tree, output_root_html, parallelizer
        )

        return document_tree, asset_dirs

    @staticmethod
    def _iterate_file_trees(file_trees):
        for file_tree in file_trees:
            task_list = [file_tree]

            file_tree_mount_folder = file_tree.mount_folder()
            while len(task_list) > 0:
                current_tree = task_list.pop(0)

                for doc_file in current_tree.files:
                    yield file_tree, doc_file, file_tree_mount_folder

                task_list.extend(current_tree.subfolder_trees)

    @staticmethod
    def processing(document_triple):
        file_tree, doc_file, file_tree_mount_folder = document_triple
        doc_full_path = doc_file.get_full_path()

        with measure_performance(
            "Reading SDOC: {}".format(os.path.basename(doc_full_path))
        ):
            reader = SDReader()
            document = reader.read_from_file(doc_full_path)
            assert isinstance(document, Document)

        document._tx_parser = None
        document._tx_attrs = None
        document._tx_metamodel = None
        document._tx_peg_rule = None
        document._tx_model_params = None
        return doc_file, document

    @staticmethod
    def _build_document_tree(file_trees, output_root_html, parallelizer):
        assert isinstance(file_trees, list)
        document_list, map_docs_by_paths, map_relpaths_by_docs = [], {}, {}

        file_tree_list = list(DocumentFinder._iterate_file_trees(file_trees))
        found_documents = parallelizer.map(
            file_tree_list, DocumentFinder.processing
        )

        for doc_file, document in found_documents:
            input_doc_full_path = doc_file.get_full_path()
            map_docs_by_paths[input_doc_full_path] = document
            document_list.append(document)

        for file_tree, doc_file, file_tree_mount_folder in file_tree_list:
            input_doc_full_path = doc_file.get_full_path()
            document = map_docs_by_paths[input_doc_full_path]
            assert isinstance(document, Document)

            doc_relative_path = os.path.relpath(
                input_doc_full_path, file_tree.root_path
            )
            doc_relative_path_folder = os.path.dirname(doc_relative_path)

            output_document_dir_rel_path = (
                "{}/{}".format(file_tree_mount_folder, doc_relative_path_folder)
                if doc_relative_path_folder
                else file_tree_mount_folder
            )

            document_filename = os.path.basename(input_doc_full_path)
            document_filename_base = os.path.splitext(document_filename)[0]

            output_document_dir_full_path = "{}/{}".format(
                output_root_html, output_document_dir_rel_path
            )

            document_meta = DocumentMeta(
                doc_file.level,
                document_filename_base,
                input_doc_full_path,
                doc_relative_path_folder,
                output_document_dir_full_path,
                output_document_dir_rel_path,
            )

            document.assign_meta(document_meta)

            map_docs_by_paths[input_doc_full_path] = document

        return DocumentTree(file_trees, document_list, map_docs_by_paths)

    @staticmethod
    def _build_file_tree(paths_to_files_or_docs):
        asset_dirs = []
        root_trees = []

        for path_to_doc_root_raw in paths_to_files_or_docs:
            if os.path.isfile(path_to_doc_root_raw):
                path_to_doc_root = path_to_doc_root_raw
                if not os.path.isabs(path_to_doc_root):
                    path_to_doc_root = os.path.abspath(path_to_doc_root)

                parent_dir = os.path.dirname(path_to_doc_root)
                path_to_doc_root_base = os.path.dirname(parent_dir)

                assets_dir = os.path.join(parent_dir, "_assets")
                if os.path.isdir(assets_dir):
                    asset_dirs.append(
                        {
                            "full_path": assets_dir,
                            "relative_path": os.path.relpath(
                                assets_dir, path_to_doc_root_base
                            ),
                        }
                    )
                root_trees.append(File(0, path_to_doc_root))
                continue

            # Strip away the trailing slash to let the later os.path.relpath
            # calculations work correctly.
            path_to_doc_root = path_to_doc_root_raw.rstrip("/")
            path_to_doc_root = os.path.abspath(path_to_doc_root)
            path_to_doc_root_base = os.path.dirname(path_to_doc_root)
            root_level = path_to_doc_root.count(os.sep)

            tree_map = {path_to_doc_root: FileTree(path_to_doc_root, 0)}

            for current_root_path, dirs, files in os.walk(
                path_to_doc_root, topdown=False
            ):
                if os.path.basename(current_root_path) == "_assets":
                    asset_dirs.append(
                        {
                            "full_path": current_root_path,
                            "relative_path": os.path.relpath(
                                current_root_path, path_to_doc_root_base
                            ),
                        }
                    )

                current_root_path_level = (
                    current_root_path.count(os.sep) - root_level
                )

                if current_root_path not in tree_map:
                    tree_map[current_root_path] = FileTree(
                        current_root_path, current_root_path_level
                    )
                current_tree = tree_map[current_root_path]

                current_tree.sort_subfolder_trees()

                files = [f for f in files if f.endswith(".sdoc")]
                files.sort(key=alphanumeric_sort)
                current_tree.set(files)
                if not current_tree.has_sdoc_content and len(files) > 0:
                    current_tree.has_sdoc_content = True

                if current_root_path == path_to_doc_root:
                    continue

                current_parent_path = os.path.dirname(current_root_path)
                if current_parent_path not in tree_map:
                    tree_map[current_parent_path] = FileTree(
                        current_parent_path, current_root_path_level - 1
                    )
                current_parent_tree = tree_map[current_parent_path]
                if len(files) > 0 or current_tree.has_sdoc_content:
                    current_parent_tree.has_sdoc_content = True

                current_parent_tree.add_subfolder_tree(current_tree)

            root_trees.append(tree_map[path_to_doc_root])
        return root_trees, asset_dirs
