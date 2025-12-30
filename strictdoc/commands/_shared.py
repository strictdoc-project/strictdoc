import argparse

from strictdoc.backend.reqif.sdoc_reqif_fields import ReqIFProfile


def _check_reqif_profile(profile: str) -> str:
    if profile not in ReqIFProfile.ALL:
        # To maintain the compatibility with the previous behavior.
        if profile == "sdoc":
            return ReqIFProfile.P01_SDOC
        valid_profiles = ", ".join(map(lambda f: f"'{f}'", ReqIFProfile.ALL))
        message = f"invalid choice: '{profile}' (choose from {valid_profiles})"
        raise argparse.ArgumentTypeError(message)
    return profile


def add_config_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--config",
        type=str,
        help="Path to the StrictDoc TOML config file.",
    )
