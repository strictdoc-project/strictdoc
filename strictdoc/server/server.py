# mypy: disable-error-code="no-untyped-call,no-untyped-def"
import os
import tempfile
from contextlib import ExitStack

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

    with ExitStack() as stack:
        if server_config.output_path is None:
            server_config.output_path = stack.enter_context(
                tempfile.TemporaryDirectory()
            )

        # uvicorn.run does not support passing arguments to the main
        # function (strictdoc_production_app). Passing the pickled config
        # through the environmental variables interface.
        tmp_config_file = stack.enter_context(tempfile.NamedTemporaryFile())
        config_dump = pickle_dump((server_config, project_config))
        tmp_config_file.write(config_dump)
        tmp_config_file.flush()

        os.environ[SDocServerEnvVariable.PATH_TO_CONFIG] = tmp_config_file.name

        uvicorn.run(
            "strictdoc.server.app:strictdoc_production_app",
            app_dir=".",
            factory=True,
            host=project_config.server_host,
            log_level="info",
            # "server" command port overrides the strictdoc.toml option for now.
            # Eventually, I am considering to remove the CLI option for the
            # port, to simplify the maintenance of two configs: the config file
            # and the "export" command's interface.
            port=(
                server_config.port
                if server_config.port is not None
                else project_config.server_port
            ),
            reload=server_config.reload,
            reload_dirs=[
                os.path.join(
                    project_config.get_strictdoc_root_path(), "strictdoc"
                )
            ],
            reload_includes=[
                "*.py",
                "*.html",
                "*.jinja",
                "*.css",
                "*.js",
                "*.toml",
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
