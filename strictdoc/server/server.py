# mypy: disable-error-code="no-untyped-call,no-untyped-def"
import os
import tempfile
from contextlib import ExitStack
from pathlib import Path

import uvicorn

from strictdoc import __version__
from strictdoc.cli.cli_arg_parser import ServerCommandConfig
from strictdoc.core.project_config import ProjectConfig
from strictdoc.helpers.pickle import pickle_dump
from strictdoc.server.config import SDocServerEnvVariable
from strictdoc.server.reload_config import UvicornReloadConfig


def print_warning_message():
    strictdoc_version = "StrictDoc web server v" + __version__
    print(  # noqa: T201
        f"""
*********************************************************
* {strictdoc_version.center(53)} *
*                                                       *
* Share feedback and report issues on GitHub:           *
* https://github.com/strictdoc-project/strictdoc/issues *
*********************************************************
""",
        flush=True,
    )


def run_strictdoc_server(
    *, server_config: ServerCommandConfig, project_config: ProjectConfig
):
    print_warning_message()

    with ExitStack() as stack:
        if server_config.output_path is None:
            server_config.output_path = stack.enter_context(
                tempfile.TemporaryDirectory()
            )

        project_config.integrate_server_config(server_config)

        reload_config = UvicornReloadConfig.create(
            project_config, server_config
        )

        # The server's uvicorn.run does not support passing arguments to the
        # main function (strictdoc_production_app). Passing the pickled config
        # through the environmental variables interface.
        tmp_config_file = stack.enter_context(tempfile.NamedTemporaryFile())
        config_dump = pickle_dump(project_config)
        tmp_config_file.write(config_dump)
        tmp_config_file.flush()

        os.environ[SDocServerEnvVariable.PATH_TO_CONFIG] = tmp_config_file.name

        # The uvicorn config code uses this function to additionally resolve
        # the reload includes and excludes. Unfortunately, it does not work
        # correctly with the expanded globs that are created by StrictDoc.
        # Not doing any resolutions seems to work fine with StrictDoc, so using
        # a 'do nothing' stub and an assert below to make sure that this function
        # is not removed by uvicorn.
        def dont_resolve_reload_patterns(arg1, arg2):  # pragma: no cover
            return arg1, list(map(Path, arg2))  # pragma: no cover

        assert hasattr(uvicorn.config, "resolve_reload_patterns"), (
            "REGRESSION: The function 'resolve_reload_patterns' is not defined "
            "in uvicorn.config. Please report this to StrictDoc developers at "
            "https://github.com/strictdoc-project/strictdoc/issues."
        )
        uvicorn.config.resolve_reload_patterns = dont_resolve_reload_patterns

        uvicorn.run(
            "strictdoc.server.app:strictdoc_production_app",
            app_dir=".",
            factory=True,
            host=server_config.host
            if server_config.host is not None
            else project_config.server_host,
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
            reload=reload_config.reload,
            reload_dirs=reload_config.reload_dirs,
            reload_includes=reload_config.reload_includes,
            reload_excludes=reload_config.reload_excludes,
        )
