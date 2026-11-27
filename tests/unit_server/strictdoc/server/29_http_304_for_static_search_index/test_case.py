"""
@relation(SDOC-SRS-4, scope=file)
"""

import os

import pytest
from fastapi.testclient import TestClient

from strictdoc.commands.server_config import ServerCommandConfig
from strictdoc.core.project_config import ProjectConfig
from strictdoc.server.app import create_app
from strictdoc.server.helpers.http import get_etag

PATH_TO_THIS_TEST_FOLDER = os.path.dirname(os.path.abspath(__file__))
PATH_TO_OUTPUT_FOLDER = os.path.join(PATH_TO_THIS_TEST_FOLDER, "output")
PATH_TO_SEARCH_INDEX = os.path.join(
    PATH_TO_OUTPUT_FOLDER, "html", "_static", "static_html_search_index.js"
)
URL_TO_SEARCH_INDEX = "/_static/static_html_search_index.js"


@pytest.fixture(scope="module")
def project_config() -> ProjectConfig:
    server_config = ServerCommandConfig(
        debug=False,
        command="server",
        input_path=PATH_TO_THIS_TEST_FOLDER,
        output_path=PATH_TO_OUTPUT_FOLDER,
        config=None,
        reload=False,
        host="127.0.0.1",
        port=8001,
    )
    project_config: ProjectConfig = ProjectConfig.default_config()
    project_config.integrate_server_config(server_config)
    return project_config


def test(project_config: ProjectConfig) -> None:
    client = TestClient(create_app(project_config=project_config))

    #
    # The first request generates the search index.
    #
    response = client.get(URL_TO_SEARCH_INDEX)
    assert response.status_code == 200
    mtime_ns_after_generation = os.stat(PATH_TO_SEARCH_INDEX).st_mtime_ns
    etag_after_generation = get_etag(PATH_TO_SEARCH_INDEX)

    #
    # A request without an ETag gets the existing search index.
    #
    response = client.get(URL_TO_SEARCH_INDEX)
    assert response.status_code == 200
    assert (
        os.stat(PATH_TO_SEARCH_INDEX).st_mtime_ns == mtime_ns_after_generation
    )

    #
    # A request with the ETag of the existing search index gets 304.
    #
    response = client.get(
        URL_TO_SEARCH_INDEX, headers={"if-none-match": etag_after_generation}
    )
    assert response.status_code == 304

    response = client.get(
        URL_TO_SEARCH_INDEX, headers={"if-none-match": "INVALID_ETAG"}
    )
    assert response.status_code == 200
    assert (
        os.stat(PATH_TO_SEARCH_INDEX).st_mtime_ns == mtime_ns_after_generation
    )

    #
    # A search index that is older than the traceability index is generated
    # again.
    #
    os.utime(PATH_TO_SEARCH_INDEX, (0, 0))
    response = client.get(
        URL_TO_SEARCH_INDEX, headers={"if-none-match": etag_after_generation}
    )
    assert response.status_code == 200
    assert os.stat(PATH_TO_SEARCH_INDEX).st_mtime_ns > 0
