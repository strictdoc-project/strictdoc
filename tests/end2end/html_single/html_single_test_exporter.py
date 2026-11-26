"""
Runs the single-file HTML export for the end-to-end tests of html-single.

@relation(SDOC-SRS-217, scope=file)
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, Optional


class HTMLSingleTestExporter:
    def __init__(
        self, *, input_path: str, extra_args: Optional[List[str]] = None
    ) -> None:
        self.input_path: str = input_path
        self.extra_args: List[str] = extra_args or []
        self.output_path: str = tempfile.mkdtemp()

    def __enter__(self) -> "HTMLSingleTestExporter":
        # sys.executable: see SDocTestHTMLExporter.run().
        subprocess.run(
            [
                sys.executable,
                "-m",
                "strictdoc.cli.main",
                "export",
                "--formats",
                "html-single",
                "--output-dir",
                self.output_path,
                *self.extra_args,
                self.input_path,
            ],
            check=True,
            capture_output=True,
        )
        return self

    def __exit__(self, *_: object) -> None:
        shutil.rmtree(self.output_path)

    def get_file_uri(self, file_name: str) -> str:
        path = Path(self.output_path) / "html-single" / file_name
        return path.resolve().as_uri()
