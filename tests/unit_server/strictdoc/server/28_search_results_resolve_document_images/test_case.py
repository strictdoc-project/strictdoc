import os
import re

import pytest
from fastapi.testclient import TestClient

from strictdoc.commands.server_config import ServerCommandConfig
from strictdoc.core.project_config import ProjectConfig
from strictdoc.server.app import create_app

PATH_TO_THIS_TEST_FOLDER = os.path.dirname(os.path.abspath(__file__))


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
    project_config.project_features = ["SEARCH"]
    project_config.integrate_server_config(server_config)
    return project_config


def test_search_results_link_document_images_from_the_document_folder(
    project_config: ProjectConfig,
):
    client = TestClient(create_app(project_config=project_config))

    response = client.get("/search?q=Findme")
    assert response.status_code == 200
    assert "REQ-1" in response.text

    image_sources = re.findall(r'<img[^>]*\bsrc="([^"]+)"', response.text)
    assert len(image_sources) == 1, image_sources
    image_source = image_sources[0]
    assert image_source.endswith("nested/_assets/picture.png"), image_source

    # The browser resolves the path against /search.
    if not image_source.startswith("/"):
        image_source = "/" + image_source
    response = client.get(image_source)
    assert response.status_code == 200, image_source
