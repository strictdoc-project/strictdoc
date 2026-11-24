import os
import sys
from pathlib import Path

from pytest import MonkeyPatch, fixture

from strictdoc.core.environment import (
    BINARY_HTML_STATIC_DIR,
    BINARY_HTML_TEMPLATES_DIR,
    SDocRuntimeEnvironment,
)


def test_get_path_to_html_templates_for_pyinstaller(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    bundle_dir = tmp_path / "pyinstaller_bundle"
    monkeypatch.setattr(sys, "_MEIPASS", str(bundle_dir), raising=False)

    environment = SDocRuntimeEnvironment.__new__(SDocRuntimeEnvironment)
    environment.is_py_installer = True
    environment.is_nuitka = False
    environment.is_binary_dist = True
    environment.path_to_strictdoc = str(bundle_dir)

    assert environment.get_path_to_html_templates() == [
        os.path.join(str(bundle_dir), BINARY_HTML_TEMPLATES_DIR),
    ]

    assert environment.get_static_files_paths() == [
        os.path.join(str(bundle_dir), BINARY_HTML_STATIC_DIR),
    ]


def test_get_path_to_html_templates_for_nuitka(tmp_path: Path) -> None:
    dist_dir = tmp_path / "main.dist"

    environment = SDocRuntimeEnvironment.__new__(SDocRuntimeEnvironment)
    environment.is_py_installer = False
    environment.is_nuitka = True
    environment.is_binary_dist = True
    environment.path_to_strictdoc = str(dist_dir)

    assert environment.get_path_to_html_templates() == [
        os.path.join(str(dist_dir), BINARY_HTML_TEMPLATES_DIR),
    ]

    assert environment.get_static_files_paths() == [
        os.path.join(str(dist_dir), BINARY_HTML_STATIC_DIR),
    ]


@fixture(name="home")
def fixture_home(monkeypatch: MonkeyPatch, tmp_path: Path) -> str:
    home = str(tmp_path / "home")
    # os.path.expanduser() reads HOME on POSIX and USERPROFILE on Windows.
    monkeypatch.setenv("HOME", home)
    monkeypatch.setenv("USERPROFILE", home)
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
    monkeypatch.delenv("LOCALAPPDATA", raising=False)
    return home


def test_get_path_to_user_cache_dir_on_linux(
    monkeypatch: MonkeyPatch, home: str, tmp_path: Path
) -> None:
    monkeypatch.setattr(sys, "platform", "linux")
    assert SDocRuntimeEnvironment.get_path_to_user_cache_dir() == os.path.join(
        home, ".cache", "strictdoc"
    )

    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "xdg"))
    assert SDocRuntimeEnvironment.get_path_to_user_cache_dir() == os.path.join(
        str(tmp_path / "xdg"), "strictdoc"
    )


def test_get_path_to_user_cache_dir_on_windows(
    monkeypatch: MonkeyPatch, home: str, tmp_path: Path
) -> None:
    monkeypatch.setattr(sys, "platform", "win32")
    assert SDocRuntimeEnvironment.get_path_to_user_cache_dir() == os.path.join(
        home, "AppData", "Local", "strictdoc", "cache"
    )

    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "local"))
    assert SDocRuntimeEnvironment.get_path_to_user_cache_dir() == os.path.join(
        str(tmp_path / "local"), "strictdoc", "cache"
    )


def test_get_path_to_user_cache_dir_on_macos(
    monkeypatch: MonkeyPatch, home: str
) -> None:
    monkeypatch.setattr(sys, "platform", "darwin")
    assert SDocRuntimeEnvironment.get_path_to_user_cache_dir() == os.path.join(
        home, "Library", "Caches", "strictdoc"
    )
