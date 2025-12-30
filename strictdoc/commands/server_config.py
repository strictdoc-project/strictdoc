import os
from typing import Optional

from strictdoc.cli.base_command import CLIValidationError
from strictdoc.helpers.auto_described import auto_described
from strictdoc.helpers.net import is_valid_host


@auto_described
class ServerCommandConfig:
    def __init__(
        self,
        *,
        debug: bool,
        command: str,
        input_path: str,
        output_path: Optional[str],
        config: Optional[str],
        reload: bool,
        host: Optional[str],
        port: Optional[int],
    ):
        self.debug: bool = debug
        self.command: str = command
        self._input_path: str = input_path
        self.output_path: Optional[str] = output_path
        self._config_path: Optional[str] = config
        self.reload: bool = reload
        self.host: Optional[str] = host
        self.port: Optional[int] = port

    def get_full_input_path(self) -> str:
        return os.path.abspath(self._input_path)

    def get_path_to_config(self) -> str:
        return (
            self._config_path
            if self._config_path is not None
            else self._input_path
        )

    def validate(self) -> None:
        if not os.path.exists(self._input_path):
            raise CLIValidationError(
                f"Provided input path does not exist: {self._input_path}"
            )

        if self._config_path is not None and not os.path.exists(
            self._config_path
        ):
            raise CLIValidationError(
                "Provided path to a configuration file does not exist: "
                f"{self._config_path}"
            )

        if (host_ := self.host) is not None:
            if not is_valid_host(host_):
                raise CLIValidationError(
                    f"Provided 'host' argument is not a valid host: {host_}"
                )
