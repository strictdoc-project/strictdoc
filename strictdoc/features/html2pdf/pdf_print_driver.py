"""
@relation(SDOC-SRS-51, scope=file)
"""

import codecs
import io
import os.path
import sys
from collections import deque
from subprocess import PIPE, CalledProcessError, Popen, TimeoutExpired
from typing import Deque, List, Tuple

from html2pdf4doc.main import HPDExitCode

from strictdoc.core.project_config import ProjectConfig
from strictdoc.features.html2pdf.pdf_postprocessor import PDFPostprocessor
from strictdoc.helpers.frozen import get_html2pdf4doc_command
from strictdoc.helpers.timing import measure_performance

# The number of html2pdf4doc's last stderr lines that are kept to explain a
# failure. A Python traceback ends with the exception message.
STDERR_TAIL_MAX_LINES = 100


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
            project_config.environment.get_path_to_user_cache_dir()
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
                returncode, stderr_tail = PDFPrintDriver.run_html2pdf4doc(cmd)
                if returncode != 0:
                    raise CalledProcessError(
                        returncode, cmd, stderr=stderr_tail
                    )
                PDFPostprocessor.rewrite_cross_document_links(
                    path_to_input_root=path_to_input_root,
                    paths_to_print=paths_to_print,
                )
            except Exception as e_:
                raise PDFPrintDriverException(e_) from e_

    @staticmethod
    def run_html2pdf4doc(cmd: List[str]) -> Tuple[int, str]:
        """
        Run html2pdf4doc and return its exit code and the last lines of its
        stderr.

        stdout goes straight to the console. stderr is passed through to the
        console as it arrives, and its last lines are kept so that a failure
        can be reported as one clear message.
        """

        stderr_tail: Deque[str] = deque(maxlen=STDERR_TAIL_MAX_LINES)
        incomplete_line = ""
        # On Windows, a Python child process writes \r\n to the pipe.
        # sys.stderr adds \r again when it writes \n, so translate \r\n to
        # \n first. The decoder also handles a \r\n split across two reads.
        decoder = io.IncrementalNewlineDecoder(
            codecs.getincrementaldecoder("utf-8")(errors="replace"),
            translate=True,
        )
        with Popen(cmd, stderr=PIPE) as process:
            assert process.stderr is not None
            while True:
                chunk = os.read(process.stderr.fileno(), 65536)
                text = decoder.decode(chunk, final=len(chunk) == 0)
                if len(text) > 0:
                    sys.stderr.write(text)
                    sys.stderr.flush()
                    lines = (incomplete_line + text).split("\n")
                    incomplete_line = lines.pop()
                    stderr_tail.extend(lines)
                if len(chunk) == 0:
                    break
            returncode = process.wait()
        if len(incomplete_line) > 0:
            stderr_tail.append(incomplete_line)
        return returncode, "\n".join(stderr_tail)
