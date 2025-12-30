import argparse
import os
from typing import Optional

from strictdoc.backend.reqif.sdoc_reqif_fields import ReqIFProfile
from strictdoc.backend.sdoc.constants import SDocMarkup
from strictdoc.cli.base_command import BaseCommand
from strictdoc.commands._shared import _check_reqif_profile
from strictdoc.commands.import_reqif_config import ImportReqIFCommandConfig
from strictdoc.core.actions.import_action import ImportAction
from strictdoc.core.project_config import ProjectConfigLoader
from strictdoc.helpers.parallelizer import Parallelizer


def _check_reqif_import_markup(markup: Optional[str]) -> str:
    if markup is None or markup not in SDocMarkup.ALL:
        valid_text_markups_string = ", ".join(SDocMarkup.ALL)
        message = f"invalid choice: '{markup}' (choose from {valid_text_markups_string})"
        raise argparse.ArgumentTypeError(message)
    return markup


class ImportReqIFCommand(BaseCommand):
    HELP = "Create StrictDoc file from ReqIF document."
    DETAILED_HELP = HELP

    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "profile",
            type=_check_reqif_profile,
            help=(
                "An argument that selects the ReqIF import/export profile. "
                f"Possible values: {{{', '.join(ReqIFProfile.ALL)}}}"
            ),
        )
        parser.add_argument(
            "input_path",
            type=str,
            help="Path to the input ReqIF file.",
        )
        parser.add_argument(
            "output_path",
            type=str,
            help="Path to the output SDoc file.",
        )
        parser.add_argument(
            "--reqif-enable-mid",
            default=False,
            action="store_true",
            help=(
                "Controls whether StrictDoc's MID field will be mapped to ReqIF "
                "SPEC-OBJECT's IDENTIFIER and vice versa when exporting/importing."
            ),
        )
        parser.add_argument(
            "--reqif-import-markup",
            default=None,
            type=_check_reqif_import_markup,
            help=(
                "Controls which MARKUP option the imported SDoc documents will have. "
                "This value is RST as what StrictDoc has by default but very often "
                "the requirements tools use the (X)HTML markup for multiline fields in "
                "which case HTML is the best option."
            ),
        )

    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.config: ImportReqIFCommandConfig = ImportReqIFCommandConfig(
            **vars(args)
        )

    def run(self, parallelizer: Parallelizer) -> None:  # noqa: ARG002
        project_config = ProjectConfigLoader.load_from_path_or_get_default(
            path_to_config=os.getcwd(),
        )

        import_action = ImportAction()
        import_action.do_import(self.config, project_config)
