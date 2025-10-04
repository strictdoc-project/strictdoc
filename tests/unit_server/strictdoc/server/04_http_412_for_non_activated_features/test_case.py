import os

import pytest
from fastapi.testclient import TestClient

from strictdoc.cli.cli_arg_parser import ServerCommandConfig
from strictdoc.core.project_config import ProjectConfig
from strictdoc.server.app import create_app

PATH_TO_THIS_TEST_FOLDER = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture(scope="module")
def project_config():
    server_config = ServerCommandConfig(
        input_path=PATH_TO_THIS_TEST_FOLDER,
        output_path=os.path.join(PATH_TO_THIS_TEST_FOLDER, "output"),
        config_path=None,
        reload=False,
        host="127.0.0.1",
        port=8001,
    )
    project_config: ProjectConfig = ProjectConfig.default_config()
    project_config.integrate_server_config(server_config)
    return project_config

def test(project_config: ProjectConfig):
    client = TestClient(
        create_app(
            project_config=project_config
        )
    )
    response = client.get("/traceability_matrix.html")
    assert response.status_code == 412

    response = client.get("/source_coverage.html")
    assert response.status_code == 412

    response = client.get("/tree_map.html")
    assert response.status_code == 412

    response = client.get("/project_statistics.html")
    assert response.status_code == 412

    response = client.get("/some_document-PDF.html")
    assert response.status_code == 412

    response = client.get("/some_document.standalone.html")
    assert response.status_code == 412

    response = client.get("/export_html2pdf/NOT_RELEVANT")
    assert response.status_code == 412

    response = client.get("/diff")
    assert response.status_code == 412
