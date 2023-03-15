from strictdoc.core.project_config import ProjectConfigLoader, ProjectFeature


def test_01_project_title():
    config_string = """
[project]
title = "StrictDoc Documentation"
"""
    project_config = ProjectConfigLoader.load_from_string(
        toml_string=config_string
    )
    assert project_config.project_title == "StrictDoc Documentation"


def test_02_features():
    config_string = """
[project]
title = "StrictDoc Documentation"
features = [
  # Stable features.
  "TABLE_SCREEN",
  "TRACEABILITY_SCREEN",
]
"""
    project_config = ProjectConfigLoader.load_from_string(
        toml_string=config_string
    )
    assert project_config.project_title == "StrictDoc Documentation"
    assert project_config.project_features == [
        ProjectFeature.TABLE_SCREEN,
        ProjectFeature.TRACEABILITY_SCREEN,
    ]
    assert project_config.is_feature_activated(
        ProjectFeature.TABLE_SCREEN,
    )
    assert project_config.is_feature_activated(
        ProjectFeature.TRACEABILITY_SCREEN,
    )
