import os

from fastapi.testclient import TestClient

from strictdoc import environment
from strictdoc.cli.cli_arg_parser import ServerCommandConfig
from strictdoc.core.project_config import ProjectConfig
from strictdoc.server.app import create_app

PATH_TO_THIS_TEST_FOLDER = os.path.dirname(os.path.abspath(__file__))


def test_get_document():
    config = ServerCommandConfig(
        input_path=PATH_TO_THIS_TEST_FOLDER,
        output_path=os.path.join(PATH_TO_THIS_TEST_FOLDER, "output"),
        config_path=None,
        reload=False,
        port=8001,
    )
    client = TestClient(
        create_app(
            server_config=config, project_config=ProjectConfig.default_config(
                environment=environment
            )
        )
    )
    response = client.get("/sample.html")
    assert response.status_code == 200
