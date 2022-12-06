import os
from mimetypes import guess_type
from typing import Optional, List

from fastapi import Form, APIRouter
from starlette.responses import HTMLResponse, Response
from starlette.websockets import WebSocket, WebSocketDisconnect

from strictdoc import __version__, STRICTDOC_ROOT_PATH
from strictdoc.cli.cli_arg_parser import ServerCommandConfig
from strictdoc.server.controllers.main_controller import (
    MainController,
    NodeCreationOrder,
)


def create_main_router(config: ServerCommandConfig) -> APIRouter:
    router = APIRouter()

    main_controller = MainController(config=config)

    @router.get("/")
    def get_root():
        return get_incoming_request("index.html")

    @router.get("/ping")
    def get_ping():
        return f"StrictDoc v{__version__}"

    @router.get("/actions/document/new_section", response_class=Response)
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

    @router.post("/actions/document/create_section", response_class=Response)
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

    @router.get(
        "/actions/document/edit_section/{section_id}", response_class=Response
    )
    def get_edit_section(section_id: str):
        content = main_controller.get_edit_section(section_id)
        return HTMLResponse(
            content=content,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.post("/actions/document/update_section", response_class=Response)
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

    @router.get("/actions/document/cancel_new_section", response_class=Response)
    def cancel_new_section(section_mid: str):
        content = main_controller.cancel_new_section(section_mid=section_mid)
        return HTMLResponse(
            content=content,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.get(
        "/actions/document/cancel_edit_section", response_class=Response
    )
    def cancel_edit_section(
        section_mid: str,
    ):
        content = main_controller.cancel_edit_section(
            section_mid=section_mid,
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
        content = main_controller.get_edit_document_freetext(document_id)
        return HTMLResponse(
            content=content,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.get(
        "/actions/document/cancel_edit_freetext", response_class=Response
    )
    def cancel_edit_document_freetext(document_mid: str):
        content = main_controller.cancel_edit_document_freetext(document_mid)
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

    @router.get("/actions/document/new_requirement", response_class=Response)
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
        "/actions/document/create_requirement", response_class=Response
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
        "/actions/document/edit_requirement/{requirement_id}",
        response_class=Response,
    )
    def get_edit_requirement(requirement_id: str):
        content = main_controller.get_edit_requirement(requirement_id)
        return HTMLResponse(
            content=content,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.post(
        "/actions/document/update_requirement", response_class=Response
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

    @router.get(
        "/actions/document/cancel_new_requirement", response_class=Response
    )
    def cancel_new_requirement(requirement_mid: str):
        content = main_controller.cancel_new_requirement(
            requirement_mid=requirement_mid
        )
        return HTMLResponse(
            content=content,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.get(
        "/actions/document/cancel_edit_requirement", response_class=Response
    )
    def cancel_edit_requirement(requirement_mid: str):
        content = main_controller.cancel_edit_requirement(
            requirement_mid=requirement_mid,
        )
        return HTMLResponse(
            content=content,
            status_code=200,
            headers={
                "Content-Type": "text/vnd.turbo-stream.html",
            },
        )

    @router.delete(
        "/actions/document/delete_section/{section_mid}",
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
        "/actions/document/delete_section/{section_mid}",
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
    @router.get("/actions/document_tree/new_document", response_class=Response)
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
        "/actions/document_tree/create_document", response_class=Response
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
        if full_path.endswith(".html"):
            return get_document(full_path)
        if (
            full_path.endswith(".css")
            or full_path.endswith(".js")
        ):
            return get_asset(full_path)
        if full_path.endswith(".ico"):
            return get_asset_binary(full_path)

        return HTMLResponse(
            content="Not Found", status_code=404
        )

    def get_document(url_to_document: str):
        document_html_content = main_controller.get_document(url_to_document)
        return HTMLResponse(content=document_html_content, status_code=200)

    def get_asset(url_to_asset: str):
        static_path = os.path.join(STRICTDOC_ROOT_PATH, "strictdoc/export/html")
        static_file = os.path.join(static_path, url_to_asset)
        content_type, _ = guess_type(static_file)

        if not os.path.isfile(static_file):
            return Response(
                content=f"File not found: {url_to_asset}",
                status_code=404,
                media_type=content_type
            )
        with open(static_file, encoding="utf8") as f:
            content = f.read()
        return Response(content, media_type=content_type)

    def get_asset_binary(url_to_asset: str):
        static_path = os.path.join(STRICTDOC_ROOT_PATH, "strictdoc/export/html")

        static_file = os.path.join(static_path, url_to_asset)
        content_type, _ = guess_type(static_file)

        if not os.path.isfile(static_file):
            return Response(
                content=f"File not found: {url_to_asset}",
                status_code=404,
                media_type=content_type
            )

        with open(static_file, "rb") as f:
            content = f.read()
        return Response(content, media_type=content_type)

    # Websockets solution based on:
    # https://fastapi.tiangolo.com/advanced/websockets/
    class ConnectionManager:
        def __init__(self):
            self.active_connections: List[WebSocket] = []

        async def connect(self, websocket: WebSocket):
            await websocket.accept()
            self.active_connections.append(websocket)

        def disconnect(self, websocket: WebSocket):
            self.active_connections.remove(websocket)

        @staticmethod
        async def send_personal_message(message: str, websocket: WebSocket):
            await websocket.send_text(message)

        async def broadcast(self, message: str):
            for connection in self.active_connections:
                await connection.send_text(message)

    manager = ConnectionManager()

    @router.websocket("/ws/{client_id}")
    async def websocket_endpoint(websocket: WebSocket, client_id: int):
        await manager.connect(websocket)
        try:
            while True:
                _ = await websocket.receive_text()
                # Do nothing for now.
        except WebSocketDisconnect:
            manager.disconnect(websocket)
            await manager.broadcast(
                f"Websocket: Client #{client_id} disconnected"
            )

    return router
