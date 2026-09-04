"""
Regression test for the bug this fixes: editing a REQUIREMENT's STATEMENT
through the web UI (table__update_node_field_multiline, the same command
class create_requirement/document__update_requirement/etc. all go through)
used to leave RequirementIntegrityAnalyzer's warnings stale until the server
was restarted or the .sdoc file was touched from outside the running
server — because write_document_to_file() explicitly inhibits the file
watcher that would otherwise trigger a re-analysis. See
strictdoc/server/routers/main_router.py::write_document_to_file() and
strictdoc/core/analyzers/requirement_integrity_analyzer.py.
"""

import os
import shutil

import pytest
from fastapi.testclient import TestClient

from strictdoc.commands.server_config import ServerCommandConfig
from strictdoc.core.analyzers.requirement_integrity_analyzer import (
    CANNOT_CONVERT_MESSAGE,
)
from strictdoc.core.project_config import ProjectConfig
from strictdoc.server.app import create_app

PATH_TO_THIS_TEST_FOLDER = os.path.dirname(os.path.abspath(__file__))

# The REQ-6 case from the bug report: prose with no ЕСЛИ/КОГДА/IF shape.
UNCONVERTIBLE_STATEMENT = "Должен быть в наличии корд (механика, платформа)"


@pytest.fixture
def project_config(tmp_path) -> ProjectConfig:
    # The server writes REQ-1's STATEMENT back to sample.sdoc as part of
    # this test (that's the whole point — it's a write-endpoint test), so
    # it runs against a throwaway copy rather than the committed fixture:
    # otherwise every test run would leave the tracked sample.sdoc modified
    # (StrictDoc's writer also normalizes formatting on every write, e.g.
    # adding a document MID / the grammar's default TEXT element), and a
    # second run would start from already-mutated content.
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    shutil.copy(
        os.path.join(PATH_TO_THIS_TEST_FOLDER, "sample.sdoc"),
        project_dir / "sample.sdoc",
    )

    server_config = ServerCommandConfig(
        debug=False,
        command="server",
        input_path=str(project_dir),
        output_path=str(tmp_path / "output"),
        config=None,
        reload=False,
        host="127.0.0.1",
        port=8001,
    )
    project_config_: ProjectConfig = ProjectConfig.default_config()
    project_config_.integrate_server_config(server_config)
    return project_config_


def test_edit_via_ui_reanalyzes_immediately_without_restart(
    project_config: ProjectConfig,
):
    client = TestClient(create_app(project_config=project_config))

    # Sanity check: the requirement starts well-formed, so no issue is shown.
    document_page = client.get("/UID/REQ-1", follow_redirects=True)
    assert document_page.status_code == 200
    assert CANNOT_CONVERT_MESSAGE not in document_page.text

    # Edit STATEMENT via the same UI save path a student's browser uses —
    # no server restart, no touching the .sdoc file from outside.
    response = client.post(
        "/actions/table/update_node_field_multiline",
        data={
            "node_mid": "req-1-mid",
            "field_name": "STATEMENT",
            "field_value": UNCONVERTIBLE_STATEMENT,
        },
    )
    assert response.status_code == 200, response.text

    # The warning must show up right away, in this same running server.
    document_page = client.get("/UID/REQ-1", follow_redirects=True)
    assert CANNOT_CONVERT_MESSAGE in document_page.text
    # Actionable, not just "invalid": names the expected shape.
    assert "ЕСЛИ" in document_page.text

    # A second, identical save must not duplicate the warning (reset()
    # before each re-run — see ValidationIndex.reset()).
    response = client.post(
        "/actions/table/update_node_field_multiline",
        data={
            "node_mid": "req-1-mid",
            "field_name": "STATEMENT",
            "field_value": UNCONVERTIBLE_STATEMENT,
        },
    )
    assert response.status_code == 200, response.text
    document_page = client.get("/UID/REQ-1", follow_redirects=True)
    assert document_page.text.count(CANNOT_CONVERT_MESSAGE) == 1

    # Fixing the text must clear the warning immediately too — a check
    # that only ever adds issues would leave this one stale forever.
    response = client.post(
        "/actions/table/update_node_field_multiline",
        data={
            "node_mid": "req-1-mid",
            "field_name": "STATEMENT",
            "field_value": (
                "ЕСЛИ (motor_Speed > 10) ТО робот должен "
                "уменьшить motor_Speed на 5"
            ),
        },
    )
    assert response.status_code == 200, response.text
    document_page = client.get("/UID/REQ-1", follow_redirects=True)
    assert CANNOT_CONVERT_MESSAGE not in document_page.text
