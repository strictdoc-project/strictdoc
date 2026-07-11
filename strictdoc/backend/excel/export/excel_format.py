import argparse
from typing import List

from strictdoc.backend.excel.excel_import import ExcelImport
from strictdoc.backend.excel.export.excel_generator import ExcelGenerator
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.commands.import_excel_config import ImportExcelCommandConfig
from strictdoc.core.format import ExportContext, Format
from strictdoc.core.project_config import ProjectConfig

EXCEL_PARSERS = ["basic"]


class ExcelFormat(Format):
    @staticmethod
    def handles() -> List[str]:
        return ["excel"]

    @staticmethod
    def import_command_name() -> str:
        return "excel"

    @classmethod
    def add_import_arguments(cls, parser: argparse.ArgumentParser) -> None:
        def check_excel_parser(parser_name: str) -> str:
            if parser_name not in EXCEL_PARSERS:
                message = (
                    f"invalid choice: '{parser_name}' "
                    f"(choose from {EXCEL_PARSERS})"
                )
                raise argparse.ArgumentTypeError(message)
            return parser_name

        parser.add_argument(
            "parser",
            type=check_excel_parser,
            help=(
                "An argument that selects the Excel parser. "
                f"Possible values: {{{', '.join(EXCEL_PARSERS)}}}"
            ),
        )
        parser.add_argument(
            "input_path",
            type=str,
            help="Path to the input Excel file.",
        )
        parser.add_argument(
            "output_path",
            type=str,
            help="Path to the output SDoc file.",
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
        self,
        import_config: ImportExcelCommandConfig,
        project_config: ProjectConfig,  # noqa: ARG002
    ) -> SDocDocument:
        return ExcelImport.import_from_file(import_config)
