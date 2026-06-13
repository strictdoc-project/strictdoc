import os
from typing import Optional

from strictdoc.cli.base_command import CLIValidationError


class ManageNewCommandConfig:
    def __init__(
        self,
        *,
        debug: bool,
        command: str,
        subcommand: str,
        project_root_path: str,
        document_path: Optional[str],
        parent_uid_or_mid: Optional[str],
        config: Optional[str],
    ):
        self.debug: bool = debug
        self.command: str = command
        self.subcommand: str = subcommand
        self.project_root_path: str = project_root_path
        self.document_path: Optional[str] = document_path
        self.parent_uid_or_mid: Optional[str] = parent_uid_or_mid
        self._config_path: Optional[str] = config

    def get_path_to_config(self) -> str:
        path_to_input_dir: str = self.project_root_path
        if os.path.isfile(path_to_input_dir):
            path_to_input_dir = os.path.dirname(path_to_input_dir)
        return (
            self._config_path
            if self._config_path is not None
            else path_to_input_dir
        )

    def validate(self) -> None:
        if not os.path.exists(self.project_root_path):
            raise CLIValidationError(
                "Provided project root path does not exist: "
                f"{self.project_root_path}"
            )
        if self._config_path is not None and not os.path.exists(
            self._config_path
        ):
            raise CLIValidationError(
                "Provided path to a configuration file does not exist: "
                f"{self._config_path}"
            )
        if self.document_path is not None and not os.path.exists(
            self.document_path
        ):
            raise CLIValidationError(
                f"Provided --document-path does not exist: {self.document_path}"
            )
        if (
            self.parent_uid_or_mid is not None
            and len(self.parent_uid_or_mid.strip()) == 0
        ):
            raise CLIValidationError(
                "The --parent-uid-or-mid value must not be empty."
            )
