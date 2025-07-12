import pytest

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


def test_80_validate_include_doc_paths_mask():
    config_string = """
[project]
title = "StrictDoc Documentation"

include_doc_paths = [
  "***"
]
"""

    with pytest.raises(SyntaxError) as exc_info_:
        _ = ProjectConfigLoader.load_from_string(
            toml_string=config_string, environment=environment
        )

    exception: SyntaxError = exc_info_.value
    assert exception.args[0] == (
        "strictdoc.toml: "
        "'include_doc_paths': Invalid wildcard: '***'. Provided string: '***'."
    )


def test_81_validate_exclude_doc_paths_mask():
    config_string = """
[project]
title = "StrictDoc Documentation"

exclude_doc_paths = [
  "***"
]
"""

    with pytest.raises(SyntaxError) as exc_info_:
        _ = ProjectConfigLoader.load_from_string(
            toml_string=config_string, environment=environment
        )

    exception: SyntaxError = exc_info_.value
    assert exception.args[0] == (
        "strictdoc.toml: "
        "'exclude_doc_paths': Invalid wildcard: '***'. Provided string: '***'."
    )


def test_82_validate_include_source_paths_mask():
    config_string = """
[project]
title = "StrictDoc Documentation"

include_source_paths = [
  "***"
]
"""

    with pytest.raises(SyntaxError) as exc_info_:
        _ = ProjectConfigLoader.load_from_string(
            toml_string=config_string, environment=environment
        )

    exception: SyntaxError = exc_info_.value
    assert exception.args[0] == (
        "strictdoc.toml: "
        "'include_source_paths': Invalid wildcard: '***'. Provided string: '***'."
    )


def test_83_validate_exclude_source_paths_mask():
    config_string = """
[project]
title = "StrictDoc Documentation"

exclude_source_paths = [
  "***"
]
"""

    with pytest.raises(SyntaxError) as exc_info_:
        _ = ProjectConfigLoader.load_from_string(
            toml_string=config_string, environment=environment
        )

    exception: SyntaxError = exc_info_.value
    assert exception.args[0] == (
        "strictdoc.toml: "
        "'exclude_source_paths': Invalid wildcard: '***'. Provided string: '***'."
    )


def test_84_validate_bad_host():
    config_string = """
[project]
title = "StrictDoc Documentation"

[server]
host = "BAD$$$HOST"
"""

    with pytest.raises(ValueError) as exc_info_:
        _ = ProjectConfigLoader.load_from_string(
            toml_string=config_string, environment=environment
        )

    exception: ValueError = exc_info_.value
    assert exception.args[0] == (
        "strictdoc.toml: 'host': invalid host: BAD$$$HOST'."
    )


def test_85_validate_bad_port():
    config_string = """
[project]
title = "StrictDoc Documentation"

[server]
port = 1234567
"""

    with pytest.raises(ValueError) as exc_info_:
        _ = ProjectConfigLoader.load_from_string(
            toml_string=config_string, environment=environment
        )

    exception: ValueError = exc_info_.value
    assert exception.args[0] == (
        "strictdoc.toml: 'port': invalid port: 1234567'."
    )


def test_86_validate_non_existing_chrome_driver():
    config_string = """
[project]
title = "StrictDoc Documentation"

chromedriver = "DOES_NOT_EXIST"
"""

    with pytest.raises(ValueError) as exc_info_:
        _ = ProjectConfigLoader.load_from_string(
            toml_string=config_string, environment=environment
        )

    exception: ValueError = exc_info_.value
    assert exception.args[0] == (
        "strictdoc.toml: 'chromedriver': not found at path: DOES_NOT_EXIST."
    )


def test_87_validate_non_existing_html2pdf_template():
    config_string = """
[project]
title = "StrictDoc Documentation"

html2pdf_template = "DOES_NOT_EXIST"
"""

    with pytest.raises(ValueError) as exc_info_:
        _ = ProjectConfigLoader.load_from_string(
            toml_string=config_string, environment=environment
        )

    exception: ValueError = exc_info_.value
    assert exception.args[0] == (
        "strictdoc.toml: 'html2pdf_template': "
        "invalid path to a template file: DOES_NOT_EXIST."
    )
