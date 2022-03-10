import os
from mimetypes import guess_type
from typing import Optional

from fastapi import Form, APIRouter
from starlette.responses import HTMLResponse, Response

from strictdoc import __version__, STRICTDOC_ROOT_PATH
from strictdoc.server.controllers.main_controller import (
    MainController,
    NodeCreationOrder,
)


def create_main_router(path_to_sdoc_tree: Optional[str]) -> APIRouter:
    router = APIRouter()

    main_controller = MainController(path_to_sdoc_tree=path_to_sdoc_tree)

    @router.get("/")
    def get_root():
        return get_incoming_request("index.html")

    @router.get("/ping")
    def get_ping():
        return f"StrictDoc v{__version__}"

    @router.get("/streams/document/new_section", response_class=Response)
    def get_new_section(reference_mid: str, whereto: str):
        assert isinstance(whereto, str), whereto
        assert NodeCreationOrder.is_valid(whereto), whereto

        content = main_controller.get_new_section(
            reference_mid=reference_mid, whereto=whereto
        )
        return HTMLResponse(
            content=content,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.post("/streams/document/create_section", response_class=Response)
    def create_section(
        section_mid: str = Form(None),
        section_title: str = Form(None),
        section_content: str = Form(None),
        reference_mid: str = Form(None),
        whereto: str = Form(None),
    ):
        assert isinstance(whereto, str), whereto
        assert NodeCreationOrder.is_valid(whereto), whereto

        content = main_controller.create_new_section(
            section_mid=section_mid,
            section_title=section_title,
            section_content=section_content,
            reference_mid=reference_mid,
            whereto=whereto,
        )
        return HTMLResponse(
            content=content,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.get("/fragments/sections/{section_id}", response_class=Response)
    def get_edit_section(section_id: str):
        content = main_controller.get_edit_section(section_id)
        return HTMLResponse(
            content=content,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.post("/streams/document/update_section", response_class=Response)
    def put_update_section(
        section_mid: str = Form(None),
        section_title: str = Form(None),
        section_content: str = Form(None),
    ):
        content = main_controller.update_section(
            section_id=section_mid,
            section_title=section_title,
            section_content=section_content,
        )
        return HTMLResponse(
            content=content,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.get("/fragments/document/{document_id}", response_class=Response)
    def get_edit_document_freetext(document_id: str):
        print("get_Test")
        print(document_id)
        content = main_controller.get_edit_document_freetext(document_id)
        # print(content)
        return HTMLResponse(
            content=content,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.post("/fragments/document/{document_id}", response_class=Response)
    def put_update_document_freetext(
        document_id: str,
        document_freetext: str = Form(None),
    ):
        content = main_controller.update_document_freetext(
            document_id=document_id,
            document_freetext=document_freetext,
        )
        return HTMLResponse(
            content=content,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.get("/streams/document/new_requirement", response_class=Response)
    def get_new_requirement(reference_mid: str, whereto: str):
        assert isinstance(reference_mid, str), reference_mid
        assert isinstance(whereto, str), whereto
        assert NodeCreationOrder.is_valid(whereto), whereto

        content = main_controller.get_new_requirement(
            reference_mid=reference_mid, whereto=whereto
        )

        return HTMLResponse(
            content=content,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.post(
        "/streams/document/create_requirement", response_class=Response
    )
    def create_requirement(
        requirement_mid: str = Form(None),
        requirement_title: str = Form(None),
        requirement_statement: str = Form(None),
        reference_mid: str = Form(None),
        whereto: Optional[str] = Form(None),
    ):
        content = main_controller.create_requirement(
            requirement_mid=requirement_mid,
            requirement_title=requirement_title,
            requirement_statement=requirement_statement,
            reference_mid=reference_mid,
            whereto=whereto,
        )
        return HTMLResponse(
            content=content,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.get(
        "/streams/document/edit_requirement/{requirement_id}",
        response_class=Response,
    )
    def get_edit_requirement(requirement_id: str):
        content = main_controller.get_edit_requirement(requirement_id)
        # print(content)
        return HTMLResponse(
            content=content,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.post(
        "/streams/document/update_requirement", response_class=Response
    )
    def post_update_requirement(
        requirement_mid: str = Form(None),
        requirement_title: str = Form(None),
        requirement_statement: str = Form(None),
    ):
        content = main_controller.update_requirement(
            requirement_mid=requirement_mid,
            requirement_title=requirement_title,
            requirement_statement=requirement_statement,
        )
        return HTMLResponse(
            content=content,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.delete(
        "/streams/document/delete_section/{section_mid}",
        response_class=Response,
    )
    def delete_section(section_mid: str):
        content = main_controller.delete_section(
            section_mid=section_mid,
        )
        return HTMLResponse(
            content=content,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.delete(
        "/streams/document/delete_section/{section_mid}",
        response_class=Response,
    )
    def delete_requirement(requirement_mid: str):
        content = main_controller.delete_requirement(
            requirement_mid=requirement_mid,
        )
        return HTMLResponse(
            content=content,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    # Generic routes
    @router.get("/streams/document_tree/new_document", response_class=Response)
    def get_new_document():
        content = main_controller.get_new_document()
        return HTMLResponse(
            content=content,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.post(
        "/streams/document_tree/create_document", response_class=Response
    )
    def create_document(
        document_title: str = Form(None),
        document_path: str = Form(None),
    ):
        content = main_controller.create_document(
            document_title=document_title, document_path=document_path
        )
        return HTMLResponse(
            content=content,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.get("/{full_path:path}", response_class=Response)
    def get_incoming_request(full_path: str):
        print(full_path)

        if full_path.endswith(".html"):
            return get_document(full_path)
        if full_path.endswith(".css") or full_path.endswith(".js"):
            return get_asset(full_path)
        return HTMLResponse(
            content="Neither existing HTML or CSS file", status_code=404
        )

    def get_document(url_to_document: str):
        print(f"MainRounter.get_document> {url_to_document}")
        document_html_content = main_controller.get_document(url_to_document)
        return HTMLResponse(content=document_html_content, status_code=200)

    def get_asset(url_to_asset: str):
        print(f"MainRounter.get_asset> {url_to_asset}")

        # if not os.path.isfile(filename):
        # return Response(status_code=405)

        static_path = os.path.join(STRICTDOC_ROOT_PATH, "strictdoc/export/html")
        static_file = os.path.join(static_path, url_to_asset)
        content_type, _ = guess_type(static_file)

        assert os.path.isfile(static_file), f"{static_file}"
        with open(static_file, encoding="utf8") as f:
            content = f.read()
        return Response(content, media_type=content_type)

    return router
