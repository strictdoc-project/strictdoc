"""
@relation(SDOC-SRS-51, scope=file)
"""

import os.path
from subprocess import CalledProcessError, CompletedProcess, TimeoutExpired, run
from typing import List, Tuple

from html2pdf4doc.main import HPDExitCode

from strictdoc.core.project_config import ProjectConfig
from strictdoc.helpers.timing import measure_performance


class PDFPrintDriverException(Exception):
    def __init__(self, exception: Exception):
        super().__init__()
        self.exception: Exception = exception

    def get_server_user_message(self) -> str:
        """
        Provide a user-friendly message that describes the underlying exception/error.
        """

        if self.is_could_not_detect_chrome():
            return "HTML2PDF could not detect an existing Chrome installation."

        if self.is_timeout_error():
            return "HTML2PDF timeout error."

        if self.is_js_success_timeout():
            return "HTML2PDF.js success timeout error."

        return "HTML2PDF internal error."

    def is_timeout_error(self) -> bool:
        return isinstance(self.exception, TimeoutExpired)

    def is_could_not_detect_chrome(self) -> bool:
        return (
            isinstance(self.exception, CalledProcessError)
            and self.exception.returncode == HPDExitCode.COULD_NOT_FIND_CHROME
        )

    def is_js_success_timeout(self) -> bool:
        return (
            isinstance(self.exception, CalledProcessError)
            and self.exception.returncode
            == HPDExitCode.DID_NOT_RECEIVE_SUCCESS_STATUS_FROM_HTML2PDF4DOC_JS
        )


class PDFPrintDriver:
    @staticmethod
    def get_pdf_from_html(
        project_config: ProjectConfig,
        paths_to_print: List[Tuple[str, str]],
    ) -> None:
        assert isinstance(paths_to_print, list), paths_to_print
        path_to_html2pdf4doc_cache = os.path.join(
            project_config.get_path_to_cache_dir(), "html2pdf"
        )
        cmd: List[str] = [
            # Using sys.executable instead of "python" is important because
            # venv subprocess call to python resolves to wrong interpreter,
            # https://github.com/python/cpython/issues/86207
            # Switching back to calling html2pdf4doc directly because the
            # python -m doesn't work well with PyInstaller.
            # sys.executable, "-m"
            "html2pdf4doc",
            "print",
            "--cache-dir",
            path_to_html2pdf4doc_cache,
        ]
        if project_config.chromedriver is not None:
            cmd.extend(
                [
                    "--chromedriver",
                    project_config.chromedriver,
                ]
            )
        if project_config.html2pdf_strict:
            cmd.append("--strict")
        for path_to_print_ in paths_to_print:
            cmd.append(path_to_print_[0])
            cmd.append(path_to_print_[1])

        with measure_performance(
            "PDFPrintDriver: printing HTML to PDF using HTML2PDF and Chrome Driver"
        ):
            try:
                _: CompletedProcess[bytes] = run(
                    cmd,
                    capture_output=False,
                    check=True,
                )
            except Exception as e_:
                raise PDFPrintDriverException(e_) from e_
