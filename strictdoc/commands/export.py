import argparse
from typing import List

from strictdoc.backend.reqif.sdoc_reqif_fields import ReqIFProfile
from strictdoc.cli.base_command import BaseCommand, CLIValidationError
from strictdoc.commands._shared import _check_reqif_profile
from strictdoc.commands.export_config import ExportCommandConfig
from strictdoc.core.actions.export_action import ExportAction
from strictdoc.core.project_config import ProjectConfigLoader
from strictdoc.helpers.parallelizer import Parallelizer

EXPORT_FORMATS = [
    "html",
    "html2pdf",
    "rst",
    "json",
    "excel",
    "reqif-sdoc",
    "reqifz-sdoc",
    "sdoc",
    "doxygen",
    "spdx",
]


def _check_formats(formats: str) -> List[str]:
    formats_array = formats.split(",")
    for fmt in formats_array:
        if fmt in EXPORT_FORMATS:
            continue
        export_formats = ", ".join(map(lambda f: f"'{f}'", EXPORT_FORMATS))
        message = f"invalid choice: '{fmt}' (choose from {export_formats})"
        raise argparse.ArgumentTypeError(message)
    return formats_array


def _check_git_revisions(git_revisions: str) -> str:
    if ".." not in git_revisions:
        message = (
            "Invalid Git revision pair. "
            'The expected format is: "<Git revision>..<Git revision>". '
            'Example: "HEAD^..HEAD".'
        )
        raise argparse.ArgumentTypeError(message)
    return git_revisions


def _parse_fields(fields: str) -> List[str]:
    fields_array = fields.split(",")
    return fields_array


class ExportCommand(BaseCommand):
    HELP = "Print the version of StrictDoc."
    DETAILED_HELP = HELP

    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
        command_parser_export = parser
        command_parser_export.add_argument(
            "input_paths",
            type=str,
            nargs="+",
            help="One or more folders with *.sdoc files",
        )
        command_parser_export.add_argument(
            "--output-dir", type=str, help="Output folder"
        )
        command_parser_export.add_argument(
            "--project-title", type=str, help="Project title"
        )
        command_parser_export.add_argument(
            "--formats",
            type=_check_formats,
            default=["html"],
            help="Export formats",
        )
        command_parser_export.add_argument(
            "--fields",
            type=_parse_fields,
            default=["uid", "statement", "parent"],
            help="Export fields, only used for Excel export",
        )
        command_parser_export.add_argument(
            "--generate-bundle-document",
            action="store_true",
            default=False,
            help=(
                "EXPERIMENTAL: "
                "In addition to generating individual documents, "
                "also create a concatenated bundle that contains "
                "all the documents together."
            ),
        )
        command_parser_export.add_argument(
            "--no-parallelization",
            action="store_true",
            help=(
                "Disables parallelization. "
                "All work happens in the main thread. "
                "This option may be useful for debugging."
            ),
        )
        command_parser_export.add_argument(
            "--enable-mathjax",
            action="store_true",
            help="Enables Mathjax support (only HTML export).",
        )
        command_parser_export.add_argument(
            "--included-documents",
            action="store_true",
            help=(
                "By default the included documents are not exported. "
                "This option makes both including and included documents to be exported."
            ),
        )
        command_parser_export.add_argument(
            "--reqif-profile",
            type=_check_reqif_profile,
            default=ReqIFProfile.P01_SDOC,
            help="Export formats",
        )
        command_parser_export.add_argument(
            "--reqif-multiline-is-xhtml",
            default=False,
            action="store_true",
            help=(
                "Controls whether StrictDoc multiline fields are exported as XHTML "
                "when the option is provided. "
                "By default StrictDoc exports multiline fields with a STRING type."
            ),
        )
        command_parser_export.add_argument(
            "--reqif-enable-mid",
            default=False,
            action="store_true",
            help=(
                "Controls whether StrictDoc's MID field will be mapped to ReqIF "
                "SPEC-OBJECT's IDENTIFIER and vice versa when exporting/importing."
            ),
        )
        # FIXME: --filter-requirements will be removed in 2026.
        command_parser_export.add_argument(
            "--filter-nodes",
            "--filter-requirements",
            dest="filter_nodes",
            type=str,
            help="Filter which requirements will be exported.",
        )
        command_parser_export.add_argument(
            "--view",
            type=str,
            help="Choose which view will be exported.",
        )
        command_parser_export.add_argument(
            "--generate-diff-git",
            type=_check_git_revisions,
            help=(
                "Generate Diff/Changelog for a given pair of Git revisions. "
                'Example: --generate-diff-git "HEAD^..HEAD"'
            ),
        )
        command_parser_export.add_argument(
            "--generate-diff-dirs",
            "--generate-diff-dirs",
            metavar=("OLD_PATH", "NEW_PATH"),
            nargs=2,
            help=(
                "Generate Diff/Changelog for a given pair of local directories. "
                'Example: --generate-diff-dirs "./old_path" "./new_path"'
            ),
        )
        command_parser_export.add_argument(
            "--chromedriver",
            type=str,
            help="Path to pre installed chromedriver for html2pdf. "
            "If not given, chromedriver is downloaded and saved to "
            "strictdoc cache.",
        )
        command_parser_export.add_argument(
            "--config",
            type=str,
            help="Path to the StrictDoc TOML config file.",
        )

    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.config: ExportCommandConfig = ExportCommandConfig(**vars(args))

    def run(self, parallelizer: Parallelizer) -> None:
        export_config = self.config
        try:
            export_config.validate()
        except CLIValidationError as exception_:
            raise exception_
        project_config = ProjectConfigLoader.load_from_path_or_get_default(
            path_to_config=export_config.get_path_to_config(),
        )
        project_config.integrate_export_config(export_config)
        project_config.validate_and_finalize()

        parallelization_value = (
            "Disabled" if export_config.no_parallelization else "Enabled"
        )
        print(  # noqa: T201
            f"Parallelization: {parallelization_value}", flush=True
        )
        export_action = ExportAction(
            project_config=project_config,
            parallelizer=parallelizer,
        )
        export_action.export()
