import os
import re
import shutil

from fastapi.testclient import TestClient

from strictdoc.cli.cli_arg_parser import ServerCommandConfig
from strictdoc.server.app import create_app

PATH_TO_THIS_TEST_FOLDER = os.path.dirname(os.path.abspath(__file__))
PATH_TO_OUTPUT_FOLDER = os.path.join(PATH_TO_THIS_TEST_FOLDER, "output")


def test_export_document_to_reqif():
    shutil.rmtree(PATH_TO_OUTPUT_FOLDER, ignore_errors=True)

    config = ServerCommandConfig(
        input_path=PATH_TO_THIS_TEST_FOLDER,
        output_path=PATH_TO_OUTPUT_FOLDER,
        reload=False,
    )
    client = TestClient(create_app(config=config))
    response = client.get("/02_export_document_to_reqif/sample.html")
    assert response.status_code == 200

    response_body = response.content.decode()

    match_document_mid = re.search(
        r"/reqif/export_document/(?P<document_mid>[a-z0-9]+)", response_body
    )
    assert match_document_mid is not None
    document_mid = match_document_mid.group("document_mid")

    response = client.get(f"/reqif/export_document/{document_mid}")
    assert response.status_code == 200
    assert "<REQ-IF xmlns=" in response.content.decode()
