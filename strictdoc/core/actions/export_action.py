import glob
import os
import sys
from pathlib import Path
from typing import List, Iterator, Optional

from strictdoc.backend.sdoc.errors.document_tree_error import DocumentTreeError
from strictdoc.backend.source_file_syntax.reader import (
    SourceFileTraceabilityReader,
)
from strictdoc.cli.cli_arg_parser import ExportCommandConfig
from strictdoc.core.document_finder import DocumentFinder
from strictdoc.core.finders.source_files_finder import (
    SourceFilesFinder,
    SourceFile,
)
from strictdoc.core.source_tree import SourceTree
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.core.traceability_index_builder import TraceabilityIndexBuilder
from strictdoc.backend.excel.export.excel_generator import ExcelGenerator
from strictdoc.export.html.html_generator import HTMLGenerator
from strictdoc.export.rst.document_rst_generator import DocumentRSTGenerator
from strictdoc.helpers.file_modification_time import get_file_modification_time
from strictdoc.helpers.timing import timing_decorator
from strictdoc.backend.reqif.reqif_export import ReqIFExport


class ExportAction:
    def __init__(self, config: ExportCommandConfig, parallelizer):
        assert parallelizer

        self.config = config
        self.parallelizer = parallelizer
        self.document_tree = None
        self.asset_dirs = None
        self.strictdoc_last_update = None
        self.traceability_index: Optional[TraceabilityIndex] = None

    # TODO: Having a cycle init - prepare - export is not great.
    # Find a better way to preserve state!
    def prepare(self):
        config = self.config
        parallelizer = self.parallelizer

        strict_own_files_unfiltered: Iterator[str] = glob.iglob(
            f"{config.strictdoc_root_path}/strictdoc/**/*",
            recursive=True,
        )
        strict_own_files: List[str] = [
            f
            for f in strict_own_files_unfiltered
            if f.endswith(".html") or f.endswith(".py")
        ]
        latest_strictdoc_own_file = max(strict_own_files, key=os.path.getctime)
        strictdoc_last_update = get_file_modification_time(
            latest_strictdoc_own_file
        )

        assert isinstance(config.formats, list)

        path_to_single_file_or_doc_root = config.input_paths
        if isinstance(path_to_single_file_or_doc_root, str):
            path_to_single_file_or_doc_root = [config.input_paths]

        document_tree, asset_dirs = DocumentFinder.find_sdoc_content(
            path_to_single_file_or_doc_root, config, parallelizer
        )
        try:
            traceability_index: TraceabilityIndex = (
                TraceabilityIndexBuilder.create(document_tree)
            )
        except DocumentTreeError as exc:
            print(exc.to_print_message())
            sys.exit(1)

        self.document_tree = document_tree
        self.asset_dirs = asset_dirs
        self.strictdoc_last_update = strictdoc_last_update
        self.traceability_index = traceability_index

    @timing_decorator("Export")
    def export(self):
        assert self.traceability_index is not None

        config = self.config
        parallelizer = self.parallelizer
        document_tree = self.document_tree
        asset_dirs = self.asset_dirs
        strictdoc_last_update = self.strictdoc_last_update
        traceability_index = self.traceability_index

        if config.experimental_enable_file_traceability:
            source_tree: SourceTree = SourceFilesFinder.find_source_files(
                config
            )
            source_files = source_tree.source_files
            source_file: SourceFile
            for source_file in source_files:
                is_source_file_referenced = (
                    traceability_index.has_source_file_reqs(
                        source_file.in_doctree_source_file_rel_path
                    )
                )
                if not is_source_file_referenced:
                    continue
                source_file.is_referenced = True
                traceability_reader = SourceFileTraceabilityReader()
                traceability_info = traceability_reader.read_from_file(
                    source_file.full_path
                )
                if traceability_info:
                    traceability_index.attach_traceability_info(
                        source_file.in_doctree_source_file_rel_path,
                        traceability_info,
                    )
            document_tree.attach_source_tree(source_tree)

        if "html" in config.formats or "html-standalone" in config.formats:
            Path(config.output_html_root).mkdir(parents=True, exist_ok=True)
            HTMLGenerator.export_tree(
                config=config,
                document_tree=document_tree,
                traceability_index=traceability_index,
                output_html_root=config.output_html_root,
                strictdoc_last_update=strictdoc_last_update,
                asset_dirs=asset_dirs,
                parallelizer=parallelizer,
            )

        if "rst" in config.formats:
            output_rst_root = os.path.join(config.output_dir, "rst")
            Path(output_rst_root).mkdir(parents=True, exist_ok=True)
            DocumentRSTGenerator.export_tree(
                document_tree, traceability_index, output_rst_root
            )

        if "excel" in config.formats:
            output_excel_root = f"{config.output_dir}/excel"
            ExcelGenerator.export_tree(
                document_tree,
                traceability_index,
                output_excel_root,
                config.fields,
            )

        if "reqif-sdoc" in config.formats:
            output_reqif_root = f"{config.output_dir}/reqif"
            ReqIFExport.export(
                document_tree,
                output_reqif_root,
            )
