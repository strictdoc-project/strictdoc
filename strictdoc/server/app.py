import os
import sys
import time
from typing import Awaitable, Callable

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import Response

from strictdoc.core.project_config import ProjectConfig
from strictdoc.helpers.coverage import register_code_coverage_hook
from strictdoc.helpers.pickle import pickle_load
from strictdoc.server.config import SDocServerEnvVariable
from strictdoc.server.routers.main_router import create_main_router
from strictdoc.server.routers.other_router import create_other_router

# Define O_TEMPORARY for Windows only
if sys.platform == "win32":
    O_TEMPORARY = os.O_TEMPORARY  # pragma: no cover
else:
    O_TEMPORARY = 0


def create_app(*, project_config: ProjectConfig) -> FastAPI:
    app = FastAPI()

    origins = [
        "http://localhost",
        "http://localhost:8081",
        "http://localhost:3000",
    ]

    # Uncomment this to enable performance measurements.
    @app.middleware("http")
    async def add_process_time_header(  # pylint: disable=unused-variable
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        start_time = time.time()
        response: Response = await call_next(request)
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
    app.include_router(create_main_router(project_config=project_config))

    return app


def strictdoc_production_app() -> FastAPI:
    register_code_coverage_hook()

    # This is a work-around to allow opening a file created with
    # NamedTemporaryFile on Windows.
    # See https://stackoverflow.com/a/15235559
    def temp_opener(name: str, flag: int, mode: int = 0o777) -> int:
        flag |= O_TEMPORARY
        return os.open(name, flag, mode)

    path_to_tmp_config = os.environ[SDocServerEnvVariable.PATH_TO_CONFIG]
    with open(path_to_tmp_config, "rb", opener=temp_opener) as tmp_config_file:
        tmp_config_bytes = tmp_config_file.read()

    project_config = pickle_load(tmp_config_bytes)
    assert isinstance(project_config, ProjectConfig), project_config

    return create_app(
        project_config=project_config,
    )
