"""
@relation(SDOC-LLR-208, scope=file)
"""

import argparse
from pathlib import Path
from typing import Dict, List, Tuple

from strictdoc.cli.base_command import BaseCommand, CLIValidationError
from strictdoc.helpers.mid import MID
from strictdoc.helpers.parallelizer import Parallelizer


class NewCommand(BaseCommand):
    HELP = "Create an initial StrictDoc project."
    DETAILED_HELP = HELP

    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "input_path",
            type=str,
            help="Folder where the initial StrictDoc project is created.",
        )

    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args

    def run(self, parallelizer: Parallelizer) -> None:  # noqa: ARG002
        output_path = Path(self.args.input_path)
        if output_path.exists() and not output_path.is_dir():
            raise CLIValidationError(
                "error: "
                "Provided path exists and is not a directory: "
                f"'{output_path}'"
            )

        directories, files = self._get_template_files(output_path)
        conflicts = [
            directory
            for directory in directories
            if directory.exists() and not directory.is_dir()
        ]
        conflicts.extend(file_path for file_path in files if file_path.exists())
        if conflicts:
            conflict_list = "\n".join(f"- {path}" for path in conflicts)
            raise CLIValidationError(
                "Refusing to overwrite existing StrictDoc project files:\n"
                f"{conflict_list}"
            )

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

        for file_path, content in files.items():
            file_path.write_text(content, encoding="utf-8")

        print(  # noqa: T201
            f"""\
╔════════════════════════════════════════════════════════════╗
║            StrictDoc project skeleton created              ║
╚════════════════════════════════════════════════════════════╝

Location: {output_path}

Next steps:

1. Change into the project directory

   cd {output_path}

2. Export static HTML documentation

   strictdoc export .

3. Start the web server

   strictdoc server .
"""
        )

    @staticmethod
    def _get_template_files(
        output_path: Path,
    ) -> Tuple[List[Path], Dict[Path, str]]:
        docs_path = output_path / "docs"
        src_path = output_path / "src"
        hlr_document_mid = MID.create()
        hlr_requirement_mid = MID.create()
        llr_document_mid = MID.create()
        llr_requirement_mid = MID.create()
        return [output_path, docs_path, src_path], {
            docs_path / "high_level_requirements.sdoc": (
                f"""\
[DOCUMENT]
MID: {hlr_document_mid}
TITLE: High-Level Requirements
PREFIX: HLR-
OPTIONS:
  ENABLE_MID: True

[REQUIREMENT]
MID: {hlr_requirement_mid}
UID: HLR-1
TITLE: Initial high-level requirement
STATEMENT: >>>
The system shall provide a hello world application.
<<<
"""
            ),
            docs_path / "low_level_requirements.sdoc": (
                f"""\
[DOCUMENT]
MID: {llr_document_mid}
TITLE: Low-Level Requirements
PREFIX: LLR-
OPTIONS:
  ENABLE_MID: True

[REQUIREMENT]
MID: {llr_requirement_mid}
UID: LLR-1
TITLE: Initial low-level requirement
STATEMENT: >>>
The software shall print a hello world message.
<<<
RELATIONS:
- TYPE: Parent
  VALUE: HLR-1
"""
            ),
            src_path / "main.c": (
                """\
/**
* @relation(LLR-1, scope=file)
*/
#include <stdio.h>

int main(void)
{
    printf("Hello, StrictDoc!\\n");
    return 0;
}
"""
            ),
            output_path / "strictdoc_config.py": (
                """\
from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    return ProjectConfig(
        project_title="Hello World",
        project_features=[
            # Stable features.
            "TABLE_SCREEN",
            "TRACEABILITY_SCREEN",
            "DEEP_TRACEABILITY_SCREEN",
            "SEARCH",
            "TRACEABILITY_MATRIX_SCREEN",
            "REQUIREMENT_TO_SOURCE_TRACEABILITY",
            # "MATHJAX"

            # Experimental features.
            # "PROJECT_STATISTICS_SCREEN",
            # "TREE_MAP_SCREEN",
            # "REQIF",
            # "HTML2PDF",
            # "DIFF",
        ],
        include_doc_paths=[
            "/docs/",
        ],
        include_source_paths=[
            "/src/**",
        ],
    )
"""
            ),
        }
