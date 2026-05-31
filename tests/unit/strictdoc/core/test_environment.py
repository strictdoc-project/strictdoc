import os
import sys
from pathlib import Path

from pytest import MonkeyPatch

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
