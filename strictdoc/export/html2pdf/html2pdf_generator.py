# mypy: disable-error-code="no-untyped-def,union-attr"
import os
from pathlib import Path
from typing import List, Tuple

from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.generators.document_pdf import (
    DocumentHTML2PDFGenerator,
)
from strictdoc.export.html.html_generator import HTMLGenerator
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.export.html.renderers.markup_renderer import MarkupRenderer
from strictdoc.export.html2pdf.pdf_print_driver import PDFPrintDriver
from strictdoc.helpers.exception import StrictDocException
from strictdoc.helpers.timing import measure_performance


class HTML2PDFGenerator:
    @staticmethod
    def export_tree(
        project_config: ProjectConfig,
        traceability_index: TraceabilityIndex,
        html_templates: HTMLTemplates,
        output_html2pdf_root: str,
        flat_assets: bool = False,
    ):
        if not project_config.is_activated_html2pdf():
            raise StrictDocException("HTML2PDF feature is not enabled")

        path_to_output_pdf_html_dir = os.path.join(output_html2pdf_root, "html")
        path_to_output_pdf_pdf_dir = os.path.join(output_html2pdf_root, "pdf")

        HTMLGenerator.export_assets(
            traceability_index=traceability_index,
            project_config=project_config,
            export_output_html_root=path_to_output_pdf_html_dir,
            flat_assets=flat_assets,
        )

        paths_to_print: List[Tuple[str, str]] = []

        for document_ in traceability_index.document_tree.document_list:
            root_path = document_.meta.get_root_path_prefix()

            link_renderer = LinkRenderer(
                root_path=root_path,
                static_path=project_config.dir_for_sdoc_assets,
            )
            markup_renderer = MarkupRenderer.create(
                "RST",
                traceability_index,
                link_renderer,
                html_templates,
                project_config,
                document_,
            )

            with measure_performance("Generating printable HTML document"):
                document_content = DocumentHTML2PDFGenerator.export(
                    project_config,
                    document_,
                    traceability_index,
                    markup_renderer,
                    link_renderer,
                    standalone=False,
                    html_templates=html_templates,
                )

            path_to_output_html_doc_dir = os.path.join(
                path_to_output_pdf_html_dir,
                document_.meta.output_document_dir_rel_path.relative_path,
            )
            Path(path_to_output_html_doc_dir).mkdir(parents=True, exist_ok=True)
            Path(path_to_output_pdf_pdf_dir).mkdir(parents=True, exist_ok=True)

            path_to_output_html_doc = os.path.join(
                path_to_output_html_doc_dir,
                document_.meta.document_filename_base + ".html",
            )

            with open(
                path_to_output_html_doc, "w", encoding="utf8"
            ) as output_html_doc_file_:
                output_html_doc_file_.write(document_content)

            path_to_output_pdf_dir = os.path.join(
                path_to_output_pdf_pdf_dir,
                document_.meta.input_doc_dir_rel_path.relative_path,
            )
            Path(path_to_output_pdf_dir).mkdir(parents=True, exist_ok=True)

            path_to_output_pdf = os.path.join(
                path_to_output_pdf_dir,
                document_.meta.document_filename_base + ".pdf",
            )

            paths_to_print.append((path_to_output_html_doc, path_to_output_pdf))

        paths_to_print_argument = ";".join(
            map(
                lambda in_out_path_pair_: f"{in_out_path_pair_[0]},{in_out_path_pair_[1]}",
                paths_to_print,
            )
        )
        pdf_print_driver = PDFPrintDriver()
        try:
            pdf_print_driver.get_pdf_from_html(
                project_config,
                paths_to_print_argument,
            )
        except TimeoutError:
            print("error: HTML2PDF: timeout error.")  # noqa: T201
