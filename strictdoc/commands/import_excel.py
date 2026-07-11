import argparse

from strictdoc.backend.excel.export.excel_format import ExcelFormat
from strictdoc.cli.base_command import BaseCommand
from strictdoc.commands._shared import add_config_argument
from strictdoc.commands.import_excel_config import ImportExcelCommandConfig
from strictdoc.core.actions.import_action import ImportAction
from strictdoc.core.project_config import ProjectConfigLoader
from strictdoc.helpers.parallelizer import Parallelizer


class ImportExcelCommand(BaseCommand):
    HELP = "Create StrictDoc file from Excel document."
    DETAILED_HELP = HELP

    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
        ExcelFormat.add_import_arguments(parser)
        add_config_argument(parser)

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
