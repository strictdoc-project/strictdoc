import os

from fastapi.testclient import TestClient

from strictdoc import environment
from strictdoc.cli.cli_arg_parser import ServerCommandConfig
from strictdoc.core.project_config import ProjectConfig
from strictdoc.server.app import create_app

PATH_TO_THIS_TEST_FOLDER = os.path.dirname(os.path.abspath(__file__))


def test_get_document():
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
    client = TestClient(
        create_app(
            project_config=project_config
        )
    )
    response = client.get("/01_hello_world/sample.html")
    assert response.status_code == 200
