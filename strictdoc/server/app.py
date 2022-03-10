import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from strictdoc.cli.cli_arg_parser import ServerCommandConfig
from strictdoc.server.config import ServerConfig
from strictdoc.server.routers.main_router import create_main_router


def create_app(*, path_to_sdoc_tree: str):
    assert os.path.exists(path_to_sdoc_tree)
    assert os.path.isabs(path_to_sdoc_tree)

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

    app.include_router(create_main_router(path_to_sdoc_tree=path_to_sdoc_tree))

    return app


def strictdoc_production_app():
    if ServerConfig.config is None:
        ServerConfig.config = ServerCommandConfig(
            input_path="developer/sandbox"
        )

    path_to_sdoc_tree = ServerConfig.config.input_path
    assert os.path.exists(path_to_sdoc_tree)
    abs_path_to_sdoc_tree = os.path.abspath(path_to_sdoc_tree)
    assert os.path.isabs(abs_path_to_sdoc_tree)
    return create_app(path_to_sdoc_tree=abs_path_to_sdoc_tree)
