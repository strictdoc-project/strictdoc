from strictdoc.cli.cli_arg_parser import ImportCommandConfig
from strictdoc.backend.excel.import_.excel_to_sdoc_converter import (
    ExcelToSDocConverter,
)


class ExcelImport:
    @staticmethod
    def import_from_file(import_config: ImportCommandConfig):
        document = ExcelToSDocConverter.parse(import_config.input_path)
        return document
