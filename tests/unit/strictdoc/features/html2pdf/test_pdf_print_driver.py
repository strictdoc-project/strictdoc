import os
import sys
from subprocess import CalledProcessError
from typing import List, Tuple

import pytest
from html2pdf4doc.main import HPDExitCode

from strictdoc.core.project_config import ProjectConfig
from strictdoc.features.html2pdf import pdf_print_driver
from strictdoc.features.html2pdf.pdf_print_driver import (
    STDERR_TAIL_MAX_LINES,
    PDFPrintDriver,
    PDFPrintDriverException,
)
from strictdoc.helpers.user_cache_dir import get_user_cache_dir

DOWNLOAD_FAILED_STDERR = """\
Traceback (most recent call last):
  File "html2pdf4doc/main.py", line 1, in get_chrome_driver
requests.exceptions.ConnectionError: HTTPSConnectionPool(host='example.com')
RuntimeError: GET request failed: https://example.com/LATEST_RELEASE
"""


@pytest.fixture(name="home")
def fixture_home(monkeypatch, tmp_path):
    home = str(tmp_path / "home")
    # os.path.expanduser() reads HOME on POSIX and USERPROFILE on Windows.
    monkeypatch.setenv("HOME", home)
    monkeypatch.setenv("USERPROFILE", home)
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
    monkeypatch.delenv("LOCALAPPDATA", raising=False)
    monkeypatch.delenv("STRICTDOC_CACHE_DIR", raising=False)
    return home


def get_html2pdf4doc_cache_dir(
    monkeypatch, project_config: ProjectConfig
) -> str:
    commands: List[List[str]] = []

    def run_html2pdf4doc(cmd: List[str]) -> Tuple[int, str]:
        commands.append(cmd)
        return 0, ""

    monkeypatch.setattr(PDFPrintDriver, "run_html2pdf4doc", run_html2pdf4doc)
    monkeypatch.setattr(
        pdf_print_driver.PDFPostprocessor,
        "rewrite_cross_document_links",
        lambda **_: None,
    )
    PDFPrintDriver.get_pdf_from_html(
        project_config, [("input.html", "input.pdf")], "."
    )
    assert len(commands) == 1
    cmd = commands[0]
    return cmd[cmd.index("--cache-dir") + 1]


def test_01_user_cache_dir_linux(monkeypatch, home, tmp_path):
    monkeypatch.setattr(sys, "platform", "linux")
    assert get_user_cache_dir() == os.path.join(home, ".cache", "strictdoc")

    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "xdg"))
    assert get_user_cache_dir() == os.path.join(
        str(tmp_path / "xdg"), "strictdoc"
    )


def test_02_user_cache_dir_windows(monkeypatch, home, tmp_path):
    monkeypatch.setattr(sys, "platform", "win32")
    assert get_user_cache_dir() == os.path.join(
        home, "AppData", "Local", "strictdoc", "cache"
    )

    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "local"))
    assert get_user_cache_dir() == os.path.join(
        str(tmp_path / "local"), "strictdoc", "cache"
    )


def test_03_user_cache_dir_macos(monkeypatch, home):
    monkeypatch.setattr(sys, "platform", "darwin")
    assert get_user_cache_dir() == os.path.join(
        home, "Library", "Caches", "strictdoc"
    )


@pytest.mark.usefixtures("home")
def test_10_default_config_uses_the_user_cache_dir(monkeypatch):
    project_config = ProjectConfig.default_config()
    assert project_config.is_default_dir_for_sdoc_cache

    assert get_html2pdf4doc_cache_dir(
        monkeypatch, project_config
    ) == os.path.join(get_user_cache_dir(), "html2pdf")


@pytest.mark.usefixtures("home")
def test_11_configured_cache_dir_is_used(monkeypatch, tmp_path):
    project_config = ProjectConfig(dir_for_sdoc_cache=str(tmp_path / "cache"))
    assert not project_config.is_default_dir_for_sdoc_cache

    assert get_html2pdf4doc_cache_dir(
        monkeypatch, project_config
    ) == os.path.join(project_config.get_path_to_cache_dir(), "html2pdf")


@pytest.mark.usefixtures("home")
def test_12_cache_dir_from_environment_is_used(monkeypatch):
    monkeypatch.setenv("STRICTDOC_CACHE_DIR", "Output/_cache")
    project_config = ProjectConfig.default_config()
    assert not project_config.is_default_dir_for_sdoc_cache


def test_20_message_when_chrome_is_not_found():
    exception = PDFPrintDriverException(
        CalledProcessError(
            HPDExitCode.COULD_NOT_FIND_CHROME,
            ["html2pdf4doc"],
            stderr="error: could not find Chrome",
        )
    )
    assert (
        exception.get_server_user_message()
        == PDFPrintDriverException.CHROME_NOT_FOUND_MESSAGE
    )
    assert str(exception) == PDFPrintDriverException.CHROME_NOT_FOUND_MESSAGE


def test_21_message_when_chromedriver_download_fails():
    exception = PDFPrintDriverException(
        CalledProcessError(1, ["html2pdf4doc"], stderr=DOWNLOAD_FAILED_STDERR)
    )
    assert (
        exception.get_server_user_message()
        == PDFPrintDriverException.CHROMEDRIVER_DOWNLOAD_FAILED_MESSAGE
    )


def test_22_message_shows_the_last_stderr_line():
    exception = PDFPrintDriverException(
        CalledProcessError(
            1,
            ["html2pdf4doc"],
            stderr=(
                "Traceback (most recent call last):\n"
                "ValueError: something else\n"
                "[PYI-123:ERROR] Failed to execute script 'main'\n"
            ),
        )
    )
    assert (
        exception.get_server_user_message()
        == "HTML2PDF internal error: ValueError: something else"
    )


@pytest.mark.usefixtures("home")
def test_23_failed_print_raises_with_the_message(monkeypatch):
    monkeypatch.setattr(
        PDFPrintDriver,
        "run_html2pdf4doc",
        lambda _: (1, DOWNLOAD_FAILED_STDERR),
    )
    with pytest.raises(PDFPrintDriverException) as exception_info:
        PDFPrintDriver.get_pdf_from_html(
            ProjectConfig.default_config(), [("input.html", "input.pdf")], "."
        )
    assert (
        str(exception_info.value)
        == PDFPrintDriverException.CHROMEDRIVER_DOWNLOAD_FAILED_MESSAGE
    )


def test_30_stderr_is_passed_through_and_its_tail_is_kept(capfd):
    script = (
        "import sys\n"
        "for i in range(150):\n"
        "    sys.stderr.write(f'line {i}\\n')\n"
        "sys.stderr.write('last line without a newline')\n"
        "sys.exit(3)\n"
    )
    returncode, stderr_tail = PDFPrintDriver.run_html2pdf4doc(
        [sys.executable, "-c", script]
    )

    assert returncode == 3
    tail_lines = stderr_tail.splitlines()
    assert len(tail_lines) == STDERR_TAIL_MAX_LINES
    assert tail_lines[-2] == "line 149"
    assert tail_lines[-1] == "last line without a newline"

    captured_stderr = capfd.readouterr().err
    assert "line 0\n" in captured_stderr
    assert captured_stderr.endswith("line 149\nlast line without a newline")
