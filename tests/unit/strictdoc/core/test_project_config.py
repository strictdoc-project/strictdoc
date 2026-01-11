import pytest

from strictdoc.core.project_config import ProjectConfig, ProjectFeature


def test_01_default_config():
    project_config = ProjectConfig.default_config()
    assert project_config.include_source_paths == []


#
# Project features.
#
def test_10__project_features__accepts_strings_or_enums():
    project_config = ProjectConfig(
        project_features=[
            ProjectFeature.DIFF,
            ProjectFeature.HTML2PDF.value,
            "REQIF",
        ]
    )
    assert project_config.is_activated_diff()
    assert project_config.is_activated_html2pdf()
    assert project_config.is_activated_reqif()


def test_30_include_doc_paths_bad_mask():
    with pytest.raises(ValueError):
        _ = ProjectConfig(include_doc_paths=[" "])


def test_31_exclude_doc_paths_bad_mask():
    with pytest.raises(ValueError):
        _ = ProjectConfig(exclude_doc_paths=[" "])


def test_32_include_source_paths_bad_mask():
    with pytest.raises(ValueError):
        _ = ProjectConfig(include_source_paths=[" "])


def test_33_exclude_source_paths_bad_mask():
    with pytest.raises(ValueError):
        _ = ProjectConfig(exclude_source_paths=[" "])


def test_60_valid_host_and_port():
    project_config = ProjectConfig(
        server_host="localhost123",
        server_port=5555,
    )
    assert project_config.server_host == "localhost123"
    assert project_config.server_port == 5555


def test_61_validate_invalid_host():
    with pytest.raises(AssertionError):
        _ = ProjectConfig(server_host="bad$host")


def test_62_validate_invalid_port():
    with pytest.raises(AssertionError):
        _ = ProjectConfig(server_port=1000000)
