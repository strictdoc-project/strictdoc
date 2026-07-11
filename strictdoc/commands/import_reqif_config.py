import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class ImportReqIFCommandConfig:
    debug: bool
    command: str
    subcommand: str
    input_path: str
    output_path: str
    profile: str
    reqif_enable_mid: bool
    reqif_import_markup: Optional[str]
    config: Optional[str] = None
    development: bool = False

    def get_path_to_config(self) -> str:
        return self.config if self.config is not None else os.getcwd()
