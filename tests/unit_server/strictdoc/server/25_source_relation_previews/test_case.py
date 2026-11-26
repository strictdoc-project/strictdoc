import json
import os
from pathlib import Path

from fastapi.testclient import TestClient

from strictdoc.commands.server_config import ServerCommandConfig
from strictdoc.core.project_config import ProjectConfig, ProjectConfigLoader
from strictdoc.server.app import create_app

PATH_TO_THIS_TEST_FOLDER = os.path.dirname(os.path.abspath(__file__))
PATH_TO_CONFIG = os.path.join(PATH_TO_THIS_TEST_FOLDER, "strictdoc_config.py")
PREVIEWS_PREFIX = (
    "window.StrictDoc.relationPreviews[document.currentScript.src] = "
)


def create_client(tmp_path: Path) -> TestClient:
    server_config = ServerCommandConfig(
        debug=False,
        command="server",
        input_path=PATH_TO_THIS_TEST_FOLDER,
        output_path=str(tmp_path / "output"),
        config=PATH_TO_CONFIG,
        reload=False,
        host="127.0.0.1",
        port=8001,
    )
    project_config: ProjectConfig = (
        ProjectConfigLoader.load_using_server_config(server_config)
    )
    return TestClient(create_app(project_config=project_config))


def test_source_relation_previews_are_rendered_on_request(
    tmp_path: Path,
) -> None:
    client = create_client(tmp_path)

    response = client.get("/_source_files/src/example.py-relation-previews.js")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/javascript")
    payload = response.text.split(PREVIEWS_PREFIX, 1)[1]
    previews = json.loads(payload.rstrip().rstrip(";"))
    assert list(previews.keys()) == ["1", "5"]
    assert len(previews["1"]) == 2
    assert "&lt;short&gt; &amp; sweet" in previews["1"][1]
    assert len(previews["5"]) == 15
    assert '<span class="nf">long_function</span>' in previews["5"][0]


def test_source_relation_previews_for_unknown_file_is_404(
    tmp_path: Path,
) -> None:
    client = create_client(tmp_path)

    response = client.get("/_source_files/src/missing.py-relation-previews.js")

    assert response.status_code == 404
