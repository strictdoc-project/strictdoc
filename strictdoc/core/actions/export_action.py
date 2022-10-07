import os
import sys
from pathlib import Path

from strictdoc.backend.excel.export.excel_generator import ExcelGenerator
from strictdoc.backend.reqif.reqif_export import ReqIFExport
from strictdoc.backend.sdoc.errors.document_tree_error import DocumentTreeError
from strictdoc.cli.cli_arg_parser import ExportCommandConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.core.traceability_index_builder import TraceabilityIndexBuilder
from strictdoc.export.html.html_generator import HTMLGenerator
from strictdoc.export.rst.document_rst_generator import DocumentRSTGenerator
from strictdoc.helpers.timing import timing_decorator


class ExportAction:
    @staticmethod
    @timing_decorator("Export")
    def export(config: ExportCommandConfig, parallelizer):
        assert parallelizer

        try:
            traceability_index: TraceabilityIndex = (
                TraceabilityIndexBuilder.create(
                    config=config, parallelizer=parallelizer
                )
            )
        except DocumentTreeError as exc:
            print(exc.to_print_message())
            sys.exit(1)

        if "html" in config.formats or "html-standalone" in config.formats:
            Path(config.output_html_root).mkdir(parents=True, exist_ok=True)
            HTMLGenerator.export_tree(
                config=config,
                traceability_index=traceability_index,
                parallelizer=parallelizer,
            )

        if "rst" in config.formats:
            output_rst_root = os.path.join(config.output_dir, "rst")
            Path(output_rst_root).mkdir(parents=True, exist_ok=True)
            DocumentRSTGenerator.export_tree(
                traceability_index, output_rst_root
            )

        if "excel" in config.formats:
            output_excel_root = f"{config.output_dir}/excel"
            ExcelGenerator.export_tree(
                traceability_index,
                output_excel_root,
                config.fields,
            )

        if "reqif-sdoc" in config.formats:
            output_reqif_root = f"{config.output_dir}/reqif"
            ReqIFExport.export(
                traceability_index=traceability_index,
                output_reqif_root=output_reqif_root,
            )
