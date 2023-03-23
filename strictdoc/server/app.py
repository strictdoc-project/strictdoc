import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from strictdoc.cli.cli_arg_parser import ServerCommandConfig
from strictdoc.core.project_config import ProjectConfig
from strictdoc.helpers.pickle import pickle_load
from strictdoc.server.config import SDocServerEnvVariable
from strictdoc.server.routers.main_router import create_main_router


def create_app(
    *, server_config: ServerCommandConfig, project_config: ProjectConfig
):
    app = FastAPI()

    origins = [
        "http://localhost",
        "http://localhost:8081",
        "http://localhost:3000",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(
        create_main_router(
            server_config=server_config, project_config=project_config
        )
    )

    return app


def strictdoc_production_app():
    # This is a work-around to allow opening a file created with
    # NamedTemporaryFile on Windows.
    # See https://stackoverflow.com/a/15235559
    def temp_opener(name, flag, mode=0o777):
        try:
            flag |= os.O_TEMPORARY
        except AttributeError:
            pass  # Only Windows has this flag

        return os.open(name, flag, mode)

    path_to_tmp_config = os.environ[SDocServerEnvVariable.PATH_TO_CONFIG]
    with open(path_to_tmp_config, "rb", opener=temp_opener) as tmp_config_file:
        tmp_config_bytes = tmp_config_file.read()

    two_configs = pickle_load(tmp_config_bytes)
    assert isinstance(two_configs, tuple), type(two_configs)
    assert len(two_configs) == 2
    assert isinstance(two_configs[0], ServerCommandConfig)
    assert isinstance(two_configs[1], ProjectConfig)

    server_config: ServerCommandConfig = two_configs[0]
    project_config: ProjectConfig = two_configs[1]

    return create_app(
        server_config=server_config,
        project_config=project_config,
    )
