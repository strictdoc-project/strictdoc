from dataclasses import dataclass


@dataclass
class ImportExcelCommandConfig:
    debug: bool
    command: str
    subcommand: str
    parser: str
    input_path: str
    output_path: str
