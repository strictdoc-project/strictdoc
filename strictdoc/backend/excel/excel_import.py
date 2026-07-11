"""
@relation(SDOC-SRS-152, scope=file)
"""

from dataclasses import dataclass

from strictdoc.backend.excel.import_.excel_to_sdoc_converter import (
    ExcelToSDocConverter,
)
from strictdoc.backend.sdoc.models.document import SDocDocument


@dataclass
class ExcelImportOptions:
    input_path: str
    excel_parser: str


class ExcelImport:
    @staticmethod
    def import_from_file(
        import_config: ExcelImportOptions,
    ) -> SDocDocument:
        document = ExcelToSDocConverter.convert(import_config.input_path)
        return document
