import json
import os

import pytest
from fastapi.testclient import TestClient

from strictdoc.commands.server_config import ServerCommandConfig
from strictdoc.core.project_config import ProjectConfig
from strictdoc.server.app import create_app

PATH_TO_THIS_TEST_FOLDER = os.path.dirname(os.path.abspath(__file__))
PREVIEWS_PREFIX = (
    "window.StrictDoc.relationPreviews[document.currentScript.src] = "
)


@pytest.fixture(scope="module")
def project_config():
    server_config = ServerCommandConfig(
        debug=False,
        command="server",
        input_path=PATH_TO_THIS_TEST_FOLDER,
        output_path=os.path.join(PATH_TO_THIS_TEST_FOLDER, "output"),
        config=None,
        reload=False,
        host="127.0.0.1",
        port=8001,
    )
    project_config: ProjectConfig = ProjectConfig.default_config()
    project_config.integrate_server_config(server_config)
    return project_config


def read_previews(response) -> dict:
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/javascript")
    payload = response.text.split(PREVIEWS_PREFIX, 1)[1]
    return json.loads(payload.rstrip().rstrip(";"))


def test_relation_previews_are_rendered_on_request(
    project_config: ProjectConfig,
):
    client = TestClient(create_app(project_config=project_config))

    # REQ-PARENT-1 has a child in child.sdoc. REQ-SAME-CHILD is only linked
    # from its own page, REQ-UNRELATED has no relations.
    previews = read_previews(
        client.get("/24_relation_previews/parent-relation-previews.js")
    )
    assert list(previews.keys()) == ["REQ-PARENT-1"]
    assert "<strong>markup</strong>" in previews["REQ-PARENT-1"]

    previews = read_previews(
        client.get("/24_relation_previews/child-relation-previews.js")
    )
    assert list(previews.keys()) == ["REQ-CROSS-CHILD"]


def test_relation_previews_for_unknown_document_is_404(
    project_config: ProjectConfig,
):
    client = TestClient(create_app(project_config=project_config))
    response = client.get("/24_relation_previews/missing-relation-previews.js")
    assert response.status_code == 404
