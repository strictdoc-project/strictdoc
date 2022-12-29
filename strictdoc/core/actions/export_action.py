import os
import sys
from pathlib import Path
from typing import Optional

from strictdoc.backend.excel.export.excel_generator import ExcelGenerator
from strictdoc.backend.reqif.reqif_export import ReqIFExport
from strictdoc.backend.sdoc.errors.document_tree_error import DocumentTreeError
from strictdoc.cli.cli_arg_parser import ExportCommandConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.core.traceability_index_builder import TraceabilityIndexBuilder
from strictdoc.export.html.html_generator import HTMLGenerator
from strictdoc.export.rst.document_rst_generator import DocumentRSTGenerator


class ExportAction:
    def __init__(self, config: ExportCommandConfig, parallelizer):
        assert parallelizer
        self.config: ExportCommandConfig = config
        self.parallelizer = parallelizer
        self.traceability_index: Optional[TraceabilityIndex] = None

    def build_index(self):
        try:
            traceability_index: TraceabilityIndex = (
                TraceabilityIndexBuilder.create(
                    config=self.config, parallelizer=self.parallelizer
                )
            )
        except DocumentTreeError as exc:
            print(exc.to_print_message())
            sys.exit(1)
        self.traceability_index = traceability_index

    def export(self):
        assert (
            self.traceability_index is not None
        ), "The index must be built at this point."
        if (
            "html" in self.config.formats
            or "html-standalone" in self.config.formats
        ):
            Path(self.config.output_html_root).mkdir(
                parents=True, exist_ok=True
            )
            HTMLGenerator.export_tree(
                config=self.config,
                traceability_index=self.traceability_index,
                parallelizer=self.parallelizer,
            )

        if "rst" in self.config.formats:
            output_rst_root = os.path.join(self.config.output_dir, "rst")
            Path(output_rst_root).mkdir(parents=True, exist_ok=True)
            DocumentRSTGenerator.export_tree(
                self.traceability_index, output_rst_root
            )

        if "excel" in self.config.formats:
            output_excel_root = f"{self.config.output_dir}/excel"
            ExcelGenerator.export_tree(
                self.traceability_index,
                output_excel_root,
                self.config,
            )

        if "reqif-sdoc" in self.config.formats:
            output_reqif_root = f"{self.config.output_dir}/reqif"
            ReqIFExport.export(
                traceability_index=self.traceability_index,
                output_reqif_root=output_reqif_root,
            )
