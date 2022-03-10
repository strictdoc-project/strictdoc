import os
import sys

import uvicorn

from strictdoc import STRICTDOC_ROOT_PATH
from strictdoc.cli.cli_arg_parser import ServerCommandConfig
from strictdoc.server.config import ServerConfig


def run_strictdoc_server(*, config: ServerCommandConfig):
    # uvicorn.run does not support passing arguments to the main
    # function (strictdoc_production_app). Passing the config through a global
    # variable.
    ServerConfig.config = config
    print(os.path.abspath(config.input_path))
    uvicorn.run(
        "strictdoc.server.app:strictdoc_production_app",
        app_dir=".",
        # debug=False,
        factory=True,
        host="127.0.0.1",
        log_level="info",
        port=8001,
        reload=True,
        reload_dirs=[STRICTDOC_ROOT_PATH],
        # reload_delay: Optional[float] = None,
        reload_includes=[
            # "strictdoc.server.restart",
            "*.py",
            "*.sdoc",
            "*.html",
            "*.css",
        ],
        # reload_excludes=[
        #     "**/developer/sandbox/output/**/*",
        #     # "*output*",
        # ],
        # root_path: str = "",
    )
