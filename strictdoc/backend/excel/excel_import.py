"""
@relation(SDOC-SRS-152, scope=file)
"""

from strictdoc.backend.excel.import_.excel_to_sdoc_converter import (
    ExcelToSDocConverter,
)
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.commands.import_excel_config import ImportExcelCommandConfig


class ExcelImport:
    @staticmethod
    def import_from_file(
        import_config: ImportExcelCommandConfig,
    ) -> SDocDocument:
        document = ExcelToSDocConverter.convert(import_config.input_path)
        return document
