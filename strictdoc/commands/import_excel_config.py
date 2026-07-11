import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class ImportExcelCommandConfig:
    debug: bool
    command: str
    subcommand: str
    parser: str
    input_path: str
    output_path: str
    config: Optional[str] = None
    development: bool = False

    def get_path_to_config(self) -> str:
        return self.config if self.config is not None else os.getcwd()
