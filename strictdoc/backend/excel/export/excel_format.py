from typing import List

from strictdoc.backend.excel.excel_import import ExcelImport
from strictdoc.backend.excel.export.excel_generator import ExcelGenerator
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.commands.import_excel_config import ImportExcelCommandConfig
from strictdoc.core.format import ExportContext, Format


class ExcelFormat(Format):
    @staticmethod
    def handles() -> List[str]:
        return ["excel"]

    @staticmethod
    def supported_extensions() -> List[str]:
        return [".xlsx"]

    @staticmethod
    def supports_import() -> bool:
        return True

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
        output_excel_root = f"{context.project_config.output_dir}/excel"
        ExcelGenerator.export_tree(
            context.traceability_index,
            output_excel_root,
            project_config=context.project_config,
        )

    def import_file(  # type: ignore[override]
        self, import_config: ImportExcelCommandConfig
    ) -> SDocDocument:
        return ExcelImport.import_from_file(import_config)
