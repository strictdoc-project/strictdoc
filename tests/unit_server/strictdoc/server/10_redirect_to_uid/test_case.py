import os

import pytest
from fastapi.testclient import TestClient

from strictdoc import environment
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
    project_config: ProjectConfig = ProjectConfig.default_config(
        environment=environment
    )
    project_config.integrate_server_config(server_config)
    return project_config

def test_redirect_to_existing_and_non_existing_uid(project_config: ProjectConfig):
    client = TestClient(
        create_app(
            project_config=project_config
        )
    )
    response = client.get("/UID/REQ-1", follow_redirects=False)
    assert response.status_code == 302

    response = client.get("/UID/MID_THAT_DOES_NOT_EXIST", follow_redirects=False)
    assert response.status_code == 404
