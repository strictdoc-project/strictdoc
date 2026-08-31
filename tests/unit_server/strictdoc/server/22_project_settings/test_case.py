from pathlib import Path

from fastapi.testclient import TestClient

from strictdoc.commands.server_config import ServerCommandConfig
from strictdoc.core.project_config import ProjectConfigLoader
from strictdoc.core.traceability_index_builder import TraceabilityIndexBuilder
from strictdoc.server.app import create_app
from strictdoc.server.project_settings import ProjectSettingsManager


def create_settings_form_data(
    *,
    project_features: list[str],
) -> dict[str, object]:
    return {
        "project_features": project_features,
    }


def create_test_project(tmp_path: Path):
    (tmp_path / "document.sdoc").write_text(
        "[DOCUMENT]\nTITLE: Test document\n",
        encoding="utf8",
    )
    config_path = tmp_path / "strictdoc_config.py"
    config_path.write_text(
        """\
from strictdoc.core.project_config import ProjectConfig

def create_config() -> ProjectConfig:
    return ProjectConfig(
        project_title="Test project",
        project_features=["SEARCH"],
    )
""",
        encoding="utf8",
    )
    server_config = ServerCommandConfig(
        debug=False,
        command="server",
        input_path=str(tmp_path),
        output_path=str(tmp_path / "output"),
        config=str(config_path),
        reload=False,
        host=None,
        port=None,
    )
    return config_path, ProjectConfigLoader.load_using_server_config(
        server_config
    )


def test_project_configuration_page_and_modal(tmp_path: Path) -> None:
    config_path, project_config = create_test_project(tmp_path)

    with TestClient(create_app(project_config=project_config)) as client:
        project_response = client.get("/project_configuration.html")
        assert project_response.status_code == 200
        assert (
            'data-testid="project-configuration-page"' in project_response.text
        )
        assert (
            'data-testid="project-configuration-edit"' in project_response.text
        )
        assert (
            'data-testid="project-tree-configuration"' in project_response.text
        )
        assert (
            'data-testid="project-configuration-editable-values"'
            in project_response.text
        )
        assert str(config_path) in project_response.text
        assert "project_tree.css" in project_response.text
        assert "path_reveal.js" in project_response.text
        assert "HTML2PDF strict mode" in project_response.text
        assert "ReqIF import markup" in project_response.text
        assert "200 by default" in project_response.text

        index_response = client.get("/")
        assert (
            'data-testid="project-tree-configuration"'
            not in index_response.text
        )
        assert 'data-testid="project-configuration-link"' in index_response.text

        settings_response = client.get("/actions/project_settings")
        assert settings_response.status_code == 200
        assert 'data-testid="project-settings-form"' in settings_response.text
        assert (
            'data-testid="project-settings-reset-all"'
            not in settings_response.text
        )
        assert (
            'data-testid="project-settings-control-all-features"'
            in settings_response.text
        )


def test_project_settings_are_saved_and_reloaded(tmp_path: Path) -> None:
    config_path, project_config = create_test_project(tmp_path)

    with TestClient(create_app(project_config=project_config)) as client:
        invalid_response = client.post(
            "/actions/project_settings",
            data=create_settings_form_data(
                project_features=["NOT_A_REAL_FEATURE"]
            ),
        )
        assert invalid_response.status_code == 200
        assert 'data-testid="project-settings-error"' in invalid_response.text

        save_response = client.post(
            "/actions/project_settings",
            data=create_settings_form_data(project_features=["SEARCH", "DIFF"]),
        )
        assert save_response.status_code == 200
        assert "Settings saved" in save_response.text
        assert project_config.project_features == ["SEARCH", "DIFF"]

    saved_config = ProjectConfigLoader.load_from_python(
        config_py_path=str(config_path)
    )
    assert saved_config.project_features == ["SEARCH", "DIFF"]
    assert len(list(tmp_path.glob("strictdoc_config.py.saved.*"))) == 1


def test_external_config_is_the_only_file_changed(tmp_path: Path) -> None:
    project_path = tmp_path / "project"
    project_path.mkdir()
    (project_path / "document.sdoc").write_text(
        "[DOCUMENT]\nTITLE: Test document\n",
        encoding="utf8",
    )
    base_config_path = project_path / "strictdoc_config.py"
    base_source = """\
from strictdoc.core.project_config import ProjectConfig

def create_config() -> ProjectConfig:
    return ProjectConfig(project_title="Base config")
"""
    base_config_path.write_text(base_source, encoding="utf8")
    external_config_path = tmp_path / "custom.py"
    external_config_path.write_text(
        """\
from strictdoc.core.project_config import ProjectConfig

def create_config() -> ProjectConfig:
    return ProjectConfig(project_features=["SEARCH"])
""",
        encoding="utf8",
    )
    server_config = ServerCommandConfig(
        debug=False,
        command="server",
        input_path=str(project_path),
        output_path=str(tmp_path / "output"),
        config=str(external_config_path),
        reload=False,
        host=None,
        port=None,
    )
    project_config = ProjectConfigLoader.load_using_server_config(server_config)

    with TestClient(create_app(project_config=project_config)) as client:
        response = client.post(
            "/actions/project_settings",
            data=create_settings_form_data(project_features=["SEARCH", "DIFF"]),
        )

    assert response.status_code == 200
    assert base_config_path.read_text(encoding="utf8") == base_source
    assert (
        "project_features=['SEARCH', 'DIFF']"
        in external_config_path.read_text(encoding="utf8")
    )


def test_reload_failure_keeps_active_state_and_reports_error(
    tmp_path: Path,
    monkeypatch,
) -> None:
    config_path, project_config = create_test_project(tmp_path)
    application = create_app(project_config=project_config)

    def fail_rebuild(**_kwargs):
        raise RuntimeError("forced settings reload failure")

    monkeypatch.setattr(TraceabilityIndexBuilder, "create", fail_rebuild)

    with TestClient(application) as client:
        with client.websocket_connect("/ws/1") as websocket:
            response = client.post(
                "/actions/project_settings",
                data=create_settings_form_data(
                    project_features=["SEARCH", "DIFF"]
                ),
            )
            websocket_message = websocket.receive_text()

    assert response.status_code == 200
    assert websocket_message.startswith("project-settings:error:")
    assert project_config.project_features == ["SEARCH"]
    assert "project_features=['SEARCH', 'DIFF']" in config_path.read_text(
        encoding="utf8"
    )


def test_write_error_keeps_modal_values(
    tmp_path: Path,
    monkeypatch,
) -> None:
    config_path, project_config = create_test_project(tmp_path)
    original_source = config_path.read_text(encoding="utf8")

    def fail_save(
        _manager: ProjectSettingsManager,
        _candidate_source: str,
    ) -> None:
        raise OSError("forced write failure")

    monkeypatch.setattr(ProjectSettingsManager, "_save_candidate", fail_save)

    with TestClient(create_app(project_config=project_config)) as client:
        response = client.post(
            "/actions/project_settings",
            data=create_settings_form_data(project_features=["SEARCH", "DIFF"]),
        )

    assert response.status_code == 200
    assert 'data-testid="project-settings-error"' in response.text
    assert (
        'data-testid="project-settings-feature-DIFF" checked' in response.text
    )
    assert config_path.read_text(encoding="utf8") == original_source
