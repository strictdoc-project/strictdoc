# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller spec for a self-contained StrictDoc bundle (onedir).
#
# Build it with scripts/build_bundle.sh, which creates the venv, installs the
# pinned dependencies, and runs:
#
#     pyinstaller --noconfirm --clean scripts/strictdoc.spec
#
# The output is dist/strictdoc/ with the "strictdoc" executable at its top.
# The build script renames that directory to include the version and platform.
#
# Data layout inside the bundle follows strictdoc/core/environment.py, which
# looks up templates and static files relative to sys._MEIPASS when frozen:
#
#   templates/html/  all Jinja HTML template dirs (HTML_TEMPLATE_DIRS), merged
#   templates/rst/   RST export templates
#   _static/         all static asset dirs (HTML_STATIC_DIRS), merged
#
# pylint: disable=undefined-variable
# ruff: noqa: F821

import os
import sys

from PyInstaller.utils.hooks import (
    collect_data_files,
    collect_submodules,
    copy_metadata,
)

ROOT = os.path.abspath(os.path.join(SPECPATH, ".."))
sys.path.insert(0, ROOT)

from strictdoc.core.environment import (  # noqa: E402
    BINARY_HTML_STATIC_DIR,
    BINARY_HTML_TEMPLATES_DIR,
    HTML_STATIC_DIRS,
    HTML_TEMPLATE_DIRS,
)


def _root(path):
    return os.path.join(ROOT, path)


datas = []
datas += [(_root(d), BINARY_HTML_TEMPLATES_DIR) for d in HTML_TEMPLATE_DIRS]
datas += [(_root(d), BINARY_HTML_STATIC_DIR) for d in HTML_STATIC_DIRS]
datas += [
    (
        _root(os.path.join("strictdoc", "backend", "rst", "templates")),
        os.path.join("templates", "rst"),
    ),
    # The experimental desktop launcher loads its window icon through
    # importlib.resources.files("strictdoc"), i.e. from the package layout.
    (
        _root(
            os.path.join(
                "strictdoc", "export", "html", "_static", "favicon.ico"
            )
        ),
        os.path.join("strictdoc", "export", "html", "_static"),
    ),
]

# Third-party package data that is read at runtime via __file__. Packages
# with official PyInstaller hooks (docutils, pygments, lark, plotly, pandas,
# uvicorn, selenium, ...) are covered by pyinstaller-hooks-contrib; the
# hooks in developer/pyinstaller_hooks cover html2pdf4doc and spdx_tools.
datas += collect_data_files("reqif")
datas += collect_data_files("textx")
datas += collect_data_files("robot")
datas += collect_data_files("webdriver_manager")

# Distribution metadata read at runtime through importlib.metadata.
for dist in (
    "strictdoc",
    "textx",
    "reqif",
    "fastapi",
    "starlette",
    "uvicorn",
    "selenium",
    "webdriver-manager",
    "html2pdf4doc",
    "openpyxl",
    "xlrd",
    "XlsxWriter",
    "spdx-tools",
):
    try:
        datas += copy_metadata(dist)
    except Exception as exception_:  # noqa: BLE001
        print(f"strictdoc.spec: no metadata for {dist}: {exception_}")

hiddenimports = [
    # uvicorn imports the app by its string name ("strictdoc.server.app"),
    # so static analysis does not see it.
    "strictdoc.server.app",
    # Imported only by user files (strictdoc_config.py, custom statistics
    # generators, plugins) that are loaded at runtime.
    "strictdoc.api",
    "strictdoc.backend.rst.strictdoc_lexer",
    "strictdoc.core.statistics.metric",
    "strictdoc.export.html.generators.project_statistics",
    "strictdoc.export.html.generators.view_objects.project_statistics_view_object",
    "strictdoc.export.html.generators.view_objects.project_tree_stats",
]
# Everything in StrictDoc itself: commands, features and routers are cheap to
# include and some are only reached through runtime registries.
hiddenimports += collect_submodules("strictdoc")
# uvicorn picks its loop/protocol/lifespan implementations by name at runtime.
hiddenimports += collect_submodules("uvicorn")
hiddenimports += collect_submodules("websockets")
hiddenimports += collect_submodules("webdriver_manager")

excludes = [
    # Development-only packages that may be present in the build venv.
    "pytest",
    "IPython",
    "matplotlib",
]

a = Analysis(
    [_root(os.path.join("strictdoc", "cli", "main.py"))],
    pathex=[ROOT],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[_root(os.path.join("developer", "pyinstaller_hooks"))],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="strictdoc",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    # Only Windows takes .ico directly; macOS would need Pillow to convert it.
    icon=(
        _root(
            os.path.join(
                "strictdoc", "export", "html", "_static", "favicon.ico"
            )
        )
        if sys.platform == "win32"
        else None
    ),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="strictdoc",
)
