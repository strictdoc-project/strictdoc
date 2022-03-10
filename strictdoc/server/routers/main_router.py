import os
from mimetypes import guess_type
from typing import Optional

from fastapi import APIRouter
from starlette.responses import HTMLResponse, Response

from strictdoc import __version__, STRICTDOC_ROOT_PATH
from strictdoc.server.controllers.main_controller import MainController


def create_main_router(path_to_sdoc_tree: Optional[str]) -> APIRouter:
    router = APIRouter()

    main_controller = MainController(path_to_sdoc_tree=path_to_sdoc_tree)

    @router.get("/")
    def get_root():
        return f"StrictDoc v{__version__}"

    @router.get("/{full_path:path}", response_class=Response)
    def get_incoming_request(full_path: str):
        if full_path.endswith(".html"):
            return get_document(full_path)
        if full_path.endswith(".css"):
            return get_css(full_path)
        return HTMLResponse(
            content="Neither existing HTML or CSS file", status_code=404
        )

    def get_document(url_to_document: str):
        print(f"MainRounter.get_document> {url_to_document}")
        document_html_content = main_controller.get_document(url_to_document)
        return HTMLResponse(content=document_html_content, status_code=200)

    def get_css(url_to_css: str):
        print(f"MainRounter.get_css> {url_to_css}")

        # if not os.path.isfile(filename):
        # return Response(status_code=405)

        static_path = os.path.join(STRICTDOC_ROOT_PATH, "strictdoc/export/html")
        static_file = os.path.join(static_path, url_to_css)
        content_type, _ = guess_type(static_file)

        assert os.path.isfile(static_file), f"{static_file}"
        with open(static_file, encoding="utf8") as f:
            content = f.read()
        return Response(content, media_type=content_type)

    return router
