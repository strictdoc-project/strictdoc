import os
from pathlib import Path
from typing import List, Type, TypeVar, Union

from strictdoc.backend.excel.export.excel_format import ExcelFormat
from strictdoc.backend.reqif.reqif_format import ReqIFFormat
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.writer import SDWriter
from strictdoc.commands.import_excel_config import ImportExcelCommandConfig
from strictdoc.commands.import_reqif_config import ImportReqIFCommandConfig
from strictdoc.core.format import Format
from strictdoc.core.project_config import ProjectConfig
from strictdoc.helpers.string import (
    create_safe_document_file_name,
)
from strictdoc.helpers.timing import timing_decorator

FormatType = TypeVar("FormatType", bound=Format)


def _get_format(
    project_config: ProjectConfig, format_cls: Type[FormatType]
) -> FormatType:
    for format_ in project_config.formats:
        if isinstance(format_, format_cls):
            return format_
    raise NotImplementedError(
        f"{format_cls.__name__} is not configured for this project."
    )


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
            reqif_format = _get_format(project_config, ReqIFFormat)
            reqif_documents: List[SDocDocument] = reqif_format.import_file(
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
            excel_format = _get_format(project_config, ExcelFormat)
            excel_document: SDocDocument = excel_format.import_file(
                import_config, project_config
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
