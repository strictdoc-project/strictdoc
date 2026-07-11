import os
from pathlib import Path
from typing import List

from strictdoc.backend.rst.document_rst_generator import DocumentRSTGenerator
from strictdoc.core.format import ExportContext, Format


class RSTFormat(Format):
    @staticmethod
    def handles() -> List[str]:
        return ["rst"]

    @staticmethod
    def supported_extensions() -> List[str]:
        return [".rst"]

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
    def supports_grammar() -> bool:
        return False

    def export_complete_tree(self, context: ExportContext, handle: str) -> None:
        assert handle in self.handles(), handle
        output_rst_root = os.path.join(context.project_config.output_dir, "rst")
        Path(output_rst_root).mkdir(parents=True, exist_ok=True)
        DocumentRSTGenerator.export_tree(
            context.traceability_index, output_rst_root
        )
