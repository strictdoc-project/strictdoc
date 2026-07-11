import os
from typing import Optional

from strictdoc.helpers.auto_described import auto_described


@auto_described
class ConvertCommandConfig:
    """
    Generic, format-agnostic slice of `convert`'s CLI arguments only:
    input/output paths, --input-format/--output-format/--config. Anything
    format-specific (e.g. --excel-parser, --reqif-profile) is contributed by
    the relevant Format's own add_import_arguments() and is read directly
    off the argparse.Namespace by that same Format's import_file() -- it
    never needs to be known here, so a new custom Format never requires a
    change to this class.
    """

    def __init__(
        self,
        *,
        debug: bool,
        development: bool = False,
        command: str,
        input_path: str,
        output_path: str,
        input_format: Optional[str],
        output_format: str,
        config: Optional[str] = None,
        **_format_specific_options: object,
    ):
        self.debug: bool = debug
        self.development: bool = development
        self.command: str = command
        self.input_path: str = input_path
        self.output_path: str = output_path
        self.input_format: Optional[str] = input_format
        self.output_format: str = output_format
        self._config_path: Optional[str] = config

    def get_path_to_config(self) -> str:
        return (
            self._config_path if self._config_path is not None else os.getcwd()
        )
