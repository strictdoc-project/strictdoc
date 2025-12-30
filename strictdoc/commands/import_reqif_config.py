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
