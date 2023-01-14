import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from strictdoc.cli.cli_arg_parser import ServerCommandConfig
from strictdoc.core.project_config import ProjectConfig
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
    server_config = ServerCommandConfig(
        input_path=os.environ[SDocServerEnvVariable.INPUT_PATH],
        output_path=os.environ[SDocServerEnvVariable.OUTPUT_PATH],
        reload=os.environ[SDocServerEnvVariable.RELOAD] == "True",
    )
    project_config: ProjectConfig = ProjectConfig.config_from_string_dump(
        os.environ[SDocServerEnvVariable.PROJECT_CONFIG]
    )
    return create_app(
        server_config=server_config,
        project_config=project_config,
    )
