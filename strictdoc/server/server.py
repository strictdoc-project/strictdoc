import os

import uvicorn

from strictdoc import STRICTDOC_ROOT_PATH
from strictdoc.cli.cli_arg_parser import ServerCommandConfig
from strictdoc.core.project_config import ProjectConfig
from strictdoc.server.config import SDocServerEnvVariable


def print_warning_message():
    print("")
    print("******************************************")
    print("*               WARNING                  *")
    print("*                                        *")
    print("* The StrictDoc Web-based user interface *")
    print("* is a highly experimental feature.      *")
    print("* Things may go wrong, so get ready      *")
    print("* to report bugs.                        *")
    print("******************************************")
    print("", flush=True)


def run_strictdoc_server(
    *, server_config: ServerCommandConfig, project_config: ProjectConfig
):
    print_warning_message()

    # uvicorn.run does not support passing arguments to the main
    # function (strictdoc_production_app). Passing the config through the
    # environmental variables interface.
    os.environ[SDocServerEnvVariable.INPUT_PATH] = server_config.input_path
    os.environ[SDocServerEnvVariable.OUTPUT_PATH] = server_config.output_path
    os.environ[SDocServerEnvVariable.RELOAD] = str(server_config.reload)
    os.environ[
        SDocServerEnvVariable.PROJECT_CONFIG
    ] = project_config.dump_to_string()

    uvicorn.run(
        "strictdoc.server.app:strictdoc_production_app",
        app_dir=".",
        # debug=False,
        factory=True,
        host="127.0.0.1",
        log_level="info",
        port=8001,
        reload=server_config.reload,
        reload_dirs=[
            STRICTDOC_ROOT_PATH,
            server_config.input_path,
        ],
        # reload_delay: Optional[float] = None,
        reload_includes=[
            "*.py",
            "*.html",
            "*.css",
            "*.js",
        ],
        # reload_excludes=[
        #     "**/developer/sandbox/output/**/*",
        #     # "*output*",
        # ],
        # root_path: str = "",
    )
