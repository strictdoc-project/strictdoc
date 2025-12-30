"""
@relation(SDOC-SRS-4, scope=file)
"""

import os

import pytest
from fastapi.testclient import TestClient

from strictdoc.commands.server_config import ServerCommandConfig
from strictdoc.core.project_config import ProjectConfig
from strictdoc.server.app import create_app
from strictdoc.server.helpers.http import get_etag

PATH_TO_THIS_TEST_FOLDER = os.path.dirname(os.path.abspath(__file__))
PATH_TO_OUTPUT_FOLDER = os.path.join(PATH_TO_THIS_TEST_FOLDER, "output")


@pytest.fixture(scope="module")
def project_config():
    server_config = ServerCommandConfig(
        debug=False,
        command="server",
        input_path=PATH_TO_THIS_TEST_FOLDER,
        output_path=PATH_TO_OUTPUT_FOLDER,
        config=None,
        reload=False,
        host="127.0.0.1",
        port=8001,
    )
    project_config: ProjectConfig = ProjectConfig.default_config()
    project_config.integrate_server_config(server_config)
    return project_config


def test(project_config: ProjectConfig):
    client = TestClient(create_app(project_config=project_config))

    path_to_index = os.path.join(PATH_TO_OUTPUT_FOLDER, "html", "index.html")
    path_to_turbo = os.path.join(
        PATH_TO_OUTPUT_FOLDER, "html", "_static", "turbo.min.js"
    )

    #
    # Test getting the index.html.
    #
    response = client.get("/")
    assert response.status_code == 200

    response = client.get(
        "/", headers={"if-none-match": get_etag(path_to_index)}
    )
    assert response.status_code == 304

    response = client.get("/", headers={"if-none-match": "INVALID_ETAG"})
    assert response.status_code == 200

    #
    # Test getting an asset file.
    #
    response = client.get("/_static/turbo.min.js")
    assert response.status_code == 200

    response = client.get(
        "/_static/turbo.min.js",
        headers={"if-none-match": get_etag(path_to_turbo)},
    )
    assert response.status_code == 304

    response = client.get(
        "/_static/turbo.min.js", headers={"if-none-match": "INVALID_ETAG"}
    )
    assert response.status_code == 200
