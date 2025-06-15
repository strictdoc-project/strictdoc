import os
from dataclasses import dataclass
from typing import List, Optional

from strictdoc.cli.cli_arg_parser import ServerCommandConfig
from strictdoc.core.project_config import ProjectConfig


@dataclass
class UvicornReloadConfig:
    """
    Class that encapsulate the Uvicorn server configuration details.

    Uvicorn has an opinionated system for configuring the reloading of a server
    when the specified files are changed on the file system. This class
    centralized the reload configuration details in one place.

    One responsibility of this class is to give a correct configuration when
    the files must be reloaded and give a completely empty configuration when
    the reload is False. In particular, if a configuration specifies reload=False
    but the reload_dirs or reload_includes or reload_excludes are specified,
    then the following warning is shown.
    WARNING:  Current configuration will not reload as not all conditions are met, please refer to documentation.
    The create() method of this class ensures that uvicorn is happy and the
    warning does not appear.
    """

    reload: bool
    reload_dirs: Optional[List[str]]
    reload_includes: Optional[List[str]]
    reload_excludes: Optional[List[str]]

    @classmethod
    def create(
        cls, project_config: ProjectConfig, server_config: ServerCommandConfig
    ) -> "UvicornReloadConfig":
        reload: bool = server_config.reload
        reload_dirs: Optional[List[str]] = None
        reload_includes: Optional[List[str]] = None
        reload_excludes: Optional[List[str]] = None

        if server_config.reload:
            # This doesn't seem to be effect because we still must provide the
            # reload_excludes outside this folder. Maybe it has to do with the
            # presence of reload_includes that includes all files with given
            # file extensions below. Anyway this works well enough with the
            # given reload_excludes.
            reload_dirs = [
                os.path.join(
                    project_config.get_strictdoc_root_path(), "strictdoc"
                )
            ]
            # It is important that StrictDoc's artifacts are excluded because
            # StrictDoc's web server will be triggered to restart every time the
            # contents of these folders changes.
            reload_excludes = (
                cls.expand_folder("build", max_depth=15)
                + cls.expand_folder("docs", max_depth=3)
                + cls.expand_folder("dist", max_depth=3)
                + cls.expand_folder("tests", max_depth=15)
                + cls.expand_folder("output", max_depth=15)
                + cls.expand_folder("Output", max_depth=15)
            )

            # Changing typical StrictDoc's own source code files should trigger
            # restarting of the web server. Whitelisting them here.
            reload_includes = [
                "*.py",
                "*.html",
                "*.jinja",
                "*.css",
                "*.js",
                "*.toml",
            ]
        return UvicornReloadConfig(
            reload=reload,
            reload_dirs=reload_dirs,
            reload_includes=reload_includes,
            reload_excludes=reload_excludes,
        )

    @classmethod
    def expand_folder(cls, folder: str, max_depth: int) -> List[str]:
        """
        Create a list of wildcard-based paths for a given folder.

        It looks like the regex engine of the uvicorn file watching library
        does not support proper ** globs.

        Examples:
        "tests",  # Doesn't work.
        "tests/",  # Doesn't work.
        "tests/*",  # Doesn't work.
        "tests/**",  # Makes the process hang, server doesn't start.

        Example of a possible StrictDoc path that must be excluded:
        output/cache/server/html/_source_files/strictdoc/backend/reqif/sdoc_reqif_fields.py.html

        This function produces output like this:
        [
            "output/*.*",
            "output/*/*.*",
            "output/*/*/*.*",
            "output/*/*/*/*.*",
            "output/*/*/*/*/*.*",
            "output/*/*/*/*/*/*.*",
            "output/*/*/*/*/*/*/*.*",
            "output/*/*/*/*/*/*/*/*.*",
            "output/*/*/*/*/*/*/*/*/*.*",
            "output/*/*/*/*/*/*/*/*/*/*.*",
            "output/*/*/*/*/*/*/*/*/*/*/*.*",
            "output/*/*/*/*/*/*/*/*/*/*/*/*.*",
            "output/*/*/*/*/*/*/*/*/*/*/*/*/*.*",
            "output/*/*/*/*/*/*/*/*/*/*/*/*/*/*.*",
            "output/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*.*",
        ]
        """

        patterns = []
        for depth in range(1, max_depth + 1):
            pattern = folder + "/" + "*/" * (depth - 1) + "*.*"
            patterns.append(pattern)
        return patterns
