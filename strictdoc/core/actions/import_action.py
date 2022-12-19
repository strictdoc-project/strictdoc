import os
from pathlib import Path
from typing import Union

from strictdoc.backend.excel.excel_import import ExcelImport
from strictdoc.backend.reqif.reqif_import import ReqIFImport
from strictdoc.backend.sdoc.writer import SDWriter
from strictdoc.cli.cli_arg_parser import (
    ImportExcelCommandConfig,
    ImportReqIFCommandConfig,
)
from strictdoc.helpers.timing import timing_decorator


class ImportAction:
    @staticmethod
    @timing_decorator("Import")
    def do_import(
        import_config: Union[ImportReqIFCommandConfig, ImportExcelCommandConfig]
    ) -> None:
        if isinstance(import_config, ImportReqIFCommandConfig):
            document = ReqIFImport.import_from_file(import_config)[0]
        elif isinstance(import_config, ImportExcelCommandConfig):
            document = ExcelImport.import_from_file(import_config)
        else:
            raise NotImplementedError()

        document_content = SDWriter().write(document)
        output_folder = os.path.dirname(import_config.output_path)
        Path(output_folder).mkdir(parents=True, exist_ok=True)
        with open(
            import_config.output_path, "w", encoding="utf8"
        ) as output_file:
            output_file.write(document_content)
