import os
from typing import Optional

from strictdoc.cli.base_command import CLIValidationError


class ManageAssetsCommandConfig:
    def __init__(
        self,
        *,
        debug: bool,
        command: str,
        subcommand: str,
        input_path: str,
        config: Optional[str],
        clean_unused_images: bool,
    ):
        self.debug: bool = debug
        self.command: str = command
        self.subcommand: str = subcommand
        self.input_path: str = input_path
        self._config_path: Optional[str] = config
        self.clean_unused_images: bool = clean_unused_images

    def validate(self) -> None:
        if not os.path.exists(self.input_path):
            raise CLIValidationError(
                f"Provided input path does not exist: {self.input_path}"
            )

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
