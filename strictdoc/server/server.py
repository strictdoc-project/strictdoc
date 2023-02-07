import os
import tempfile

import uvicorn

from strictdoc.cli.cli_arg_parser import ServerCommandConfig
from strictdoc.core.project_config import ProjectConfig
from strictdoc.helpers.pickle import pickle_dump
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
        # debug=False,
        factory=True,
        host="127.0.0.1",
        log_level="info",
        port=server_config.port,
        reload=server_config.reload,
        reload_dirs=[
            server_config.environment.path_to_strictdoc,
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
    tmp_config_file.close()
    if os.path.exists(tmp_config_file.name):
        os.unlink(tmp_config_file.name)
