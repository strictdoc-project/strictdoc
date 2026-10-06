"""
@relation(SDOC-SRS-51, scope=file)
"""

import os.path
import sys
from subprocess import (
    PIPE,
    CalledProcessError,
    CompletedProcess,
    TimeoutExpired,
    run,
)
from typing import List, Tuple

from html2pdf4doc.main import HPDExitCode

from strictdoc import environment
from strictdoc.core.project_config import ProjectConfig
from strictdoc.features.html2pdf.pdf_postprocessor import PDFPostprocessor
from strictdoc.helpers.frozen import get_html2pdf4doc_command
from strictdoc.helpers.timing import measure_performance
from strictdoc.helpers.user_cache_dir import get_user_cache_dir


class PDFPrintDriverException(Exception):
    CHROME_NOT_FOUND_MESSAGE = (
        "HTML2PDF: Chrome/Chromium not found. Install Google Chrome, or pass "
        "--chrome-binary PATH or set HTML2PDF4DOC_CHROME_BINARY."
    )
    CHROMEDRIVER_DOWNLOAD_FAILED_MESSAGE = (
        "HTML2PDF: could not download ChromeDriver (no network connection?). "
        "Connect to the internet once so that it gets cached, or pass "
        "--chromedriver PATH."
    )

    def __init__(self, exception: Exception):
        self.exception: Exception = exception
        super().__init__(self.get_server_user_message())

    def get_server_user_message(self) -> str:
        """
        Provide a user-friendly message that describes the underlying exception/error.
        """

        if self.is_could_not_detect_chrome():
            return self.CHROME_NOT_FOUND_MESSAGE

        if self.is_chromedriver_download_error():
            return self.CHROMEDRIVER_DOWNLOAD_FAILED_MESSAGE

        if self.is_timeout_error():
            return "HTML2PDF timeout error."

        if self.is_js_success_timeout():
            return "HTML2PDF.js success timeout error."

        # The last line of html2pdf4doc's stderr is usually the exception
        # message, e.g. "RuntimeError: ...". A frozen binary's bootloader
        # adds a "[PYI-<pid>:ERROR] Failed to execute script" line after it.
        stderr_lines = [
            line_
            for line_ in self.get_stderr().splitlines()
            if len(line_.strip()) > 0 and not line_.startswith("[PYI-")
        ]
        if len(stderr_lines) > 0:
            return f"HTML2PDF internal error: {stderr_lines[-1].strip()}"
        return "HTML2PDF internal error."

    def get_stderr(self) -> str:
        if isinstance(self.exception, CalledProcessError) and isinstance(
            self.exception.stderr, str
        ):
            return self.exception.stderr
        return ""

    def is_chromedriver_download_error(self) -> bool:
        stderr = self.get_stderr()
        return (
            "GET request failed" in stderr
            or "Could not download" in stderr
            or "requests.exceptions.ConnectionError" in stderr
        )

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
        path_to_input_root: str,
    ) -> None:
        assert isinstance(paths_to_print, list), paths_to_print
        # The ChromeDriver only depends on the installed Chrome, so unless the
        # project config sets a cache folder, keep it in the per-user cache
        # instead of downloading it again for every output folder.
        path_to_html2pdf4doc_cache = os.path.join(
            get_user_cache_dir()
            if project_config.is_default_dir_for_sdoc_cache
            else project_config.get_path_to_cache_dir(),
            "html2pdf",
        )
        cmd: List[str] = [
            # Using sys.executable instead of "python" is important because
            # venv subprocess call to python resolves to wrong interpreter,
            # https://github.com/python/cpython/issues/86207
            # Switching back to calling html2pdf4doc directly because the
            # python -m doesn't work well with PyInstaller.
            # sys.executable, "-m"
            # A frozen binary has no html2pdf4doc on PATH, so it re-invokes
            # itself with an internal helper command instead.
            *get_html2pdf4doc_command(),
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
        if project_config.chrome_binary is not None:
            cmd.extend(
                [
                    "--chrome-binary",
                    project_config.chrome_binary,
                ]
            )
        if project_config.html2pdf_disable_ssl_check:
            cmd.append("--disable-ssl-check")
        if project_config.html2pdf_strict:
            cmd.append("--strict")
        for path_to_print_ in paths_to_print:
            cmd.append(path_to_print_[0])
            cmd.append(path_to_print_[1])

        with measure_performance(
            "PDFPrintDriver: printing HTML to PDF using HTML2PDF and Chrome Driver"
        ):
            try:
                # stdout goes straight to the console. stderr is captured so
                # that a failure is reported as one clear message instead of
                # html2pdf4doc's traceback (shown with --debug).
                completed_process: CompletedProcess[str] = run(
                    cmd,
                    stderr=PIPE,
                    encoding="utf-8",
                    errors="replace",
                    check=False,
                )
                if completed_process.returncode != 0:
                    if environment.is_debug_mode:
                        sys.stderr.write(completed_process.stderr)
                    raise CalledProcessError(
                        completed_process.returncode,
                        cmd,
                        stderr=completed_process.stderr,
                    )
                sys.stderr.write(completed_process.stderr)
                PDFPostprocessor.rewrite_cross_document_links(
                    path_to_input_root=path_to_input_root,
                    paths_to_print=paths_to_print,
                )
            except Exception as e_:
                raise PDFPrintDriverException(e_) from e_
