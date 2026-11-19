import os

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
    # No TABLE_SCREEN, TRACEABILITY_SCREEN or DEEP_TRACEABILITY_SCREEN.
    project_config.project_features = []
    project_config.integrate_server_config(server_config)
    return project_config


def test_document_views_of_non_activated_screens_return_404(
    project_config: ProjectConfig,
):
    client = TestClient(create_app(project_config=project_config))

    document_url = f"/{os.path.basename(PATH_TO_THIS_TEST_FOLDER)}/sample"

    response = client.get(f"{document_url}.html")
    assert response.status_code == 200

    for view_ in ("TABLE", "TRACE", "DEEP-TRACE"):
        response = client.get(f"{document_url}-{view_}.html")
        assert response.status_code == 404, view_
