import os
import tempfile
from typing import Optional

import uvicorn

from strictdoc.cli.cli_arg_parser import ServerCommandConfig
from strictdoc.core.project_config import ProjectConfig
from strictdoc.helpers.pickle import pickle_dump
from strictdoc.server.config import SDocServerEnvVariable


def print_warning_message():
    print("")  # noqa: T201
    print("******************************************")  # noqa: T201
    print("*               WARNING                  *")  # noqa: T201
    print("*                                        *")  # noqa: T201
    print("* The StrictDoc Web-based user interface *")  # noqa: T201
    print("* is a highly experimental feature.      *")  # noqa: T201
    print("* Things may go wrong, so get ready      *")  # noqa: T201
    print("* to report bugs.                        *")  # noqa: T201
    print("******************************************")  # noqa: T201
    print("", flush=True)  # noqa: T201


def run_strictdoc_server(
    *, server_config: ServerCommandConfig, project_config: ProjectConfig
):
    print_warning_message()

    temp_dir: Optional[tempfile.TemporaryDirectory] = None
    if server_config.output_path is None:
        temp_dir = (
            tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
        )
        server_config.output_path = temp_dir.name

    # uvicorn.run does not support passing arguments to the main
    # function (strictdoc_production_app). Passing the pickled config through
    # the environmental variables interface.
    tmp_config_file = (
        tempfile.NamedTemporaryFile()  # pylint: disable=consider-using-with  # noqa: E501
    )
    with open(tmp_config_file.name, "wb") as tmp_config_file_:
        config_dump = pickle_dump((server_config, project_config))
        tmp_config_file_.write(config_dump)
    os.environ[SDocServerEnvVariable.PATH_TO_CONFIG] = tmp_config_file.name

    uvicorn.run(
        "strictdoc.server.app:strictdoc_production_app",
        app_dir=".",
        factory=True,
        host="127.0.0.1",
        log_level="info",
        port=server_config.port,
        reload=server_config.reload,
        reload_dirs=[
            os.path.join(
                server_config.environment.path_to_strictdoc, "strictdoc"
            )
        ],
        reload_includes=[
            "*.py",
            "*.html",
            "*.jinja",
            "*.css",
            "*.js",
        ],
        reload_excludes=[
            # "tests",  # Doesn't work.
            # "tests/",  # Doesn't work.
            # "tests/*",  # Doesn't work.
            # "tests/**",  # Makes the process hang, server doesn't start.
            # It looks like the regex engine does not support ** globs.
            "tests/*/*.*",
            "tests/*/*/*.*",
            "tests/*/*/*/*.*",
            "tests/*/*/*/*/*.*",
            "tests/*/*/*/*/*/*.*",
            "tests/*/*/*/*/*/*/*.*",
            "tests/*/*/*/*/*/*/*/*.*",
            "tests/*/*/*/*/*/*/*/*/*.*",
            "tests/*/*/*/*/*/*/*/*/*/*.*",
            "tests/*/*/*/*/*/*/*/*/*/*/*.*",
            "tests/*/*/*/*/*/*/*/*/*/*/*/*.*",
            "tests/*/*/*/*/*/*/*/*/*/*/*/*/*.*",
            "tests/*/*/*/*/*/*/*/*/*/*/*/*/*/*.*",
            "tests/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*.*",
        ],
    )
    tmp_config_file.close()
    if os.path.exists(tmp_config_file.name):
        os.unlink(tmp_config_file.name)
    if temp_dir is not None:
        temp_dir.cleanup()
