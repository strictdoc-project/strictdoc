import os

from fastapi.testclient import TestClient

from strictdoc.cli.cli_arg_parser import ServerCommandConfig
from strictdoc.server.app import create_app

PATH_TO_THIS_TEST_FOLDER = os.path.dirname(os.path.abspath(__file__))


def test_get_document():
    config = ServerCommandConfig(
        input_path=PATH_TO_THIS_TEST_FOLDER,
        output_path=os.path.join(PATH_TO_THIS_TEST_FOLDER, "output"),
        reload=False,
    )
    client = TestClient(create_app(config=config))
    response = client.get("/01_hello_world/sample.html")
    assert response.status_code == 200
