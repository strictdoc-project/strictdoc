import argparse
from typing import NoReturn, Optional

from strictdoc.backend.reqif.sdoc_reqif_fields import ReqIFProfile
from strictdoc.backend.sdoc.constants import SDocMarkup


class _SilentArgumentParser(argparse.ArgumentParser):
    """
    For throwaway pre-parses (see e.g. export.py's/convert.py's
    _preparse_config_path()): these are inherently best-effort and fall back
    silently on failure, so they must never print their own usage/error to
    stderr -- that would duplicate (and, with the wrong `prog`) the real
    parser's own error message for the same problem.
    """

    def error(self, message: str) -> NoReturn:
        raise argparse.ArgumentError(None, message)


def _check_reqif_profile(profile: str) -> str:
    if profile not in ReqIFProfile.ALL:
        # To maintain the compatibility with the previous behavior.
        if profile == "sdoc":
            return ReqIFProfile.P01_SDOC
        valid_profiles = ", ".join(map(lambda f: f"'{f}'", ReqIFProfile.ALL))
        message = f"invalid choice: '{profile}' (choose from {valid_profiles})"
        raise argparse.ArgumentTypeError(message)
    return profile


def _check_reqif_import_markup(markup: Optional[str]) -> str:
    if markup is None or markup not in SDocMarkup.ALL:
        valid_text_markups_string = ", ".join(SDocMarkup.ALL)
        message = f"invalid choice: '{markup}' (choose from {valid_text_markups_string})"
        raise argparse.ArgumentTypeError(message)
    return markup


def add_config_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--config",
        type=str,
        help=(
            "Path to the StrictDoc config file ("
            "strictdoc_config.py preferred, strictdoc.toml legacy"
            ")."
        ),
    )
