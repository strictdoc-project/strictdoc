# mypy: disable-error-code="no-untyped-call,no-untyped-def"
import os
from pathlib import Path
from typing import List, Union

from strictdoc.backend.excel.excel_import import ExcelImport
from strictdoc.backend.reqif.reqif_import import ReqIFImport
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.writer import SDWriter
from strictdoc.cli.cli_arg_parser import (
    ImportExcelCommandConfig,
    ImportReqIFCommandConfig,
)
from strictdoc.core.project_config import ProjectConfig
from strictdoc.helpers.string import (
    create_safe_document_file_name,
)
from strictdoc.helpers.timing import timing_decorator


class ImportAction:
    @staticmethod
    @timing_decorator("Import")
    def do_import(
        import_config: Union[
            ImportReqIFCommandConfig, ImportExcelCommandConfig
        ],
        project_config: ProjectConfig,
    ) -> None:
        if isinstance(import_config, ImportReqIFCommandConfig):
            reqif_documents: List[SDocDocument] = ReqIFImport.import_from_file(
                import_config, project_config
            )
            for document_ in reqif_documents:
                Path(import_config.output_path).mkdir(
                    parents=True, exist_ok=True
                )
                path_to_output_document = os.path.join(
                    import_config.output_path,
                    create_safe_document_file_name(document_.reserved_title)
                    + ".sdoc",
                )
                document_content = SDWriter(project_config).write(document_)
                with open(
                    path_to_output_document, "w", encoding="utf8"
                ) as output_file:
                    output_file.write(document_content)
        elif isinstance(import_config, ImportExcelCommandConfig):
            excel_document: SDocDocument = ExcelImport.import_from_file(
                import_config
            )
            Path(import_config.output_path).mkdir(parents=True, exist_ok=True)
            path_to_output_document = os.path.join(
                import_config.output_path,
                os.path.splitext(os.path.basename(import_config.input_path))[0]
                + ".sdoc",
            )
            document_content = SDWriter(project_config).write(excel_document)
            with open(
                path_to_output_document, "w", encoding="utf8"
            ) as output_file:
                output_file.write(document_content)
        else:
            raise NotImplementedError()  # pragma: no cover
