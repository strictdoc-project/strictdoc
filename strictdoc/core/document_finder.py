import os
import sys

from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.reader import SDReader
from strictdoc.cli.cli_arg_parser import ExportCommandConfig
from strictdoc.core.document_meta import DocumentMeta
from strictdoc.core.document_tree import DocumentTree
from strictdoc.core.file_tree import (
    FileTree,
    FileFinder,
    PathFinder,
)
from strictdoc.helpers.textx import drop_textx_meta
from strictdoc.helpers.timing import measure_performance, timing_decorator


class DocumentFinder:
    @staticmethod
    @timing_decorator("Find and read SDoc files")
    def find_sdoc_content(config: ExportCommandConfig, parallelizer):
        for paths_to_files_or_doc in config.input_paths:
            if not os.path.exists(paths_to_files_or_doc):
                sys.stdout.flush()
                err = (
                    "error: "
                    "Provided path is neither a single file or a folder: "
                    f"'{paths_to_files_or_doc}'"
                )
                print(err)
                sys.exit(1)

        file_tree, asset_dirs = DocumentFinder._build_file_tree(config)
        document_tree = DocumentFinder._build_document_tree(
            file_tree, config.output_html_root, parallelizer
        )

        return document_tree, asset_dirs

    @staticmethod
    def _process_worker_parse_document(document_triple):
        _, doc_file, _ = document_triple
        doc_full_path = doc_file.get_full_path()

        with measure_performance(
            f"Reading SDOC: {os.path.basename(doc_full_path)}"
        ):
            reader = SDReader()
            document = reader.read_from_file(doc_full_path)
            assert isinstance(document, Document)

        drop_textx_meta(document)
        return doc_file, document

    @staticmethod
    def _build_document_tree(file_trees, output_root_html, parallelizer):
        assert isinstance(file_trees, list)
        document_list, map_docs_by_paths = [], {}

        file_tree_list = []
        for file_tree in file_trees:
            file_tree_list.extend(list(file_tree.iterate()))

        found_documents = parallelizer.map(
            file_tree_list, DocumentFinder._process_worker_parse_document
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
                f"{file_tree_mount_folder}/{doc_relative_path_folder}"
                if doc_relative_path_folder
                else file_tree_mount_folder
            )

            document_filename = os.path.basename(input_doc_full_path)
            document_filename_base = os.path.splitext(document_filename)[0]

            output_document_dir_full_path = (
                f"{output_root_html}/{output_document_dir_rel_path}"
            )

            document_meta = DocumentMeta(
                doc_file.level,
                file_tree_mount_folder,
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
    def _build_file_tree(config: ExportCommandConfig):
        asset_dirs = []
        root_trees = []

        for path_to_doc_root_raw in config.input_paths:
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
                root_trees.append(
                    FileTree.create_single_file_tree(path_to_doc_root)
                )
                continue

            # Strip away the trailing slash to let the later os.path.relpath
            # calculations work correctly.
            path_to_doc_root = path_to_doc_root_raw.rstrip("/")
            path_to_doc_root = os.path.abspath(path_to_doc_root)
            path_to_doc_root_base = os.path.dirname(path_to_doc_root)

            # Finding assets.
            tree_asset_dirs = PathFinder.find_directories(
                path_to_doc_root, "_assets"
            )
            for asset_dir in tree_asset_dirs:
                asset_dirs.append(
                    {
                        "full_path": asset_dir,
                        "relative_path": os.path.relpath(
                            asset_dir, path_to_doc_root_base
                        ),
                    }
                )

            # Finding SDoc files.
            file_tree_structure = FileFinder.find_files_with_extensions(
                root_path=path_to_doc_root,
                ignored_dirs=[config.output_dir],
                extensions={".sdoc"},
            )
            root_trees.append(file_tree_structure)

        return root_trees, asset_dirs
