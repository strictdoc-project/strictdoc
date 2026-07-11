import argparse
import os
import sys
from typing import List, Optional

from strictdoc.cli.base_command import BaseCommand
from strictdoc.commands._shared import (
    _SilentArgumentParser,
    add_config_argument,
)
from strictdoc.commands.convert_config import ConvertCommandConfig
from strictdoc.core.actions.convert_action import ConvertAction
from strictdoc.core.project_config import ProjectConfig, ProjectConfigLoader
from strictdoc.helpers.parallelizer import Parallelizer


def _preparse_config_path() -> Optional[str]:
    """
    Best-effort pre-parse of sys.argv to discover --config's value (if any)
    before the real argparse parse happens. Only --config is extracted here
    -- unlike a full mirror of ConvertCommand's own arguments -- since that's
    all _load_project_config_for_preparse() below needs, and it keeps this
    independent of which Format-contributed flags exist (see
    add_arguments()), avoiding any recursion between the two.
    """
    try:
        convert_index = next(
            i
            for i, token in enumerate(sys.argv[1:], start=1)
            if token == "convert"
        )
    except StopIteration:
        return None

    pre_parser = _SilentArgumentParser(add_help=False)
    add_config_argument(pre_parser)
    try:
        pre_args, _ = pre_parser.parse_known_args(sys.argv[convert_index + 1 :])
    except (SystemExit, argparse.ArgumentError):
        return None

    return str(pre_args.config) if pre_args.config is not None else None


def _load_project_config_for_preparse() -> ProjectConfig:
    config_path = _preparse_config_path()
    if config_path is None:
        config_path = os.getcwd()
    try:
        return ProjectConfigLoader.load_from_path_or_get_default(
            path_to_config=config_path
        )
    except Exception:
        # A broken config surfaces properly later, when ConvertCommand.run()
        # loads it for real.
        return ProjectConfig.default_config()


def _get_allowed_input_format_handles() -> List[str]:
    allowed_handles: List[str] = []
    project_config = _load_project_config_for_preparse()
    for format_ in project_config.formats:
        if not format_.supports_import():
            continue
        for handle_ in format_.handles():
            if handle_ not in allowed_handles:
                allowed_handles.append(handle_)
    return allowed_handles


def _get_allowed_output_format_handles() -> List[str]:
    allowed_handles: List[str] = []
    project_config = _load_project_config_for_preparse()
    for format_ in project_config.formats:
        if not format_.supports_convert_output():
            continue
        for handle_ in format_.handles():
            if handle_ not in allowed_handles:
                allowed_handles.append(handle_)
    return allowed_handles


def _check_input_format(input_format: str) -> str:
    allowed_handles = _get_allowed_input_format_handles()
    if input_format in allowed_handles:
        return input_format
    choices = ", ".join(f"'{f}'" for f in allowed_handles)
    message = f"invalid choice: '{input_format}' (choose from {choices})"
    raise argparse.ArgumentTypeError(message)


def _check_output_format(output_format: str) -> str:
    allowed_handles = _get_allowed_output_format_handles()
    if output_format in allowed_handles:
        return output_format
    choices = ", ".join(f"'{f}'" for f in allowed_handles)
    message = f"invalid choice: '{output_format}' (choose from {choices})"
    raise argparse.ArgumentTypeError(message)


class ConvertCommand(BaseCommand):
    HELP = (
        "Convert a document from one format to another "
        "(e.g. Excel/ReqIF -> SDoc)."
    )
    DETAILED_HELP = HELP

    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "input_path",
            type=str,
            help="Path to the input file.",
        )
        parser.add_argument(
            "output_path",
            type=str,
            help="Path to the output directory.",
        )
        parser.add_argument(
            "--input-format",
            type=_check_input_format,
            default=None,
            help=(
                "Input format. Auto-discovered from the input file's "
                "extension if not given."
            ),
        )
        parser.add_argument(
            "--output-format",
            type=_check_output_format,
            default="sdoc",
            help="Output format.",
        )
        add_config_argument(parser)

        # Each import-capable Format contributes its own CLI flags (e.g.
        # ExcelFormat's --excel-parser, ReqIFFormat's --reqif-profile). A
        # custom Format registered via the project config gets its flags
        # added here too, without any change to ConvertCommand/
        # ConvertCommandConfig. Only attempted when "convert" is actually
        # being run -- this same `add_arguments` is invoked for every
        # command's subparser construction on every CLI invocation (e.g.
        # `strictdoc version`), and there is no reason to load a project
        # config for those.
        if "convert" in sys.argv:
            project_config = _load_project_config_for_preparse()
            for format_ in project_config.formats:
                if format_.supports_import():
                    format_.add_import_arguments(parser)

    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.config: ConvertCommandConfig = ConvertCommandConfig(**vars(args))

    def run(self, parallelizer: Parallelizer) -> None:  # noqa: ARG002
        project_config = ProjectConfigLoader.load_using_convert_config(
            self.config
        )
        convert_action = ConvertAction()
        convert_action.do_convert(self.args, self.config, project_config)
