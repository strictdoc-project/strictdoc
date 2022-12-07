import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from strictdoc.cli.cli_arg_parser import ServerCommandConfig
from strictdoc.server.config import SDocServerEnvVariable
from strictdoc.server.routers.main_router import create_main_router


def create_app(*, config: ServerCommandConfig):
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

    app.include_router(create_main_router(config=config))

    return app


def strictdoc_production_app():
    config = ServerCommandConfig(
        input_path=os.environ[SDocServerEnvVariable.INPUT_PATH],
        output_path=os.environ[SDocServerEnvVariable.OUTPUT_PATH],
        reload=os.environ[SDocServerEnvVariable.RELOAD] == "True",
    )
    return create_app(config=config)
