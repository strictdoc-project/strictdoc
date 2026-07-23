import os
from pathlib import Path
from typing import List

from strictdoc.core.format import ExportContext, Format
from strictdoc.features.html2pdf.html2pdf_generator import HTML2PDFGenerator


class HTML2PDFFormat(Format):
    @staticmethod
    def handles() -> List[str]:
        return ["html2pdf"]

    @staticmethod
    def supported_extensions() -> List[str]:
        return [".pdf"]

    @staticmethod
    def supports_import() -> bool:
        return False

    @staticmethod
    def supports_export() -> bool:
        return True

    @staticmethod
    def supports_read() -> bool:
        return False

    @staticmethod
    def supports_edit() -> bool:
        return False

    @staticmethod
    def supports_grammar() -> bool:
        return False

    def export_complete_tree(self, context: ExportContext, handle: str) -> None:
        assert handle in self.handles(), handle
        assert context.html_templates is not None

        output_html2pdf_root = os.path.join(
            context.project_config.output_dir, "html2pdf"
        )
        Path(output_html2pdf_root).mkdir(parents=True, exist_ok=True)
        HTML2PDFGenerator.export_tree(
            context.project_config,
            context.traceability_index,
            context.html_templates,
            output_html2pdf_root,
        )

        if context.project_config.generate_bundle_document:
            assert context.bundle_traceability_index is not None
            HTML2PDFGenerator.export_tree(
                context.project_config,
                context.bundle_traceability_index,
                context.html_templates,
                output_html2pdf_root,
                flat_assets=True,
            )
