import os
from typing import Optional

from strictdoc.cli.base_command import CLIValidationError


class ManageAutoUIDCommandConfig:
    def __init__(
        self,
        *,
        debug: bool,
        command: str,
        subcommand: str,
        input_path: str,
        config: Optional[str],
        include_sections: bool,
    ):
        self.debug: bool = debug
        self.command: str = command
        self.subcommand: str = subcommand
        self.input_path: str = input_path
        self._config_path: Optional[str] = config
        self.include_sections: bool = include_sections

    def get_path_to_config(self) -> str:
        path_to_input_dir: str = self.input_path
        if os.path.isfile(path_to_input_dir):
            path_to_input_dir = os.path.dirname(path_to_input_dir)
        path_to_config = (
            self._config_path
            if self._config_path is not None
            else path_to_input_dir
        )
        return path_to_config

    def validate(self) -> None:
        if self._config_path is not None and not os.path.exists(
            self._config_path
        ):
            raise CLIValidationError(
                "Provided path to a configuration file does not exist: "
                f"{self._config_path}"
            )
