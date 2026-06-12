import os
import re
from typing import List, Tuple

import pytest
from fastapi.testclient import TestClient

from strictdoc.commands.server_config import ServerCommandConfig
from strictdoc.core.project_config import ProjectConfig, ProjectConfigLoader
from strictdoc.server.app import create_app

PATH_TO_THIS_TEST_FOLDER = os.path.dirname(os.path.abspath(__file__))
PATH_TO_CONFIG = os.path.join(PATH_TO_THIS_TEST_FOLDER, "strictdoc_config.py")
assert os.path.exists(PATH_TO_CONFIG)

REGEX_FRAGMENT_SRC = re.compile(
    r'src="(/fragments/document/[^"]+)"',
)
REGEX_FRAGMENT_URL_PARTS = re.compile(
    r"/fragments/document/(?P<document_mid>[0-9a-f]+)/chunk"
    r"\?from_node=(?P<from_node>[0-9a-f]+)"
    r"&count=(?P<count>\d+)"
    r"&chunk=(?P<chunk>\d+)"
)


@pytest.fixture(scope="module")
def client() -> TestClient:
    server_config = ServerCommandConfig(
        debug=False,
        command="server",
        input_path=PATH_TO_THIS_TEST_FOLDER,
        output_path=os.path.join(PATH_TO_THIS_TEST_FOLDER, "output"),
        config=PATH_TO_CONFIG,
        reload=False,
        host="127.0.0.1",
        port=8001,
    )
    project_config: ProjectConfig = (
        ProjectConfigLoader.load_using_server_config(server_config)
    )
    return TestClient(create_app(project_config=project_config))


def get_placeholder_srcs(client: TestClient) -> Tuple[str, List[str]]:
    response = client.get("/21_chunked_document_fragments/sample.html")
    assert response.status_code == 200
    srcs = [
        src.replace("&amp;", "&")
        for src in REGEX_FRAGMENT_SRC.findall(response.text)
    ]
    return response.text, srcs


def test_document_screen_renders_chunked(client: TestClient) -> None:
    document_html, placeholder_srcs = get_placeholder_srcs(client)

    # The first chunk is rendered inline.
    assert 'id="document-chunk-0"' in document_html

    # The remaining chunks are lazily-loaded placeholders: 30 nodes with
    # threshold 10 produce chunks of 10 (chunk 0 inline, chunks 1-2 lazy).
    assert document_html.count('data-testid="document-chunk-placeholder"') == 2
    assert document_html.count('loading="lazy"') == 2
    assert len(placeholder_srcs) == 2
    for placeholder_src in placeholder_srcs:
        match = REGEX_FRAGMENT_URL_PARTS.search(placeholder_src)
        assert match is not None, placeholder_src
        assert match.group("count") == "10"


def test_toc_links_carry_chunk_frame(client: TestClient) -> None:
    # Each TOC entry is stamped with the id of the lazy chunk that holds it,
    # so the deep-link script (toc_chunk_navigation.js) can force-load the
    # right chunk before scrolling to a target in an unloaded chunk. The
    # 30-requirement fixture splits into chunks 0, 1, 2, so all three frame
    # ids must appear in the TOC.
    document_html, _ = get_placeholder_srcs(client)

    assert 'data-chunk-frame="document-chunk-0"' in document_html
    assert 'data-chunk-frame="document-chunk-1"' in document_html
    assert 'data-chunk-frame="document-chunk-2"' in document_html


def test_document_chunk_fragment_returns_chunk_nodes(
    client: TestClient,
) -> None:
    _, placeholder_srcs = get_placeholder_srcs(client)

    response = client.get(placeholder_srcs[0])

    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-cache"
    assert 'id="document-chunk-1"' in response.text
    # One closing </sdoc-node> tag and one per-node turbo-frame per node.
    assert response.text.count("</sdoc-node>") == 10
    assert response.text.count('<turbo-frame id="article-') == 10
    # Chunk 1 must contain exactly the 11-20 window of requirements:
    # a requirement unique to this window is present, while requirements
    # from the preceding (1-10) and following (21-30) windows are not.
    assert "Requirement 15" in response.text
    assert "Requirement 5" not in response.text
    assert "Requirement 25" not in response.text


def test_document_chunk_count_must_be_validated(client: TestClient) -> None:
    _, placeholder_srcs = get_placeholder_srcs(client)
    match = REGEX_FRAGMENT_URL_PARTS.search(placeholder_srcs[0])
    assert match is not None
    document_mid = match.group("document_mid")
    from_node = match.group("from_node")

    base_url = f"/fragments/document/{document_mid}/chunk"

    response = client.get(f"{base_url}?from_node={from_node}&count=0&chunk=1")
    assert response.status_code == 422

    response = client.get(f"{base_url}?from_node={from_node}&count=101&chunk=1")
    assert response.status_code == 422

    response = client.get(f"{base_url}?from_node={from_node}&count=10&chunk=-1")
    assert response.status_code == 422


def test_document_chunk_unknown_document_returns_404(
    client: TestClient,
) -> None:
    response = client.get(
        "/fragments/document/0123456789abcdef0123456789abcdef/chunk"
        "?from_node=0123456789abcdef0123456789abcdef&count=10&chunk=1"
    )
    assert response.status_code == 404


def test_document_chunk_unknown_from_node_returns_empty_frame(
    client: TestClient,
) -> None:
    _, placeholder_srcs = get_placeholder_srcs(client)
    match = REGEX_FRAGMENT_URL_PARTS.search(placeholder_srcs[0])
    assert match is not None
    document_mid = match.group("document_mid")

    response = client.get(
        f"/fragments/document/{document_mid}/chunk"
        "?from_node=ffffffffffffffffffffffffffffffff&count=10&chunk=1"
    )

    assert response.status_code == 200
    assert 'id="document-chunk-1"' in response.text
    assert "<sdoc-node" not in response.text


def test_small_document_is_not_chunked(client: TestClient) -> None:
    response = client.get("/21_chunked_document_fragments/small.html")

    assert response.status_code == 200
    # A non-chunked document renders its nodes inline, so none of the chunk
    # turbo-frames or lazy placeholders are emitted. (The string
    # "document-chunk-" still appears in the MathJax/Mermaid deferral scripts,
    # which are enabled by default, so we assert on the actual chunk markup.)
    assert 'id="document-chunk-' not in response.text
    assert 'data-testid="document-chunk-placeholder"' not in response.text
