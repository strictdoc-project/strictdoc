import os

from fastapi.testclient import TestClient

from strictdoc.server.app import create_app

PATH_TO_THIS_TEST_FOLDER = os.path.dirname(os.path.abspath(__file__))


def test_get_document():
    client = TestClient(create_app(path_to_sdoc_tree=PATH_TO_THIS_TEST_FOLDER))
    response = client.get("/01_hello_world/sample.html")
    assert response.status_code == 200
