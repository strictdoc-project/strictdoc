"""
@relation(SDOC-SRS-104, SDOC-SRS-115, scope=file)
"""

import os
import sys
import time
from functools import partial
from typing import Dict, List, Optional, Tuple, Union

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
from strictdoc.helpers.timing import (
    measure_performance,
    measure_performance_loop,
    timing_decorator,
)

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
    ) -> Tuple[File, str, Union[SDocDocument, DocumentGrammar], float]:
        """
        Returns the read document/grammar together with the read's duration
        instead of printing directly: the caller (running in the main
        process) reports progress for all documents through a single
        measure_performance_loop(), which a worker process can't safely
        share (concurrent in-place progress-line writes from multiple
        processes would interleave and corrupt the terminal output).
        """
        _, doc_file, file_tree_mount_folder = document_triple
        doc_full_path = doc_file.full_path

        time_start = time.time()

        document_or_grammar: Union[SDocDocument, DocumentGrammar, None] = None

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

        time_end = time.time()

        return (
            doc_file,
            file_tree_mount_folder,
            document_or_grammar,
            time_end - time_start,
        )

    @staticmethod
    def _read_document_from_cache(
        document_triple: Tuple[Union[Folder, File], File, str],
        extension_dispatch_table: List[FormatDispatchEntry],
        project_config: ProjectConfig,
    ) -> Optional[
        Tuple[File, str, Union[SDocDocument, DocumentGrammar], float]
    ]:
        """
        Return the document or grammar from the cache of its format, in the
        same form as _process_worker_parse_document(). Return None if the
        format has no up-to-date cache entry for the file, or no cache.
        """
        _, doc_file, file_tree_mount_folder = document_triple
        doc_full_path = doc_file.full_path

        time_start = time.time()

        for (
            extension_,
            format_,
            is_grammar_,
        ) in extension_dispatch_table:
            if not doc_full_path.endswith(extension_):
                continue
            document_or_grammar: Union[SDocDocument, DocumentGrammar, None] = (
                format_.read_grammar_from_cache(doc_file, project_config)
                if is_grammar_
                else format_.read_from_cache(doc_file, project_config)
            )
            if document_or_grammar is None:
                return None
            drop_textx_meta(document_or_grammar)
            return (
                doc_file,
                file_tree_mount_folder,
                document_or_grammar,
                time.time() - time_start,
            )
        return None

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
            with measure_performance_loop(
                "Reading SDOC", len(file_tree_list)
            ) as report_progress:

                def on_item_complete(
                    item_index: int,  # noqa: ARG001
                    result: Tuple[
                        File, str, Union[SDocDocument, DocumentGrammar], float
                    ],
                ) -> None:
                    doc_file_ = result[0]
                    elapsed_time = result[3]
                    title = os.path.basename(doc_file_.full_path)
                    with report_progress(title, elapsed_time=elapsed_time):
                        pass

                # The documents and grammars whose cache entries are up to
                # date are read in this process. Reading them in worker
                # processes would cost more: the parallelizer would start
                # the worker processes, and each document would be unpickled
                # from the cache in a worker, pickled again, and unpickled
                # once more in this process. Only the documents that must be
                # parsed go to the parallelizer.
                extension_dispatch_table = _build_extension_dispatch_table(
                    project_config
                )
                found_documents: List[
                    Optional[
                        Tuple[
                            File,
                            str,
                            Union[SDocDocument, DocumentGrammar],
                            float,
                        ]
                    ]
                ] = [None] * len(file_tree_list)
                indexes_to_parse: List[int] = []
                for index_, document_triple_ in enumerate(file_tree_list):
                    cached_result = DocumentFinder._read_document_from_cache(
                        document_triple_,
                        extension_dispatch_table,
                        project_config,
                    )
                    if cached_result is None:
                        indexes_to_parse.append(index_)
                        continue
                    found_documents[index_] = cached_result
                    on_item_complete(index_, cached_result)

                parsed_results = parallelizer.run_parallel(
                    [file_tree_list[index_] for index_ in indexes_to_parse],
                    process_document_binding,
                    on_item_complete,
                )
                for index_, parsed_result_ in zip(
                    indexes_to_parse, parsed_results
                ):
                    found_documents[index_] = parsed_result_

        doc_file: File
        for found_document_ in found_documents:
            assert found_document_ is not None
            doc_file, file_tree_mount_folder, document, _ = found_document_
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
                level=doc_file.level,
                file_tree_mount_folder=file_tree_mount_folder,
                document_filename=document_filename,
                document_filename_base=document_filename_base,
                input_doc_full_path=input_doc_full_path,
                input_doc_rel_path=doc_file.rel_path,
                input_doc_dir_rel_path=doc_relative_path_folder,
                input_doc_assets_dir_rel_path=input_doc_assets_dir_rel_path,
                output_document_dir_full_path=output_document_dir_full_path,
                output_document_dir_rel_path=output_document_dir_rel_path,
            )
            document.assign_meta(document_meta)

            output_document_rel_path: SDocRelativePath = SDocRelativePath(
                os.path.join(
                    output_document_dir_rel_path.relative_path,
                    f"{document_filename}.html",
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
