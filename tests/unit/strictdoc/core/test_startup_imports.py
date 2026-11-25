"""
Startup must not import the packages of optional formats and features.

Each Format and Feature imports its implementation on first use. These tests
start a fresh Python process, because the pytest process has already imported
most of these packages through other tests.
"""

import os
import subprocess
import sys
from typing import Dict, List

import strictdoc

# The package and the format, feature, or command that needs it.
OPTIONAL_PACKAGES: Dict[str, str] = {
    "bs4": "JUnit XML format",
    "docutils": "HTML and RST export",
    "fastapi": "server command",
    "html2pdf4doc": "HTML and HTML2PDF export",
    "jinja2": "HTML export",
    "lark": "source file traceability",
    "markdown_it": "Markdown format",
    "openpyxl": "Excel format",
    "PIL": "HTML and RST export",
    "pygments": "HTML export",
    "pypdf": "HTML2PDF format",
    "reqif": "ReqIF format",
    "robot": "Robot Framework source files and XML reports",
    "selenium": "HTML2PDF format",
    "spdx_tools": "SPDX format",
    "starlette": "server command",
    "tree_sitter_ada": "source file traceability",
    "tree_sitter_c": "source file traceability",
    "tree_sitter_cpp": "source file traceability",
    "tree_sitter_python": "source file traceability",
    "tree_sitter_rust": "source file traceability",
    "uvicorn": "server command",
    "watchfiles": "server command",
    "xlrd": "Excel format",
    "xlsxwriter": "Excel format",
    "yaml": "Markdown format",
}


def test_01_cli_startup_does_not_import_optional_packages():
    imported_packages = _get_imported_optional_packages(
        "import strictdoc.cli.main"
    )
    assert imported_packages == []


def test_02_format_and_feature_registries_do_not_import_optional_packages():
    imported_packages = _get_imported_optional_packages(
        "from strictdoc.core.project_config import ProjectConfig\n"
        "ProjectConfig.default_formats()\n"
        "ProjectConfig._builtin_features_by_handle()\n"
    )
    assert imported_packages == []


def _get_imported_optional_packages(code: str) -> List[str]:
    path_to_strictdoc_root = os.path.dirname(
        os.path.dirname(os.path.abspath(strictdoc.__file__))
    )
    environment = dict(os.environ)
    environment["PYTHONPATH"] = os.pathsep.join(
        [path_to_strictdoc_root, environment.get("PYTHONPATH", "")]
    )
    check_code = (
        f"{code}\n"
        "import sys\n"
        f"for package_ in {sorted(OPTIONAL_PACKAGES)!r}:\n"
        "    if package_ in sys.modules:\n"
        "        print(package_)\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", check_code],
        capture_output=True,
        check=True,
        encoding="utf8",
        env=environment,
    )
    return [
        f"{package_} ({OPTIONAL_PACKAGES[package_]})"
        for package_ in result.stdout.split()
    ]
