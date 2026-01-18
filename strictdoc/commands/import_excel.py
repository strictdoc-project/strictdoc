import argparse

from strictdoc.cli.base_command import BaseCommand
from strictdoc.commands.import_excel_config import ImportExcelCommandConfig
from strictdoc.core.actions.import_action import ImportAction
from strictdoc.core.project_config import ProjectConfigLoader
from strictdoc.helpers.parallelizer import Parallelizer

EXCEL_PARSERS = ["basic"]


class ImportExcelCommand(BaseCommand):
    HELP = "Create StrictDoc file from Excel document."
    DETAILED_HELP = HELP

    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
        def check_excel_parser(parser: str) -> str:
            if parser not in EXCEL_PARSERS:
                message = (
                    f"invalid choice: '{parser}' (choose from {EXCEL_PARSERS})"
                )
                raise argparse.ArgumentTypeError(message)
            return parser

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

    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.config: ImportExcelCommandConfig = ImportExcelCommandConfig(
            **vars(args)
        )

    def run(self, parallelizer: Parallelizer) -> None:  # noqa: ARG002
        project_config = ProjectConfigLoader.load_using_import_excel_config(
            self.config
        )
        import_action = ImportAction()
        import_action.do_import(self.config, project_config)
