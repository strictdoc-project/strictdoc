import os

import pytest
from fastapi.testclient import TestClient

from strictdoc import environment
from strictdoc.cli.cli_arg_parser import ServerCommandConfig
from strictdoc.core.project_config import ProjectConfig, ProjectConfigLoader
from strictdoc.server.app import create_app

PATH_TO_THIS_TEST_FOLDER = os.path.dirname(os.path.abspath(__file__))
PATH_TO_CONFIG = os.path.join(PATH_TO_THIS_TEST_FOLDER, "strictdoc.toml")
assert os.path.exists(PATH_TO_CONFIG)

@pytest.fixture(scope="module")
def project_config():
    server_config = ServerCommandConfig(
        input_path=PATH_TO_THIS_TEST_FOLDER,
        output_path=os.path.join(PATH_TO_THIS_TEST_FOLDER, "output"),
        config_path=PATH_TO_CONFIG,
        reload=False,
        host="127.0.0.1",
        port=8001,
    )
    project_config: ProjectConfig = ProjectConfigLoader.load_from_path_or_get_default(
        path_to_config=PATH_TO_CONFIG,
        environment=environment
    )
    project_config.integrate_server_config(server_config)
    return project_config

def test(project_config: ProjectConfig):
    client = TestClient(
        create_app(
            project_config=project_config
        )
    )
    response = client.get("/diff?tab=foo")
    assert response.status_code == 400

    response = client.get("/diff")
    assert response.status_code == 200
