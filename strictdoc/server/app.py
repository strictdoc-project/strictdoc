# mypy: disable-error-code="no-untyped-def"
import os
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request

from strictdoc.cli.cli_arg_parser import ServerCommandConfig
from strictdoc.core.project_config import ProjectConfig
from strictdoc.helpers.pickle import pickle_load
from strictdoc.server.config import SDocServerEnvVariable
from strictdoc.server.routers.main_router import create_main_router
from strictdoc.server.routers.other_router import create_other_router


def create_app(
    *, server_config: ServerCommandConfig, project_config: ProjectConfig
):
    app = FastAPI()

    origins = [
        "http://localhost",
        "http://localhost:8081",
        "http://localhost:3000",
    ]

    # Uncomment this to enable performance measurements.
    @app.middleware("http")
    async def add_process_time_header(  # pylint: disable=unused-variable
        request: Request, call_next
    ):
        start_time = time.time()
        response = await call_next(request)
        time_passed = round(time.time() - start_time, 3)

        request_path = request.url.path
        if len(request.url.query) > 0:
            request_path += f"?{request.url.query}"

        print(  # noqa: T201
            f"PERF:     {request.method} {request_path} {time_passed}s"
        )
        return response

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(create_other_router(project_config=project_config))
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
