import argparse
from typing import Any, Dict, Optional

from strictdoc.cli.command_parser_builder import (
    COMMAND_REGISTRY,
    CommandParserBuilder,
    SDocArgumentParser,
)
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.parallelizer import Parallelizer


class ImportReqIFCommandConfig:
    def __init__(
        self,
        input_path: str,
        output_path: str,
        profile: str,
        reqif_enable_mid: bool,
        reqif_import_markup: Optional[str],
    ):
        self.input_path: str = input_path
        self.output_path: str = output_path
        self.profile: Optional[str] = profile
        self.reqif_enable_mid: bool = reqif_enable_mid
        self.reqif_import_markup: Optional[str] = reqif_import_markup


class ImportExcelCommandConfig:
    def __init__(
        self, input_path: str, output_path: str, parser: SDocArgumentParser
    ) -> None:
        self.input_path: str = input_path
        self.output_path: str = output_path
        self.parser: SDocArgumentParser = parser


class SDocArgsParser:
    def __init__(self, args: argparse.Namespace, registry: Dict[str, Any]):
        self.args: argparse.Namespace = args
        self.registry: Dict[str, Any] = registry

    def is_debug_mode(self) -> bool:
        return assert_cast(self.args.debug, bool)

    def run(self, parallelizer: Parallelizer) -> bool:
        if self.args.command not in self.registry:
            return False

        cmd = self.registry[self.args.command]
        if isinstance(cmd, dict):
            assert self.args.subcommand in cmd
            command_instance = cmd[self.args.subcommand](self.args)
        else:
            command_instance = cmd(self.args)
        command_instance.run(parallelizer)

        return True

    @property
    def is_import_command_reqif(self) -> bool:
        return (
            str(self.args.command) == "import"
            and str(self.args.import_format) == "reqif"
        )

    @property
    def is_import_command_excel(self) -> bool:
        return (
            str(self.args.command) == "import"
            and str(self.args.import_format) == "excel"
        )

    @property
    def is_server_command(self) -> bool:
        return str(self.args.command) == "server"

    def get_import_config_reqif(self, _: Any) -> ImportReqIFCommandConfig:
        return ImportReqIFCommandConfig(
            self.args.input_path,
            self.args.output_path,
            self.args.profile,
            self.args.reqif_enable_mid,
            self.args.reqif_import_markup,
        )

    def get_import_config_excel(self, _: Any) -> ImportExcelCommandConfig:
        return ImportExcelCommandConfig(
            self.args.input_path, self.args.output_path, self.args.parser
        )


def create_sdoc_args_parser(
    testing_args: Optional[argparse.Namespace] = None,
) -> SDocArgsParser:
    args = testing_args
    if not args:
        builder = CommandParserBuilder()
        parser = builder.build()
        args = parser.parse_args()
    return SDocArgsParser(args, COMMAND_REGISTRY)
