import os
import tempfile

from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.generators.document_pdf import (
    DocumentHTML2PDFGenerator,
)
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.export.html.renderers.markup_renderer import MarkupRenderer
from strictdoc.export.html2pdf.pdf_print_driver import PDFPrintDriver
from strictdoc.helpers.file_system import sync_dir
from strictdoc.helpers.timing import measure_performance


class HTML2PDFGenerator:
    @staticmethod
    def export_tree(
        project_config: ProjectConfig,
        traceability_index: TraceabilityIndex,
        html_templates: HTMLTemplates,
        output_html2pdf_root: str,
    ):
        for document_ in traceability_index.document_tree.document_list:
            link_renderer = LinkRenderer(
                root_path="", static_path=project_config.dir_for_sdoc_assets
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

            with tempfile.NamedTemporaryFile(
                "w",
                suffix=".html",
            ) as temp_output_html_file_:
                temp_output_html_dir_ = os.path.dirname(
                    temp_output_html_file_.name
                )
                sync_dir(
                    project_config.get_static_files_path(),
                    os.path.join(temp_output_html_dir_, "_static"),
                    message="Copying StrictDoc's assets for HTML2PDF",
                )

                temp_output_html_file_.write(document_content)

                path_to_output_pdf = os.path.join(
                    output_html2pdf_root,
                    document_.meta.input_doc_dir_rel_path,
                    document_.meta.document_filename_base + ".pdf",
                )
                pdf_print_driver = PDFPrintDriver()
                try:
                    pdf_print_driver.get_pdf_from_html(
                        temp_output_html_file_.name, path_to_output_pdf
                    )
                except TimeoutError:
                    print("error: HTML2PDF: timeout error.")  # noqa: T201
