"""
Startup must not import the packages of optional formats and features.

Each Format and Feature imports its implementation on first use. These tests
start a fresh Python process, because the pytest process has already imported
most of these packages through other tests.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

import strictdoc
from strictdoc.core.project_config import ProjectConfig

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


def test_03_server_startup_imports_only_the_server_packages():
    """
    The server routers import the packages of ReqIF, HTML2PDF, and the
    Markdown writer only in the routes that use them.
    """
    # The server and its HTML rendering need these packages at startup.
    # "html2pdf4doc" here is only the package itself, which provides the path
    # to its JavaScript files. html2pdf4doc.main imports selenium and pypdf.
    server_packages = {
        "docutils",
        "fastapi",
        "html2pdf4doc",
        "jinja2",
        "markdown_it",
        "PIL",
        "pygments",
        "starlette",
        "uvicorn",
    }
    imported_packages = _get_imported_optional_packages(
        "import strictdoc.cli.main\n"
        "import strictdoc.server.app\n"
        "import strictdoc.server.routers.main_router\n"
        "import strictdoc.server.routers.other_router\n"
    )
    assert [
        package_
        for package_ in imported_packages
        if package_.split(" ")[0] not in server_packages
    ] == []


def test_04_api_imports_excel_export_on_first_access():
    """
    Every export loads the project config, which usually imports
    strictdoc.api. The Excel export of strictdoc.api loads only on access.
    """
    imported_packages = _get_imported_optional_packages(
        "import strictdoc.api\nfrom strictdoc.api import ProjectConfig\n"
    )
    assert "xlsxwriter (Excel format)" not in imported_packages

    imported_packages = _get_imported_optional_packages(
        "from strictdoc.api import ExcelGenerator\n"
    )
    assert "xlsxwriter (Excel format)" in imported_packages


def test_05_markdown_document_from_cache_does_not_import_the_parser(
    tmp_path: Path,
):
    """
    An export without changes reads the Markdown documents from the cache.
    The cache entry does not need the Markdown parser or PyYAML.
    """
    from strictdoc.backend.markdown.reader import (  # noqa: PLC0415
        SDMarkdownReader,
    )

    path_to_document = tmp_path / "document.md"
    path_to_document.write_text("# Document\n\nText.\n")
    project_config = ProjectConfig.default_config()
    project_config.output_dir = str(tmp_path / "output")
    project_config.dir_for_sdoc_cache = str(tmp_path / "cache")
    # The first read parses the document and saves it to the cache.
    SDMarkdownReader().read_from_file(str(path_to_document), project_config)

    imported_packages = _get_imported_optional_packages(
        "from strictdoc.backend.markdown.markdown_format import MarkdownFormat\n"
        "from strictdoc.core.file_system.file_tree import File\n"
        "from strictdoc.core.project_config import ProjectConfig\n"
        "from strictdoc.helpers.paths import SDocRelativePath\n"
        "project_config = ProjectConfig.default_config()\n"
        f"project_config.output_dir = {project_config.output_dir!r}\n"
        f"project_config.dir_for_sdoc_cache = {project_config.dir_for_sdoc_cache!r}\n"
        "document = MarkdownFormat().read_from_cache(\n"
        f"    File(1, {str(path_to_document)!r}, SDocRelativePath('document.md')),\n"
        "    project_config,\n"
        ")\n"
        "assert document is not None\n"
    )

    assert "yaml (Markdown format)" not in imported_packages
    assert "markdown_it (Markdown format)" not in imported_packages


def test_06_export_without_changes_does_not_import_the_page_generators(
    tmp_path: Path,
):
    """
    An export without changes writes no pages, so it does not need the page
    generators of the HTML export and the packages of MarkupRenderer.
    """
    path_to_input = tmp_path / "input"
    path_to_input.mkdir()
    (path_to_input / "document.sdoc").write_text(
        "[DOCUMENT]\n"
        "TITLE: Document\n"
        "\n"
        "[REQUIREMENT]\n"
        "UID: REQ-1\n"
        "STATEMENT: Statement\n"
    )
    # The export prints to the standard output, which the check of the
    # imported packages reads. The output of the export goes to os.devnull.
    export_code = (
        "import os, sys\n"
        "from strictdoc.cli.main import main\n"
        "sys.argv = [\n"
        "    'strictdoc', 'export', "
        f"{str(path_to_input)!r}, '--output-dir', "
        f"{str(tmp_path / 'output')!r},\n"
        "]\n"
        "stdout_fd = os.dup(1)\n"
        "os.dup2(os.open(os.devnull, os.O_WRONLY), 1)\n"
        "try:\n"
        "    main()\n"
        "except SystemExit:\n"
        "    pass\n"
        "finally:\n"
        "    sys.stdout.flush()\n"
        "    os.dup2(stdout_fd, 1)\n"
    )
    # The first export writes the pages and the caches.
    imported_packages = _get_imported_optional_packages(export_code)
    assert "docutils (HTML and RST export)" in imported_packages

    imported_packages = _get_imported_optional_packages(export_code)

    for package_ in ("docutils", "pygments", "PIL"):
        assert all(
            not imported_package_.startswith(f"{package_} ")
            for imported_package_ in imported_packages
        ), imported_packages


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
