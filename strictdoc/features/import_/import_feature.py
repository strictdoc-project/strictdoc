import argparse
import os
import sys
from typing import Any, Dict, Optional, Type

from strictdoc.backend.excel.export.excel_format import ExcelFormat
from strictdoc.backend.reqif.reqif_format import ReqIFFormat
from strictdoc.commands._shared import add_config_argument
from strictdoc.commands.import_excel import ImportExcelCommand
from strictdoc.commands.import_reqif import ImportReqIFCommand
from strictdoc.core.format import Format
from strictdoc.core.project_config import ProjectConfig, ProjectConfigLoader

# Maps a Format class supporting import to the CLI command class that wires
# it up to `strictdoc import <name>`. Formats supporting import without an
# entry here are not exposed as CLI subcommands.
IMPORT_FORMAT_TO_COMMAND: Dict[Type[Format], Any] = {
    ExcelFormat: ImportExcelCommand,
    ReqIFFormat: ImportReqIFCommand,
}


class ImportFeature:
    @staticmethod
    def _preparse_import_config_path() -> Optional[str]:
        """
        Best-effort pre-parse of sys.argv to discover the project config path
        before the "import" family's subcommands (and therefore its --config
        argument) even exist -- the set of available import subcommands is
        itself derived from the project config's Formats, so the config path
        must be known first.
        """
        try:
            import_index = next(
                i
                for i, token in enumerate(sys.argv[1:], start=1)
                if token == "import"
            )
        except StopIteration:
            return None

        pre_parser = argparse.ArgumentParser(add_help=False)
        add_config_argument(pre_parser)
        try:
            pre_args, _ = pre_parser.parse_known_args(
                sys.argv[import_index + 1 :]
            )
        except (SystemExit, argparse.ArgumentError):
            return None

        return str(pre_args.config) if pre_args.config is not None else None

    @classmethod
    def get_import_family_registry(cls) -> Dict[str, Any]:
        path_to_config = cls._preparse_import_config_path()
        if path_to_config is None:
            path_to_config = os.getcwd()

        try:
            project_config = ProjectConfigLoader.load_from_path_or_get_default(
                path_to_config=path_to_config
            )
        except Exception:
            # A broken config surfaces properly later, when the chosen
            # import subcommand actually loads it for real.
            project_config = ProjectConfig.default_config()

        import_family: Dict[str, Any] = {}
        for format_ in project_config.formats:
            if not format_.supports_import():
                continue
            command_cls = IMPORT_FORMAT_TO_COMMAND.get(type(format_))
            if command_cls is None:
                continue
            import_family[format_.import_command_name()] = command_cls
        return import_family
