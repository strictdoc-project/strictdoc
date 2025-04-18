import os
import shutil
import subprocess
import tempfile
from contextlib import ExitStack
from pathlib import Path
from time import sleep
from typing import Optional

from strictdoc.helpers.file_system import get_portable_temp_dir
from tests.end2end.conftest import test_environment


class SDocTestHTMLExporter:
    def __init__(
        self,
        *,
        input_path: str,
        output_path: Optional[str] = None,
        config_path: Optional[str] = None,
    ):
        assert os.path.isdir(input_path)
        if config_path is not None:
            assert os.path.exists(config_path)
        if output_path is not None:
            assert os.path.exists(output_path)
            self.cleanup_output_path = False
        else:
            output_path = tempfile.mkdtemp()
            self.cleanup_output_path = True

        self.path_to_tdoc_folder = input_path
        self.output_path: str = output_path
        self.config_path: Optional[str] = config_path

        path_to_tmp_dir = get_portable_temp_dir()
        self.path_to_out_log = os.path.join(
            path_to_tmp_dir, "strictdoc_export.out.log"
        )
        self.path_to_err_log = os.path.join(
            path_to_tmp_dir, "strictdoc_export.err.log"
        )
        self.exit_stack = ExitStack()

    def __enter__(self) -> "SDocTestHTMLExporter":
        self.run()
        return self

    def __exit__(
        self, type__, reason_exception: Optional[Exception], traceback
    ) -> None:
        self.close()

    def run(self) -> None:
        args = [
            "python",
            "strictdoc/cli/main.py",
            "export",
        ]
        if self.config_path:
            args.extend(["--config", self.config_path])
        if self.output_path is not None:
            args.extend(
                [
                    "--output-dir",
                    self.output_path,
                ]
            )
        args.extend([self.path_to_tdoc_folder])

        self.log_file_out = open(  # pylint: disable=consider-using-with
            self.path_to_out_log, "wb"
        )
        self.log_file_err = open(  # pylint: disable=consider-using-with
            self.path_to_err_log, "wb"
        )
        self.exit_stack.enter_context(self.log_file_out)
        self.exit_stack.enter_context(self.log_file_err)

        process = subprocess.run(  # pylint: disable=consider-using-with
            args,
            check=True,
            stdout=self.log_file_out.fileno(),
            stderr=self.log_file_err.fileno(),
            shell=False,
        )
        self.process = process

        sleep(test_environment.warm_up_interval_seconds)
        print(  # noqa: T201
            f"SDocTestHTMLExporter: "
            f"Static HTML sucessfully exported to : {self.output_path}."
        )

    def get_output_path_as_uri(self) -> str:
        html_folder = Path(self.output_path) / "html"
        return html_folder.resolve().as_uri() + "/"

    def close(self) -> None:
        self.exit_stack.close()
        self.process = None

        if self.output_path is not None and self.cleanup_output_path:
            shutil.rmtree(self.output_path)
