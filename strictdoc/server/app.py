"""
@relation(SDOC-SRS-126, scope=file)
"""

import logging
import os
import sys
import time
from typing import Awaitable, Callable, Generator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import Response

from strictdoc import __version__
from strictdoc.core.project_config import ProjectConfig
from strictdoc.helpers.coverage import register_code_coverage_hook
from strictdoc.helpers.deprecation_engine import DEPRECATION_ENGINE
from strictdoc.helpers.pickle import pickle_load
from strictdoc.server.config import SDocServerEnvVariable
from strictdoc.server.helpers.hierarchical_rw_lock_manager import (
    HierarchicalRWLockManager,
)
from strictdoc.server.routers.main_router import create_main_router
from strictdoc.server.routers.other_router import create_other_router

# Define O_TEMPORARY for Windows only
if sys.platform == "win32":
    O_TEMPORARY = os.O_TEMPORARY  # pragma: no cover
else:
    O_TEMPORARY = 0


LOGGER = logging.getLogger("uvicorn.error")


def print_welcome_message(project_config: ProjectConfig) -> None:
    strictdoc_version = f"StrictDoc Web Server v{__version__}"

    host = (
        project_config.server_host
        if project_config.server_host.startswith("http")
        else f"http://{project_config.server_host}"
    )

    url = f"{host}:{project_config.server_port}"

    width = 72
    border = "=" * width

    lines = [
        f" {strictdoc_version.center(width - 2)} ",
        "",
        f" Server URL: {url}",
        "",
        " Documentation: https://strictdoc.readthedocs.io/",
        "",
        " Subscribe to the StrictDoc mailing list for news about features,",
        " breaking changes, and other updates:",
        " https://groups.io/g/strictdoc",
        "",
        " Share feedback or report issues:",
        " https://github.com/strictdoc-project/strictdoc/issues",
    ]

    banner = (
        "\n\n"
        f"+{border}+\n"
        + "\n".join(f"|{line.ljust(width)}|" for line in lines)
        + f"\n+{border}+\n"
    )

    LOGGER.info(banner)


def create_app(*, project_config: ProjectConfig) -> FastAPI:
    def lifespan(_: FastAPI) -> Generator[None, None, None]:
        DEPRECATION_ENGINE.print_all_messages()
        print_welcome_message(project_config)
        yield

    app = FastAPI(lifespan=lifespan)

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

    lock_manager = HierarchicalRWLockManager()

    app.include_router(
        create_other_router(
            project_config=project_config,
            lock_manager=lock_manager,
        )
    )
    app.include_router(
        create_main_router(
            project_config=project_config,
            app=app,
            lock_manager=lock_manager,
        )
    )

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
