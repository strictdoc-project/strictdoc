import os
import sys
from pathlib import Path
from typing import Optional

from strictdoc.backend.excel.export.excel_generator import ExcelGenerator
from strictdoc.backend.reqif.reqif_export import ReqIFExport
from strictdoc.backend.sdoc.errors.document_tree_error import DocumentTreeError
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.core.traceability_index_builder import TraceabilityIndexBuilder
from strictdoc.export.dot.document_dot_generator import DocumentDotGenerator
from strictdoc.export.html.html_generator import HTMLGenerator
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.export.rst.document_rst_generator import DocumentRSTGenerator
from strictdoc.helpers.timing import timing_decorator


class ExportAction:
    def __init__(
        self,
        project_config: ProjectConfig,
        parallelizer,
    ):
        assert parallelizer
        self.project_config: ProjectConfig = project_config
        self.parallelizer = parallelizer
        self.traceability_index: Optional[TraceabilityIndex] = None

    @timing_decorator("Parse SDoc project tree")
    def build_index(self):
        try:
            traceability_index: TraceabilityIndex = (
                TraceabilityIndexBuilder.create(
                    project_config=self.project_config,
                    parallelizer=self.parallelizer,
                )
            )
        except DocumentTreeError as exc:
            print(exc.to_print_message())  # noqa: T201
            sys.exit(1)
        self.traceability_index = traceability_index

    @timing_decorator("Export SDoc")
    def export(self):
        assert (
            self.traceability_index is not None
        ), "The index must be built at this point."
        if (
            "html" in self.project_config.export_formats
            or "html-standalone" in self.project_config.export_formats
        ):
            is_small_project = self.traceability_index.is_small_project()

            html_templates = HTMLTemplates.create(
                project_config=self.project_config,
                enable_caching=not is_small_project,
                strictdoc_last_update=self.traceability_index.strictdoc_last_update,
            )

            html_generator = HTMLGenerator(self.project_config, html_templates)
            html_generator.export_complete_tree(
                traceability_index=self.traceability_index,
                parallelizer=self.parallelizer,
            )

        if "rst" in self.project_config.export_formats:
            output_rst_root = os.path.join(
                self.project_config.export_output_dir, "rst"
            )
            Path(output_rst_root).mkdir(parents=True, exist_ok=True)
            DocumentRSTGenerator.export_tree(
                self.traceability_index, output_rst_root
            )

        if "excel" in self.project_config.export_formats:
            output_excel_root = f"{self.project_config.export_output_dir}/excel"
            ExcelGenerator.export_tree(
                self.traceability_index,
                output_excel_root,
                project_config=self.project_config,
            )

        if "reqif-sdoc" in self.project_config.export_formats:
            output_reqif_root = f"{self.project_config.export_output_dir}/reqif"
            ReqIFExport.export(
                project_config=self.project_config,
                traceability_index=self.traceability_index,
                output_reqif_root=output_reqif_root,
                reqifz=False,
            )

        if "reqifz-sdoc" in self.project_config.export_formats:
            output_reqif_root = f"{self.project_config.export_output_dir}/reqif"
            ReqIFExport.export(
                project_config=self.project_config,
                traceability_index=self.traceability_index,
                output_reqif_root=output_reqif_root,
                reqifz=True,
            )

        if "dot" in self.project_config.export_formats:
            output_dot_root = os.path.join(
                self.project_config.export_output_dir, "dot"
            )
            Path(output_dot_root).mkdir(parents=True, exist_ok=True)
            DocumentDotGenerator("profile1").export_tree(
                self.traceability_index, output_dot_root
            )
            DocumentDotGenerator("profile2").export_tree(
                self.traceability_index, output_dot_root
            )
