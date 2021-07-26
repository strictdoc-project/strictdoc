import glob
import os
from pathlib import Path

from strictdoc.backend.dsl.errors.document_tree_error import DocumentTreeError
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
from strictdoc.export.excel.excel_generator import ExcelGenerator
from strictdoc.export.html.html_generator import HTMLGenerator
from strictdoc.export.rst.document_rst_generator import DocumentRSTGenerator
from strictdoc.helpers.file_modification_time import get_file_modification_time
from strictdoc.helpers.timing import timing_decorator


class ExportAction:
    @staticmethod
    @timing_decorator("Export")
    def export(config: ExportCommandConfig, parallelizer):
        assert parallelizer
        cwd = os.getcwd()
        strict_own_files = glob.iglob(
            "{}/strictdoc/**/*".format(config.strictdoc_root_path),
            recursive=True,
        )
        strict_own_files = [
            f
            for f in strict_own_files
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
        output_dir = config.output_dir if config.output_dir else "output"

        if not os.path.isabs(output_dir):
            output_dir = os.path.join(cwd, output_dir)

        output_html_root = "{}/html".format(output_dir)

        document_tree, asset_dirs = DocumentFinder.find_sdoc_content(
            path_to_single_file_or_doc_root, output_html_root, parallelizer
        )

        try:
            traceability_index: TraceabilityIndex = (
                TraceabilityIndexBuilder.create(document_tree)
            )
        except DocumentTreeError as exc:
            print(exc.to_print_message())
            exit(1)

        if config.experimental_enable_file_traceability:
            source_tree: SourceTree = SourceFilesFinder.find_source_files(
                output_html_root, document_tree
            )
            source_files = source_tree.source_files
            source_file: SourceFile
            for source_file in source_files:
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
            Path(output_html_root).mkdir(parents=True, exist_ok=True)
            HTMLGenerator.export_tree(
                config,
                document_tree,
                traceability_index,
                output_html_root,
                strictdoc_last_update,
                asset_dirs,
                parallelizer,
            )

        if "rst" in config.formats:
            output_rst_root = "{}/rst".format(output_dir)
            Path(output_rst_root).mkdir(parents=True, exist_ok=True)
            DocumentRSTGenerator.export_tree(
                document_tree, traceability_index, output_rst_root
            )

        if "excel" in config.formats:
            output_excel_root = "{}/excel".format(output_dir)
            ExcelGenerator.export_tree(
                document_tree,
                traceability_index,
                output_excel_root,
                config.fields,
            )
