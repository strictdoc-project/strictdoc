"""
@relation(SDOC-SRS-104, SDOC-SRS-115, scope=file)
"""

import os
import sys
from functools import partial
from typing import Dict, List, Tuple, Union

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_grammar import DocumentGrammar
from strictdoc.core.asset_manager import AssetManager
from strictdoc.core.document_meta import DocumentMeta
from strictdoc.core.document_tree import DocumentTree
from strictdoc.core.file_system.file_tree import (
    File,
    FileFinder,
    FileTree,
    Folder,
    PathFinder,
)
from strictdoc.core.format import Format
from strictdoc.core.project_config import ProjectConfig
from strictdoc.helpers.exception import StrictDocException
from strictdoc.helpers.parallelizer import Parallelizer
from strictdoc.helpers.paths import SDocRelativePath
from strictdoc.helpers.textx import drop_textx_meta
from strictdoc.helpers.timing import measure_performance, timing_decorator

# Each entry: (extension, Format instance, is_grammar).
# Sorted longest-extension-first so that e.g. ".gra.md" is matched before
# ".md" (a "foo.gra.md" file ends with both).
FormatDispatchEntry = Tuple[str, Format, bool]


def _build_extension_dispatch_table(
    project_config: ProjectConfig,
) -> List[FormatDispatchEntry]:
    entries: List[FormatDispatchEntry] = []
    for format_ in project_config.formats:
        if format_.supports_read():
            for extension_ in format_.read_extensions():
                entries.append((extension_, format_, False))
        if format_.supports_grammar():
            for extension_ in format_.grammar_extensions():
                entries.append((extension_, format_, True))
    entries.sort(key=lambda entry: len(entry[0]), reverse=True)
    return entries


def get_document_extensions(project_config: ProjectConfig) -> List[str]:
    """
    All extensions natively read (as documents or grammars) by the
    project's registered Formats. Used both for DocumentFinder's own file
    discovery and, in strictdoc/server/document_watcher.py, so a filesystem
    watcher can't drift out of sync with what DocumentFinder actually reads.
    """
    return [
        extension_
        for extension_, _, _ in _build_extension_dispatch_table(project_config)
    ]


class DocumentFinder:
    @staticmethod
    @timing_decorator("Find and read SDoc files")
    def find_sdoc_content(
        project_config: ProjectConfig, parallelizer: Parallelizer
    ) -> Tuple[DocumentTree, AssetManager]:
        assert project_config.input_paths is not None
        for paths_to_files_or_doc in project_config.input_paths:
            if not os.path.exists(paths_to_files_or_doc):
                sys.stdout.flush()
                raise StrictDocException(
                    "error: "
                    "Provided path is neither a single file or a folder: "
                    f"'{paths_to_files_or_doc}'"
                )

        with measure_performance("Completed finding SDoc and assets"):
            file_tree, asset_manager = DocumentFinder._build_file_tree(
                project_config=project_config
            )
        with measure_performance("Completed building document tree"):
            document_tree = DocumentFinder._build_document_tree(
                file_tree, project_config, parallelizer
            )

        return document_tree, asset_manager

    @staticmethod
    def _process_worker_parse_document(
        document_triple: Tuple[Union[Folder, File], File, str],
        project_config: ProjectConfig,
    ) -> Tuple[File, str, Union[SDocDocument, DocumentGrammar]]:
        _, doc_file, file_tree_mount_folder = document_triple
        doc_full_path = doc_file.full_path

        with measure_performance(
            f"Reading SDOC: {os.path.basename(doc_full_path)}"
        ):
            document_or_grammar: Union[SDocDocument, DocumentGrammar, None] = (
                None
            )

            # @relation(SDOC-SRS-104, scope=range_start)
            for (
                extension_,
                format_,
                is_grammar_,
            ) in _build_extension_dispatch_table(project_config):
                if not doc_full_path.endswith(extension_):
                    continue
                if is_grammar_:
                    document_or_grammar = format_.read_grammar(
                        doc_file, project_config
                    )
                    assert isinstance(document_or_grammar, DocumentGrammar)
                else:
                    document_or_grammar = format_.read_from_file(
                        doc_file, project_config
                    )
                    assert isinstance(document_or_grammar, SDocDocument)
                break
            # @relation(SDOC-SRS-104, scope=range_end)

            if document_or_grammar is None:
                raise NotImplementedError
        drop_textx_meta(document_or_grammar)

        return doc_file, file_tree_mount_folder, document_or_grammar

    @staticmethod
    def _build_document_tree(
        file_trees: List[FileTree],
        project_config: ProjectConfig,
        parallelizer: Parallelizer,
    ) -> DocumentTree:
        """
        @relation(SDOC-SRS-48, scope=function)
        """

        assert isinstance(file_trees, list)

        output_root_html = project_config.export_output_html_root
        assert output_root_html is not None

        document_list: List[SDocDocument] = []
        map_docs_by_paths = {}
        map_docs_by_rel_paths: Dict[str, SDocDocument] = {}
        map_grammars_by_filenames = {}

        file_tree_list: List[Tuple[Union[Folder, File], File, str]] = []
        for file_tree in file_trees:
            file_tree_list.extend(list(file_tree.iterate()))

        process_document_binding = partial(
            DocumentFinder._process_worker_parse_document,
            project_config=project_config,
        )

        with measure_performance("Completed parsing all documents"):
            found_documents = parallelizer.run_parallel(
                file_tree_list, process_document_binding
            )

        doc_file: File
        for doc_file, file_tree_mount_folder, document in found_documents:
            assert isinstance(file_tree_mount_folder, str), (
                file_tree_mount_folder
            )

            if isinstance(document, DocumentGrammar):
                map_grammars_by_filenames[
                    doc_file.rel_path.relative_path_posix
                ] = document
                continue

            input_doc_full_path: str = doc_file.full_path
            map_docs_by_paths[input_doc_full_path] = document
            document_list.append(document)

            doc_relative_path_folder: SDocRelativePath = SDocRelativePath(
                os.path.dirname(doc_file.rel_path.relative_path)
            )
            output_document_dir_rel_path: SDocRelativePath = SDocRelativePath(
                os.path.join(
                    file_tree_mount_folder,
                    doc_relative_path_folder.relative_path,
                )
                if len(doc_relative_path_folder.relative_path) > 0
                else file_tree_mount_folder
            )

            document_filename = doc_file.file_name
            document_filename_base = os.path.splitext(document_filename)[0]

            output_document_dir_full_path: str = os.path.join(
                output_root_html, output_document_dir_rel_path.relative_path
            )

            input_doc_assets_dir_rel_path: SDocRelativePath = SDocRelativePath(
                os.path.join(
                    file_tree_mount_folder,
                    doc_relative_path_folder.relative_path,
                    "_assets",
                )
                if doc_relative_path_folder.length() > 0
                else "/".join((file_tree_mount_folder, "_assets"))
            )

            document_meta = DocumentMeta(
                doc_file.level,
                file_tree_mount_folder,
                document_filename,
                document_filename_base,
                input_doc_full_path,
                doc_file.rel_path,
                doc_relative_path_folder,
                input_doc_assets_dir_rel_path,
                output_document_dir_full_path,
                output_document_dir_rel_path,
            )
            document.assign_meta(document_meta)

            output_document_rel_path: SDocRelativePath = SDocRelativePath(
                os.path.join(
                    output_document_dir_rel_path.relative_path,
                    f"{document_filename_base}.html",
                )
            )

            map_docs_by_paths[input_doc_full_path] = document
            map_docs_by_rel_paths[output_document_rel_path.relative_path] = (
                document
            )

        return DocumentTree(
            file_trees,
            document_list,
            map_docs_by_paths,
            map_docs_by_rel_paths,
            map_grammars_by_filenames=map_grammars_by_filenames,
        )

    @staticmethod
    def _build_file_tree(
        project_config: ProjectConfig,
    ) -> Tuple[List[FileTree], AssetManager]:
        assert isinstance(project_config.input_paths, list)
        assert len(project_config.input_paths) > 0

        root_trees: List[FileTree] = []
        asset_manager = AssetManager()

        for path_to_doc_root_raw in project_config.input_paths:
            if os.path.isfile(path_to_doc_root_raw):
                path_to_doc_root = path_to_doc_root_raw
                if not os.path.isabs(path_to_doc_root):
                    path_to_doc_root = os.path.abspath(path_to_doc_root)

                parent_dir = os.path.dirname(path_to_doc_root)
                path_to_doc_root_base = os.path.dirname(parent_dir)

                assets_dir: str = os.path.join(parent_dir, "_assets")
                if os.path.isdir(assets_dir):
                    asset_manager.add_asset_dir(
                        full_path=assets_dir,
                        relative_path=SDocRelativePath(
                            os.path.relpath(assets_dir, path_to_doc_root_base)
                        ),
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
            with measure_performance("Find asset directories"):
                tree_asset_dirs: List[str] = PathFinder.find_directories(
                    path_to_doc_root,
                    "_assets",
                    include_paths=project_config.include_doc_paths,
                    exclude_paths=project_config.exclude_doc_paths,
                )

            for asset_dir_ in tree_asset_dirs:
                asset_manager.add_asset_dir(
                    full_path=asset_dir_,
                    relative_path=SDocRelativePath(
                        os.path.relpath(asset_dir_, path_to_doc_root_base)
                    ),
                )

            # Finding SDoc files.
            assert isinstance(project_config.output_dir, str)
            with measure_performance("Find SDoc files"):
                file_tree_structure = FileFinder.find_files_with_extensions(
                    root_path=path_to_doc_root,
                    ignored_dirs=[project_config.output_dir],
                    extensions=get_document_extensions(project_config),
                    include_paths=project_config.include_doc_paths,
                    exclude_paths=project_config.exclude_doc_paths,
                )
            root_trees.append(file_tree_structure)

        return root_trees, asset_manager
