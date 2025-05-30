# mypy: disable-error-code="arg-type,no-untyped-call,no-untyped-def,operator"
import os
import sys
from pathlib import Path
from typing import Optional

from strictdoc.backend.excel.export.excel_generator import ExcelGenerator
from strictdoc.backend.reqif.reqif_export import ReqIFExport
from strictdoc.backend.sdoc.errors.document_tree_error import DocumentTreeError
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.writer import SDWriter
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.core.traceability_index_builder import TraceabilityIndexBuilder
from strictdoc.export.doxygen.doxygen_generator import DoxygenGenerator
from strictdoc.export.html.document_type import DocumentType
from strictdoc.export.html.html_generator import HTMLGenerator
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.export.html2pdf.html2pdf_generator import HTML2PDFGenerator
from strictdoc.export.json.json_generator import JSONGenerator
from strictdoc.export.rst.document_rst_generator import DocumentRSTGenerator
from strictdoc.export.spdx.spdx_generator import SPDXGenerator
from strictdoc.helpers.parallelizer import NullParallelizer
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
        self.traceability_index: TraceabilityIndex = self.build_index()

    @timing_decorator("Parse SDoc project tree")
    def build_index(self) -> TraceabilityIndex:
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
        return traceability_index

    @timing_decorator("Export SDoc")
    def export(self) -> None:
        assert self.traceability_index is not None, (
            "The index must be built at this point."
        )
        if (
            "html" in self.project_config.export_formats
            or "html-standalone" in self.project_config.export_formats
            or "html2pdf" in self.project_config.export_formats
        ):
            is_small_project = self.traceability_index.is_small_project()

            html_templates = HTMLTemplates.create(
                project_config=self.project_config,
                enable_caching=not is_small_project,
                strictdoc_last_update=self.traceability_index.strictdoc_last_update,
            )

            # The bundle document is generated only when the option is provided.
            traceability_index_copy: Optional[TraceabilityIndex] = None
            bundle_document: Optional[SDocDocument] = None
            if self.project_config.generate_bundle_document:
                traceability_index_copy, bundle_document = (
                    self.traceability_index.clone_to_bundle_document(
                        self.project_config
                    )
                )

            if (
                "html" in self.project_config.export_formats
                or "html-standalone" in self.project_config.export_formats
            ):
                html_generator = HTMLGenerator(
                    self.project_config, html_templates
                )
                html_generator.export_complete_tree(
                    traceability_index=self.traceability_index,
                    parallelizer=self.parallelizer,
                )
                if self.project_config.generate_bundle_document:
                    html_generator.export_single_document(
                        document=bundle_document,
                        traceability_index=traceability_index_copy,
                        specific_documents=(DocumentType.DOCUMENT,),
                    )

            if "html2pdf" in self.project_config.export_formats:
                output_html2pdf_root = os.path.join(
                    self.project_config.output_dir, "html2pdf"
                )
                Path(output_html2pdf_root).mkdir(parents=True, exist_ok=True)
                HTML2PDFGenerator.export_tree(
                    self.project_config,
                    self.traceability_index,
                    html_templates,
                    output_html2pdf_root,
                )

                if self.project_config.generate_bundle_document:
                    HTML2PDFGenerator.export_tree(
                        self.project_config,
                        traceability_index_copy,
                        html_templates,
                        output_html2pdf_root,
                        flat_assets=True,
                    )

        if "rst" in self.project_config.export_formats:
            output_rst_root = os.path.join(
                self.project_config.output_dir, "rst"
            )
            Path(output_rst_root).mkdir(parents=True, exist_ok=True)
            DocumentRSTGenerator.export_tree(
                self.traceability_index, output_rst_root
            )

        if "excel" in self.project_config.export_formats:
            output_excel_root = f"{self.project_config.output_dir}/excel"
            ExcelGenerator.export_tree(
                self.traceability_index,
                output_excel_root,
                project_config=self.project_config,
            )

        if "reqif-sdoc" in self.project_config.export_formats:
            output_reqif_root = f"{self.project_config.output_dir}/reqif"
            ReqIFExport.export(
                project_config=self.project_config,
                traceability_index=self.traceability_index,
                output_reqif_root=output_reqif_root,
                reqifz=False,
            )

        if "reqifz-sdoc" in self.project_config.export_formats:
            output_reqif_root = f"{self.project_config.output_dir}/reqif"
            ReqIFExport.export(
                project_config=self.project_config,
                traceability_index=self.traceability_index,
                output_reqif_root=output_reqif_root,
                reqifz=True,
            )

        if "sdoc" in self.project_config.export_formats:
            self.export_sdoc()

        if "doxygen" in self.project_config.export_formats:
            output_doxygen_root = os.path.join(
                self.project_config.output_dir, "doxygen"
            )
            doxygen_generator = DoxygenGenerator(
                project_config=self.project_config
            )
            doxygen_generator.export(
                traceability_index=self.traceability_index,
                path_to_output_dir=output_doxygen_root,
            )

        if "spdx" in self.project_config.export_formats:
            output_dot_root = os.path.join(
                self.project_config.output_dir, "spdx"
            )
            Path(output_dot_root).mkdir(parents=True, exist_ok=True)
            SPDXGenerator().export_tree(
                self.project_config, self.traceability_index, output_dot_root
            )

        if "json" in self.project_config.export_formats:
            output_json_root = os.path.join(
                self.project_config.output_dir, "json"
            )
            Path(output_json_root).mkdir(parents=True, exist_ok=True)
            JSONGenerator().export_tree(
                self.traceability_index, self.project_config, output_json_root
            )

    def export_sdoc(self):
        assert self.project_config.input_paths
        try:
            traceability_index: TraceabilityIndex = (
                TraceabilityIndexBuilder.create(
                    project_config=self.project_config,
                    parallelizer=NullParallelizer(),
                )
            )
        except DocumentTreeError as exc:
            print(exc.to_print_message())  # noqa: T201
            sys.exit(1)
        else:
            assert traceability_index.document_tree

        writer = SDWriter(self.project_config)

        output_base_dir = (
            self.project_config.output_dir
            if self.project_config.output_dir is not None
            else os.path.join(os.getcwd(), "output")
        )
        output_dir = os.path.join(output_base_dir, "sdoc")
        for document in traceability_index.document_tree.document_list:
            assert document.meta
            assert document.meta.document_filename_base
            assert document.meta.input_doc_dir_rel_path
            output, fragments_dict = writer.write_with_fragments(
                document,
            )

            path_to_output_file_dir: str = os.path.join(
                output_dir, document.meta.input_doc_dir_rel_path.relative_path
            )
            Path(path_to_output_file_dir).mkdir(parents=True, exist_ok=True)
            path_to_output_file = os.path.join(
                path_to_output_file_dir, document.meta.document_filename_base
            )
            path_to_output_file += ".sdoc"
            with open(path_to_output_file, "w", encoding="utf8") as file:
                file.write(output)

            for fragment_path_, fragment_content_ in fragments_dict.items():
                path_to_output_fragment = os.path.join(
                    path_to_output_file_dir, fragment_path_
                )
                with open(
                    path_to_output_fragment, "w", encoding="utf8"
                ) as file_:
                    file_.write(fragment_content_)
