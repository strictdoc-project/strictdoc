import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from strictdoc.server.routers.main_router import create_main_router

ENV_INPUT_PATH = "ENV_INPUT_PATH"
ENV_OUTPUT_PATH = "ENV_OUTPUT_PATH"


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
    assert ENV_INPUT_PATH in os.environ
    path_to_sdoc_tree = os.environ[ENV_INPUT_PATH]
    assert os.path.exists(path_to_sdoc_tree)
    abs_path_to_sdoc_tree = os.path.abspath(path_to_sdoc_tree)
    assert os.path.isabs(abs_path_to_sdoc_tree)
    return create_app(path_to_sdoc_tree=abs_path_to_sdoc_tree)
