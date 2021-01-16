import glob
import os
from pathlib import Path

from strictdoc.core.document_finder import DocumentFinder
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.excel.excel_generator import ExcelGenerator
from strictdoc.export.html.html_generator import HTMLGenerator
from strictdoc.export.rst.document_rst_generator import DocumentRSTGenerator
from strictdoc.helpers.file_modification_time import get_file_modification_time
from strictdoc.helpers.timing import timing_decorator


class ExportAction:
    def __init__(self, strictdoc_src_path, parallelizer):
        assert parallelizer
        self.strictdoc_src_path = strictdoc_src_path
        self.cwd = os.getcwd()
        self.parallelizer = parallelizer
        strict_own_files = glob.iglob(
            "{}/strictdoc/**/*".format(self.strictdoc_src_path), recursive=True
        )
        strict_own_files = [
            f
            for f in strict_own_files
            if f.endswith(".html") or f.endswith(".py")
        ]
        latest_strictdoc_own_file = max(strict_own_files, key=os.path.getctime)
        self.strictdoc_last_update = get_file_modification_time(
            latest_strictdoc_own_file
        )

    @timing_decorator("Export")
    def export(
        self, path_to_single_file_or_doc_root, output_dir, formats, fields
    ):
        assert isinstance(formats, list)

        if isinstance(path_to_single_file_or_doc_root, str):
            path_to_single_file_or_doc_root = [path_to_single_file_or_doc_root]
        output_dir = output_dir if output_dir else "output"

        if not os.path.isabs(output_dir):
            output_dir = os.path.join(self.cwd, output_dir)

        output_html_root = "{}/html".format(output_dir)

        document_tree, asset_dirs = DocumentFinder.find_sdoc_content(
            path_to_single_file_or_doc_root, output_html_root, self.parallelizer
        )

        traceability_index = TraceabilityIndex.create(document_tree)

        if "html" in formats or "html-standalone" in formats:
            Path(output_html_root).mkdir(parents=True, exist_ok=True)
            HTMLGenerator.export_tree(
                formats,
                document_tree,
                traceability_index,
                output_html_root,
                self.strictdoc_src_path,
                self.strictdoc_last_update,
                asset_dirs,
                self.parallelizer,
            )

        if "rst" in formats:
            output_rst_root = "{}/rst".format(output_dir)
            Path(output_rst_root).mkdir(parents=True, exist_ok=True)
            DocumentRSTGenerator.export_tree(
                document_tree, traceability_index, output_rst_root
            )

        if "excel" in formats:
            output_excel_root = "{}/excel".format(output_dir)
            ExcelGenerator.export_tree(
                document_tree, traceability_index, output_excel_root, fields
            )
