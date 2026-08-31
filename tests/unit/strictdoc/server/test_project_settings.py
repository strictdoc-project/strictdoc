from pathlib import Path
from typing import Dict

from strictdoc.core.project_config import ProjectConfig, ProjectConfigLoader
from strictdoc.export.html.html_templates import NormalHTMLTemplates
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.features.project_configuration.generator import (
    ProjectConfigurationHTMLGenerator,
)
from strictdoc.features.project_configuration.view_object import (
    ProjectConfigurationViewObject,
)
from strictdoc.server.project_settings import (
    ProjectSettingsManager,
    SettingValue,
)


def create_project_config(config_path: Path) -> ProjectConfig:
    project_config = ProjectConfig(
        project_features=["SEARCH"],
        _config_path=str(config_path),
    )
    project_config.input_paths = [str(config_path.parent)]
    project_config.source_root_path = str(config_path.parent)
    return project_config


def editable_values(manager: ProjectSettingsManager) -> Dict[str, SettingValue]:
    return {
        state_.definition.name: state_.value
        for state_ in manager.inspect().settings
        if state_.editable
    }


def test_inspect_exposes_only_project_features(tmp_path: Path) -> None:
    config_path = tmp_path / "strictdoc_config.py"
    config_path.write_text(
        """\
from strictdoc.core.project_config import ProjectConfig

def create_config() -> ProjectConfig:
    return ProjectConfig(
        project_features=["SEARCH"],
    )
""",
        encoding="utf8",
    )

    project_config = create_project_config(config_path)
    inspection = ProjectSettingsManager(project_config).inspect()

    assert [state_.definition.name for state_ in inspection.settings] == [
        "project_features",
    ]
    assert all(state_.editable for state_ in inspection.settings)

    view_object = ProjectConfigurationViewObject(
        project_config=project_config,
        link_renderer=LinkRenderer(root_path="", static_path="."),
    )
    assert view_object.project_settings_unavailable_message() is None


def test_save_updates_literals_and_preserves_other_source(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "strictdoc_config.py"
    config_path.write_text(
        """\
from strictdoc.core.project_config import ProjectConfig

# This comment must remain.
def create_config() -> ProjectConfig:
    return ProjectConfig(
        project_title="Example",
        project_features=["SEARCH"],
    )
""",
        encoding="utf8",
    )
    manager = ProjectSettingsManager(create_project_config(config_path))
    values = editable_values(manager)
    values["project_features"] = ["SEARCH", "DIFF"]

    result = manager.save(values)

    assert result.changed is True
    assert result.saved_version_path is not None
    source = config_path.read_text(encoding="utf8")
    assert "# This comment must remain." in source
    assert 'project_title="Example"' in source
    loaded_config = ProjectConfigLoader.load(str(tmp_path))
    assert loaded_config.project_features == ["SEARCH", "DIFF"]


def test_save_extending_config_assignments(tmp_path: Path) -> None:
    base_config_path = tmp_path / "base_config.py"
    base_config_path.write_text(
        """\
from strictdoc.core.project_config import ProjectConfig

def create_config() -> ProjectConfig:
    return ProjectConfig(project_title="Base project")
""",
        encoding="utf8",
    )
    config_path = tmp_path / "strictdoc_config.py"
    config_path.write_text(
        """\
from base_config import create_config as create_base_config

def create_config():
    config = create_base_config()
    config.project_features = ["SEARCH"]
    return config
""",
        encoding="utf8",
    )
    project_config = ProjectConfigLoader.load_from_python(
        config_py_path=str(config_path)
    )
    project_config.config_path = str(config_path)
    project_config.input_paths = [str(tmp_path)]
    project_config.source_root_path = str(tmp_path)
    manager = ProjectSettingsManager(project_config)
    values = editable_values(manager)
    values["project_features"] = ["SEARCH", "DIFF"]

    manager.save(values)

    source = config_path.read_text(encoding="utf8")
    assert "config.project_features = ['SEARCH', 'DIFF']" in source
    assert (
        "project_features"
        not in base_config_path.read_text(encoding="utf8").split(
            "return ProjectConfig(", 1
        )[0]
    )


def test_project_feature_all_is_replaced_with_a_literal(tmp_path: Path) -> None:
    config_path = tmp_path / "strictdoc_config.py"
    config_path.write_text(
        """\
from strictdoc.core.project_config import ProjectConfig, ProjectFeature

def create_config() -> ProjectConfig:
    config = ProjectConfig()
    config.project_features = ProjectFeature.all()
    return config
""",
        encoding="utf8",
    )
    project_config = ProjectConfigLoader.load_from_python(
        config_py_path=str(config_path)
    )
    project_config.config_path = str(config_path)
    project_config.input_paths = [str(tmp_path)]
    project_config.source_root_path = str(tmp_path)
    manager = ProjectSettingsManager(project_config)
    values = editable_values(manager)
    assert values["project_features"] == ["ALL_FEATURES"]
    values["project_features"] = ["SEARCH", "DIFF"]

    manager.save(values)

    assert (
        "config.project_features = ['SEARCH', 'DIFF']"
        in config_path.read_text(encoding="utf8")
    )


def test_save_creates_missing_config_with_changed_values(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "strictdoc_config.py"
    manager = ProjectSettingsManager(create_project_config(config_path))
    values = editable_values(manager)
    values["project_features"] = ["SEARCH", "DIFF"]

    result = manager.save(values)

    assert result.changed is True
    assert result.saved_version_path is None
    source = config_path.read_text(encoding="utf8")
    assert "project_features=['SEARCH', 'DIFF']" in source


def test_save_rotates_saved_versions(tmp_path: Path) -> None:
    config_path = tmp_path / "strictdoc_config.py"
    config_path.write_text(
        """\
from strictdoc.core.project_config import ProjectConfig

def create_config() -> ProjectConfig:
    return ProjectConfig(project_features=["SEARCH"])
""",
        encoding="utf8",
    )
    manager = ProjectSettingsManager(create_project_config(config_path))

    for iteration_ in range(2, 9):
        values = editable_values(manager)
        values["project_features"] = (
            ["SEARCH", "DIFF"] if iteration_ % 2 == 0 else ["SEARCH"]
        )
        manager.save(values)

    assert len(list(tmp_path.glob("strictdoc_config.py.saved.*"))) == 5


def test_save_does_nothing_for_unchanged_values(tmp_path: Path) -> None:
    config_path = tmp_path / "strictdoc_config.py"
    config_path.write_text(
        """\
from strictdoc.core.project_config import ProjectConfig

def create_config() -> ProjectConfig:
    return ProjectConfig()
""",
        encoding="utf8",
    )
    manager = ProjectSettingsManager(create_project_config(config_path))

    result = manager.save(editable_values(manager))

    assert result.changed is False
    assert list(tmp_path.glob("strictdoc_config.py.saved.*")) == []


def test_invalid_feature_does_not_change_file(tmp_path: Path) -> None:
    config_path = tmp_path / "strictdoc_config.py"
    config_path.write_text(
        """\
from strictdoc.core.project_config import ProjectConfig

def create_config() -> ProjectConfig:
    return ProjectConfig(project_features=["SEARCH"])
""",
        encoding="utf8",
    )
    original_source = config_path.read_text(encoding="utf8")
    manager = ProjectSettingsManager(create_project_config(config_path))
    values = editable_values(manager)
    values["project_features"] = ["NOT_A_REAL_FEATURE"]

    try:
        manager.save(values)
    except ValueError as exception_:
        assert "Unknown project features" in str(exception_)
    else:
        raise AssertionError("An unknown feature was accepted.")

    assert config_path.read_text(encoding="utf8") == original_source
    assert list(tmp_path.glob("strictdoc_config.py.saved.*")) == []


def test_static_project_configuration_has_no_edit_action(
    tmp_path: Path,
) -> None:
    project_config = ProjectConfig(project_title="Static project")
    project_config.input_paths = [str(tmp_path)]
    project_config.source_root_path = str(tmp_path)

    output = ProjectConfigurationHTMLGenerator.export(
        project_config,
        html_templates=NormalHTMLTemplates(),
    )

    assert 'data-testid="project-configuration-page"' in output
    assert 'data-testid="project-tree-configuration"' in output
    assert 'data-testid="project-configuration-editable-values"' in output
    assert "200 by default" in output
    assert "project_tree.css" in output
    assert "path_reveal.js" in output
    assert "data-js-path-reveal-control" in output
    assert 'data-testid="project-configuration-edit"' not in output


def test_computed_setting_is_read_only(tmp_path: Path) -> None:
    config_path = tmp_path / "strictdoc_config.py"
    config_path.write_text(
        """\
from strictdoc.core.project_config import ProjectConfig

FEATURES = ["SEARCH"]

def create_config() -> ProjectConfig:
    return ProjectConfig(
        project_features=FEATURES,
    )
""",
        encoding="utf8",
    )

    project_config = create_project_config(config_path)
    states = {
        state_.definition.name: state_
        for state_ in ProjectSettingsManager(project_config).inspect().settings
    }

    assert states["project_features"].editable is False

    view_object = ProjectConfigurationViewObject(
        project_config=project_config,
        link_renderer=LinkRenderer(root_path="", static_path="."),
    )
    assert (
        view_object.project_settings_unavailable_message()
        == "Edit this setting manually in the settings file."
    )


def test_write_error_keeps_original_file(
    tmp_path: Path,
    monkeypatch,
) -> None:
    config_path = tmp_path / "strictdoc_config.py"
    config_path.write_text(
        """\
from strictdoc.core.project_config import ProjectConfig

def create_config() -> ProjectConfig:
    return ProjectConfig(project_features=["SEARCH"])
""",
        encoding="utf8",
    )
    original_source = config_path.read_text(encoding="utf8")
    manager = ProjectSettingsManager(create_project_config(config_path))
    values = editable_values(manager)
    values["project_features"] = ["SEARCH", "DIFF"]

    def fail_replace(_source: str, _destination: str) -> None:
        raise OSError("forced write failure")

    monkeypatch.setattr(
        "strictdoc.server.project_settings.os.replace", fail_replace
    )

    try:
        manager.save(values)
    except OSError as exception_:
        assert "forced write failure" in str(exception_)
    else:
        raise AssertionError("The forced write error was not reported.")

    assert config_path.read_text(encoding="utf8") == original_source
