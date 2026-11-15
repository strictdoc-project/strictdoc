from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from strictdoc.commands.server_config import ServerCommandConfig
from strictdoc.core.project_config import ProjectConfig
from strictdoc.server.app import create_app


@pytest.mark.parametrize("relaxed_mode", [False, True])
def test_unresolved_references_server_page(
    tmp_path: Path,
    relaxed_mode: bool,
) -> None:
    input_path = tmp_path / "project"
    input_path.mkdir()
    statement = (
        "An unresolved reference: [LINK: MISSING-TARGET]."
        if relaxed_mode
        else "A valid statement."
    )
    (input_path / "input.sdoc").write_text(
        "[DOCUMENT]\nTITLE: Server project\n\n"
        "[REQUIREMENT]\nUID: REQ-001\nTITLE: Requirement\n"
        f"STATEMENT: >>>\n{statement}\n<<<\n",
        encoding="utf-8",
    )
    server_config = ServerCommandConfig(
        debug=False,
        command="server",
        input_path=str(input_path),
        output_path=str(tmp_path / "output"),
        config=None,
        reload=False,
        host="127.0.0.1",
        port=8001,
        relaxed_mode=relaxed_mode,
    )
    project_config = ProjectConfig()
    project_config.integrate_server_config(server_config)
    client = TestClient(create_app(project_config=project_config))

    response = client.get("/unresolved_references.html")

    assert response.status_code == (200 if relaxed_mode else 412)
    if relaxed_mode:
        assert "MISSING-TARGET" in response.text
        assert "STATEMENT" in response.text
        assert 'href="project/input.html#' in response.text
        repeated_response = client.get("/unresolved_references.html")
        assert repeated_response.status_code == 200
        assert "MISSING-TARGET" in repeated_response.text
    index_response = client.get("/")
    assert index_response.status_code == 200
    assert (
        'data-testid="project-tree-link-unresolved-references"'
        in index_response.text
    ) is relaxed_mode
