import os
import platform
import sys
from typing import List

#
# HTML templates.
#
HTML_TEMPLATES_DIR = os.path.join("strictdoc", "export", "html", "templates")
HTML_TEMPLATE_DIRS = [
    HTML_TEMPLATES_DIR,
    os.path.join("strictdoc", "features", "deep_trace", "templates"),
    os.path.join("strictdoc", "features", "diff_and_changelog", "templates"),
    os.path.join("strictdoc", "features", "html2pdf", "templates"),
    os.path.join("strictdoc", "features", "nestor", "templates"),
    os.path.join("strictdoc", "features", "project_index", "templates"),
    os.path.join("strictdoc", "features", "project_statistics", "templates"),
    os.path.join("strictdoc", "features", "search", "templates"),
    os.path.join("strictdoc", "features", "source_coverage", "templates"),
    os.path.join("strictdoc", "features", "source_file_view", "templates"),
    os.path.join("strictdoc", "features", "traceability_matrix", "templates"),
    os.path.join("strictdoc", "features", "tree_map", "templates"),
    os.path.join("strictdoc", "features", "trace", "templates"),
]
BINARY_HTML_TEMPLATES_DIR = os.path.join("templates", "html")

#
# HTML static files.
#
HTML_STATIC_DIR = os.path.join("strictdoc", "export", "html", "_static")
HTML_STATIC_DIRS = [
    HTML_STATIC_DIR,
    os.path.join("strictdoc", "features", "diff_and_changelog", "assets"),
    os.path.join("strictdoc", "features", "html2pdf", "assets"),
    os.path.join("strictdoc", "features", "mathjax", "assets"),
    os.path.join("strictdoc", "features", "mermaid", "assets"),
    os.path.join("strictdoc", "features", "nestor", "assets"),
    os.path.join("strictdoc", "features", "plantuml", "assets"),
    os.path.join("strictdoc", "features", "project_index", "assets"),
    os.path.join("strictdoc", "features", "source_coverage", "assets"),
    os.path.join("strictdoc", "features", "source_file_view", "assets"),
    os.path.join("strictdoc", "features", "traceability_matrix", "assets"),
    os.path.join("strictdoc", "features", "tree_map", "assets"),
]
BINARY_HTML_STATIC_DIR = "_static"


class SDocRuntimeEnvironment:
    def __init__(self, path_to_init: str) -> None:
        assert isinstance(path_to_init, str), path_to_init

        # FIXME: Delete me.
        self.path_to_init = path_to_init
        # https://stackoverflow.com/a/55556360/598057
        self.is_nuitka = "__compiled__" in globals()
        self.is_py_installer = (
            getattr(sys, "frozen", False) and not self.is_nuitka
        )

        # "frozen" attribute is set to True by PyInstaller, and it looks like
        # Nuitka does the same.
        self.is_binary_dist: bool = (
            getattr(sys, "frozen", False) or self.is_nuitka
        )

        if self.is_binary_dist:  # pragma: no cover
            # When it is a binary distribution, we don't have a Python package
            # file structure but only a binary with surrounding libraries and
            # data files (Jinja HTML files, CSS, JS, ...).
            path_to_main = os.path.abspath(sys.argv[0])
            path_to_main_dir = os.path.dirname(os.path.abspath(path_to_main))

            # Nuitka.
            if self.is_nuitka:
                self.path_to_strictdoc = path_to_main_dir
            # PyInstaller
            else:
                self.path_to_strictdoc = (
                    sys._MEIPASS  # type: ignore[attr-defined]
                )
        else:
            self.path_to_strictdoc = os.path.abspath(
                os.path.join(path_to_init, "..", "..")
            )
        assert os.path.isdir(self.path_to_strictdoc), self.path_to_strictdoc
        assert os.path.isabs(self.path_to_strictdoc), (
            "Path to strictdoc's package path must be an absolute path: "
            f"{self.path_to_strictdoc}"
        )

        self.is_debug_mode: bool = False
        self.is_test_env: bool = False
        self.is_development_mode: bool = False

    def is_windows(self) -> bool:
        return platform.system() == "Windows"

    def is_github_ci_windows(self) -> bool:
        return self.is_windows() and os.environ.get("GITHUB_ACTIONS") == "true"

    @staticmethod
    def get_path_to_user_cache_dir() -> str:
        """
        Return the per-user StrictDoc cache folder for downloads that do not
        belong to one project, such as the ChromeDriver used by HTML2PDF.
        This function does not create the folder.

        - Windows: %LOCALAPPDATA%/strictdoc/cache
        - macOS: ~/Library/Caches/strictdoc
        - Linux and others: $XDG_CACHE_HOME/strictdoc or ~/.cache/strictdoc
        """
        # Keep the if/elif/else form. mypy checks only the branch of the
        # platform that it runs on. Code after an early return in a platform
        # branch is reported as unreachable on that platform.
        path_to_home = os.path.expanduser("~")
        if sys.platform == "win32":
            path_to_base = os.environ.get("LOCALAPPDATA")
            if path_to_base is None or len(path_to_base) == 0:
                path_to_base = os.path.join(path_to_home, "AppData", "Local")
            path_to_cache_dir = os.path.join(path_to_base, "strictdoc", "cache")
        elif sys.platform == "darwin":
            path_to_cache_dir = os.path.join(
                path_to_home, "Library", "Caches", "strictdoc"
            )
        else:
            path_to_base = os.environ.get("XDG_CACHE_HOME")
            if path_to_base is None or len(path_to_base) == 0:
                path_to_base = os.path.join(path_to_home, ".cache")
            path_to_cache_dir = os.path.join(path_to_base, "strictdoc")
        return path_to_cache_dir

    def get_static_files_paths(self) -> List[str]:
        if self.is_binary_dist:  # pragma: no cover
            return [
                os.path.join(self.path_to_strictdoc, BINARY_HTML_STATIC_DIR)
            ]
        # Normal Python.
        static_files_paths = [
            os.path.join(self.path_to_strictdoc, static_dir)
            for static_dir in HTML_STATIC_DIRS
        ]
        for path in static_files_paths:
            assert os.path.isdir(path), path
            assert os.path.isabs(path), path
        return static_files_paths

    def get_path_to_rst_templates(self) -> str:
        if self.is_py_installer:  # pragma: no cover
            # If the application is run as a bundle, the PyInstaller bootloader
            # extends the sys module by a flag frozen=True and sets the app
            # path into variable _MEIPASS'.
            bundle_dir = (
                sys._MEIPASS  # type: ignore[attr-defined]
            )
            return os.path.join(bundle_dir, "templates/rst")
        if self.is_nuitka:  # pragma: no cover
            return os.path.join(self.path_to_strictdoc, "templates/rst")
        # Normal Python
        return os.path.join(
            self.path_to_strictdoc, "strictdoc", "backend", "rst", "templates"
        )

    def get_path_to_html_templates(self) -> List[str]:
        if self.is_py_installer:  # pragma: no cover
            # If the application is run as a bundle, the PyInstaller bootloader
            # extends the sys module by a flag frozen=True and sets the app
            # path into variable _MEIPASS'.
            bundle_dir = (
                sys._MEIPASS  # type: ignore[attr-defined]
            )
            return [os.path.join(bundle_dir, BINARY_HTML_TEMPLATES_DIR)]
        if self.is_nuitka:  # pragma: no cover
            return [
                os.path.join(self.path_to_strictdoc, BINARY_HTML_TEMPLATES_DIR)
            ]
        # Normal Python.
        path_to_html_templates = [
            os.path.join(self.path_to_strictdoc, template_dir)
            for template_dir in HTML_TEMPLATE_DIRS
        ]
        for path in path_to_html_templates:
            assert os.path.isdir(path), path
            assert os.path.isabs(path), path
        return path_to_html_templates
