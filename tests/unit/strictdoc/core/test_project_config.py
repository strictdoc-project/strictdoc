from strictdoc import environment
from strictdoc.core.project_config import (
    ProjectConfigLoader,
    ProjectFeature,
    parse_relation_tuple,
)


def test_01_project_title():
    config_string = """
[project]
title = "StrictDoc Documentation"
"""
    project_config = ProjectConfigLoader.load_from_string(
        toml_string=config_string, environment=environment
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
        toml_string=config_string, environment=environment
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


def test_parse_relation_tuple():
    assert parse_relation_tuple("Parent") == ("Parent", None)

    assert parse_relation_tuple("Parent[Refines]") == ("Parent", "Refines")

    assert parse_relation_tuple("Parent[REQUIREMENT_FOR]") == (
        "Parent",
        "REQUIREMENT_FOR",
    )

    assert parse_relation_tuple("Parent[Foo bar]") == ("Parent", "Foo bar")

    assert parse_relation_tuple("File") == ("File", None)

    assert parse_relation_tuple("Foobar") is None

    assert parse_relation_tuple("Parent[REQUIREMENT_FOR") is None

    assert (
        parse_relation_tuple(
            "Parent[Very long Foobar Very long Foobar Very long Foobar Very long Foobar]"
        )
        is None
    )
