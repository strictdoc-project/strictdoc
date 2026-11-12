"""
@relation(SDOC-SRS-208, scope=file)
"""

import os
import re
from typing import List, Optional

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


SECOND_DOCUMENT_MID = "5f0c2d6b8a9e4f1aa3c7d2e1b4f60789"


def found_uids(
    client: TestClient, query: str, document_mid: Optional[str] = None
) -> List[str]:
    params = {"q": query}
    if document_mid is not None:
        params["document_mid"] = document_mid
    response = client.get("/autocomplete/link", params=params)
    assert response.status_code == 200
    return re.findall(r'data-autocompletable-value="([^"]+)"', response.text)


def test_all_kinds_of_targets(client: TestClient):
    assert found_uids(client, "") == [
        "DOC-1",
        "SECT-1",
        "ANCHOR-1",
        "ANCHOR-2",
        "REQ-1",
        "SECOND-1",
    ]


def test_current_document_first(client: TestClient):
    assert found_uids(client, "", document_mid=SECOND_DOCUMENT_MID) == [
        "SECOND-1",
        "DOC-1",
        "SECT-1",
        "ANCHOR-1",
        "ANCHOR-2",
        "REQ-1",
    ]
    assert found_uids(client, "requirement", SECOND_DOCUMENT_MID) == [
        "SECOND-1",
        "REQ-1",
    ]


def test_match_by_uid_and_title(client: TestClient):
    assert found_uids(client, "sect") == ["SECT-1"]
    assert found_uids(client, "overview") == ["SECT-1"]
    assert found_uids(client, "anchor title") == ["ANCHOR-1"]
    assert found_uids(client, "first requirement") == ["REQ-1"]
    assert found_uids(client, "sample") == ["DOC-1"]
    assert found_uids(client, "missing") == []


def test_kind_of_each_target(client: TestClient):
    response = client.get("/autocomplete/link", params={"q": ""})
    kinds = re.findall(
        r'<span class="field-widgets-link-kind">([^<]+)</span>', response.text
    )
    assert kinds == [
        "DOCUMENT",
        "SECTION",
        "ANCHOR",
        "ANCHOR",
        "REQUIREMENT",
        "REQUIREMENT",
    ]


def test_no_query_returns_nothing(client: TestClient):
    response = client.get("/autocomplete/link")
    assert response.status_code == 200
    assert response.text == ""
