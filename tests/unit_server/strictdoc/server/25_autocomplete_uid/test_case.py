"""
@relation(SDOC-SRS-120, scope=file)
"""

import os
import re
from typing import List, Tuple

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


def found_options(client: TestClient, query: str) -> List[Tuple[str, str]]:
    """
    Returns (UID, title) of each option.
    """

    response = client.get("/autocomplete/uid", params={"q": query})
    assert response.status_code == 200
    return re.findall(
        r'data-autocompletable-value="([^"]+)">'
        r'<span class="autocomplete_item_uid">[^<]+</span> ([^<]*)</li>',
        response.text,
    )


def test_nodes_without_sections(client: TestClient):
    assert found_options(client, "") == [
        ("REQ-1", "First requirement"),
        ("REQ-2", ""),
    ]


def test_match_by_uid_and_title(client: TestClient):
    assert found_options(client, "first") == [("REQ-1", "First requirement")]
    assert found_options(client, "req-2") == [("REQ-2", "")]
    assert found_options(client, "missing") == []
