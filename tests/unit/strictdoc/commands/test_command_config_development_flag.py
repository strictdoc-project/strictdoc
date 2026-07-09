import dataclasses
import inspect

from strictdoc.commands.export_config import ExportCommandConfig
from strictdoc.commands.format_config import FormatCommandConfig
from strictdoc.commands.import_excel_config import ImportExcelCommandConfig
from strictdoc.commands.import_reqif_config import ImportReqIFCommandConfig
from strictdoc.commands.manage_autouid_config import (
    ManageAutoUIDCommandConfig,
)
from strictdoc.commands.manage_new_config import ManageNewCommandConfig
from strictdoc.commands.server_config import ServerCommandConfig

ALL_COMMAND_CONFIGS = [
    ExportCommandConfig,
    FormatCommandConfig,
    ImportExcelCommandConfig,
    ImportReqIFCommandConfig,
    ManageAutoUIDCommandConfig,
    ManageNewCommandConfig,
    ServerCommandConfig,
]


def test_every_command_config_accepts_the_global_development_flag():
    """
    --development is a top-level argparse flag
    (strictdoc/cli/cli_arg_parser.py), so it is present in vars(args)
    regardless of which subcommand runs. Every *Command.__init__ builds
    its config as SomeCommandConfig(**vars(args)), and each
    *CommandConfig has a strict, non-**kwargs signature (or is a plain
    @dataclass) - a Config class missing "development" as a field raises
    TypeError: unexpected keyword argument 'development' for any command
    invoked with the flag.
    """
    for config_class in ALL_COMMAND_CONFIGS:
        if dataclasses.is_dataclass(config_class):
            field_names = {
                field.name for field in dataclasses.fields(config_class)
            }
        else:
            field_names = set(
                inspect.signature(config_class.__init__).parameters
            )
        assert "development" in field_names, config_class
