import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from strictdoc.commands.server_config import ServerCommandConfig
from strictdoc.core.project_config import ProjectConfig, ProjectConfigLoader
from strictdoc.server.app import create_app

PATH_TO_THIS_TEST_FOLDER = Path(__file__).parent
DOCUMENT_MID = "398e37d756ea406f87ca83ec8e29c178"
REQUIREMENT_MID = "a5c6b14d5ee443149687fb9be69a7ede"


@pytest.mark.parametrize(
    ("filename", "content_type"),
    [
        ("picture.tiff", "image/tiff"),
        ("document.pdf", "application/pdf"),
    ],
)
def test_upload_asset_rejects_unsupported_format(
    tmp_path: Path, filename: str, content_type: str
) -> None:
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

    response = client.post(
        (
            "/actions/document/upload_asset"
            f"?document_mid={DOCUMENT_MID}"
            f"&requirement_mid={REQUIREMENT_MID}"
        ),
        files={
            "uploaded_files": (
                filename,
                b"unsupported file",
                content_type,
            )
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": (
            f"Unsupported format: {filename}. "
            "You can use SVG, PNG, GIF, JPG, JPEG, WebP, AVIF."
        )
    }
    assert not (input_path / "_assets").exists()
