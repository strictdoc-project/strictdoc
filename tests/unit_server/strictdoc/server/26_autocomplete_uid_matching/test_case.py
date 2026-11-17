"""
@relation(SDOC-SRS-120, scope=file)
"""

import os
import re
from typing import List

import pytest
from fastapi.testclient import TestClient

from strictdoc.commands.server_config import ServerCommandConfig
from strictdoc.core.project_config import ProjectConfig
from strictdoc.server.app import create_app

PATH_TO_THIS_TEST_FOLDER = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture(scope="module")
def client():
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
    project_config.integrate_server_config(server_config)
    return TestClient(create_app(project_config=project_config))


def found_uids(client: TestClient, query: str) -> List[str]:
    response = client.get("/autocomplete/uid", params={"q": query})
    assert response.status_code == 200
    return re.findall(r'data-autocompletable-value="([^"]+)"', response.text)


def test_exact_uid_comes_first(client: TestClient):
    assert found_uids(client, "REQ-1") == ["REQ-1", "REQ-10"]


def test_exact_uid_of_section_is_not_an_option(client: TestClient):
    assert found_uids(client, "REQ-1-SECTION") == []
