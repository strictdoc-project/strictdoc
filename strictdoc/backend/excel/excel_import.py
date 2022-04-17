from strictdoc.cli.cli_arg_parser import ImportExcelCommandConfig
from strictdoc.backend.excel.import_.excel_to_sdoc_converter import (
    ExcelToSDocConverter,
)


class ExcelImport:
    @staticmethod
    def import_from_file(import_config: ImportExcelCommandConfig):
        document = ExcelToSDocConverter.convert(import_config.input_path)
        return document
