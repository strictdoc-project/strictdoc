"""
@relation(SDOC-SRS-152, scope=file)
"""

# mypy: disable-error-code="no-untyped-def"
from strictdoc.backend.excel.import_.excel_to_sdoc_converter import (
    ExcelToSDocConverter,
)
from strictdoc.cli.cli_arg_parser import ImportExcelCommandConfig


class ExcelImport:
    @staticmethod
    def import_from_file(import_config: ImportExcelCommandConfig):
        document = ExcelToSDocConverter.convert(import_config.input_path)
        return document
