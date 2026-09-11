import shutil
from pathlib import Path

from fastapi.testclient import TestClient
from httpx import Response

from strictdoc.commands.server_config import ServerCommandConfig
from strictdoc.core.project_config import ProjectConfig, ProjectConfigLoader
from strictdoc.server.app import create_app

PATH_TO_THIS_TEST_FOLDER = Path(__file__).parent
DOCUMENT_MID = "398e37d756ea406f87ca83ec8e29c178"
REQUIREMENT_MID = "a5c6b14d5ee443149687fb9be69a7ede"
UNKNOWN_DOCUMENT_MID = "ffffffffffffffffffffffffffffffff"


def test_upload_asset_endpoint(tmp_path: Path) -> None:
    input_path = tmp_path / "input"
    input_path.mkdir()
    shutil.copyfile(
        PATH_TO_THIS_TEST_FOLDER / "document.sdoc",
        input_path / "document.sdoc",
    )
    server_config = ServerCommandConfig(
        debug=False,
        command="server",
        input_path=str(input_path),
        output_path=str(tmp_path / "output"),
        config=None,
        reload=False,
        host="127.0.0.1",
        port=8001,
    )
    project_config: ProjectConfig = (
        ProjectConfigLoader.load_using_server_config(server_config)
    )
    client = TestClient(create_app(project_config=project_config))

    def upload(
        files: list[tuple[str, bytes, str]],
        *,
        document_mid: str = DOCUMENT_MID,
        requirement_mid: str = REQUIREMENT_MID,
    ) -> Response:
        return client.post(
            (
                "/actions/document/upload_asset"
                f"?document_mid={document_mid}"
                f"&requirement_mid={requirement_mid}"
            ),
            files=[
                ("uploaded_files", (filename, contents, content_type))
                for filename, contents, content_type in files
            ],
        )

    for filename, content_type in (
        ("picture.tiff", "image/tiff"),
        ("document.pdf", "application/pdf"),
    ):
        response = upload([(filename, b"unsupported file", content_type)])
        assert response.status_code == 400
        assert response.json() == {
            "detail": (
                f"Unsupported format: {filename}. "
                "You can use SVG, PNG, GIF, JPG, JPEG, WebP, AVIF."
            )
        }
        assert not (input_path / "_assets").exists()

    response = upload(
        [("picture.svg", b"<svg/>", "image/svg+xml")],
        requirement_mid="invalid-mid",
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid requirement MID format"}
    assert not (input_path / "_assets").exists()

    response = upload(
        [("picture.svg", b"<svg/>", "image/svg+xml")],
        document_mid=UNKNOWN_DOCUMENT_MID,
    )
    assert response.status_code == 404
    assert response.json() == {
        "detail": (f"Active Document with MID {UNKNOWN_DOCUMENT_MID} not found")
    }
    assert not (input_path / "_assets").exists()

    response = upload(
        [
            ("pair.svg", b"<svg/>", "image/svg+xml"),
            ("pair.png", b"png", "image/png"),
            ("separate.gif", b"gif", "image/gif"),
            ("raster.jpg", b"jpg", "image/jpeg"),
            ("raster.png", b"png", "image/png"),
            ("second.svg", b"<svg/>", "image/svg+xml"),
            ("second.webp", b"webp", "image/webp"),
        ]
    )
    assert response.status_code == 200
    uri_base = f"./_assets/{REQUIREMENT_MID}"
    assert response.json() == {
        "images": {
            "pair.svg": f"{uri_base}/pair.*",
            "pair.png": f"{uri_base}/pair.*",
            "separate.gif": f"{uri_base}/separate.gif",
            "raster.jpg": f"{uri_base}/raster.jpg",
            "raster.png": f"{uri_base}/raster.png",
            "second.svg": f"{uri_base}/second.*",
            "second.webp": f"{uri_base}/second.*",
        }
    }

    asset_directory = input_path / "_assets" / REQUIREMENT_MID
    for filename in (
        "pair.svg",
        "pair.png",
        "separate.gif",
        "raster.jpg",
        "raster.png",
        "second.svg",
        "second.webp",
    ):
        assert (asset_directory / filename).is_file()

    asset_response = client.get(
        f"/input/_assets/{REQUIREMENT_MID}/separate.gif"
    )
    assert asset_response.status_code == 200
    assert asset_response.content == b"gif"

    response = upload([("incremental.png", b"png", "image/png")])
    assert response.status_code == 200
    assert response.json() == {
        "images": {"incremental.png": f"{uri_base}/incremental.png"}
    }

    response = upload([("incremental.svg", b"<svg/>", "image/svg+xml")])
    assert response.status_code == 200
    assert response.json() == {
        "images": {"incremental.svg": f"{uri_base}/incremental.*"}
    }

    response = upload(
        [("../../outside.svg", b"<svg>safe</svg>", "image/svg+xml")]
    )
    assert response.status_code == 200
    assert response.json() == {
        "images": {"outside.svg": f"{uri_base}/outside.svg"}
    }
    assert (asset_directory / "outside.svg").read_bytes() == b"<svg>safe</svg>"
    assert not (tmp_path / "outside.svg").exists()
