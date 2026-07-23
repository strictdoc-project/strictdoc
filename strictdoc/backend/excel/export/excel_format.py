import argparse
import os
from typing import List

from strictdoc.backend.excel.excel_import import ExcelImport, ExcelImportOptions
from strictdoc.backend.excel.export.excel_generator import ExcelGenerator
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.commands.convert_config import ConvertCommandConfig
from strictdoc.core.format import ExportContext, Format
from strictdoc.core.project_config import ProjectConfig

EXCEL_PARSERS = ["basic"]


def check_excel_parser(parser_name: str) -> str:
    if parser_name not in EXCEL_PARSERS:
        message = (
            f"invalid choice: '{parser_name}' (choose from {EXCEL_PARSERS})"
        )
        raise argparse.ArgumentTypeError(message)
    return parser_name


class ExcelFormat(Format):
    @staticmethod
    def handles() -> List[str]:
        return ["excel"]

    @classmethod
    def add_import_arguments(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--excel-parser",
            type=check_excel_parser,
            default="basic",
            help=(
                "An argument that selects the Excel parser. "
                f"Possible values: {{{', '.join(EXCEL_PARSERS)}}}"
            ),
        )

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
    def supports_edit() -> bool:
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

    @classmethod
    def build_import_options(
        cls, args: argparse.Namespace
    ) -> ExcelImportOptions:
        return ExcelImportOptions(
            input_path=args.input_path,
            excel_parser=args.excel_parser,
        )

    def import_file(  # type: ignore[override]
        self,
        import_options: ExcelImportOptions,
        project_config: ProjectConfig,  # noqa: ARG002
    ) -> SDocDocument:
        return ExcelImport.import_from_file(import_options)

    def import_output_filename_stem(
        self,
        document: SDocDocument,  # noqa: ARG002
        convert_config: ConvertCommandConfig,
    ) -> str:
        return os.path.splitext(os.path.basename(convert_config.input_path))[0]
