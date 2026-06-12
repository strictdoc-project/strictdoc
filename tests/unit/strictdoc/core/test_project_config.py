import os
import tempfile

import pytest

from strictdoc.core.project_config import (
    ProjectConfig,
    ProjectConfigLoader,
    ProjectFeature,
)


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


#
# Config loading from Python files.
#
def test_70_load_python_config_with_canonical_filename():
    config_content = """\
from strictdoc.core.project_config import ProjectConfig

def create_config():
    return ProjectConfig(project_title="Canonical")
"""
    with tempfile.NamedTemporaryFile(
        suffix="_strictdoc_config.py", mode="w", delete=False
    ) as f:
        f.write(config_content)
        path = f.name
    try:
        config = ProjectConfigLoader.load_from_path_or_get_default(
            path_to_config=path
        )
        assert config.project_title == "Canonical"
    finally:
        os.unlink(path)


def test_71_load_python_config_with_non_canonical_filename():
    config_content = """\
from strictdoc.core.project_config import ProjectConfig

def create_config():
    return ProjectConfig(project_title="NonCanonical")
"""
    with tempfile.NamedTemporaryFile(
        suffix="_my_custom_config.py", mode="w", delete=False
    ) as f:
        f.write(config_content)
        path = f.name
    try:
        config = ProjectConfigLoader.load_from_path_or_get_default(
            path_to_config=path
        )
        assert config.project_title == "NonCanonical"
    finally:
        os.unlink(path)


def test_80_chunked_documents_threshold_from_config(tmp_path):
    path_to_config = tmp_path / "strictdoc_config.py"
    path_to_config.write_text(
        """\
from strictdoc.core.project_config import ProjectConfig


def create_config():
    return ProjectConfig(chunked_documents_threshold=50)
"""
    )
    project_config = ProjectConfigLoader.load_from_path_or_get_default(
        path_to_config=str(path_to_config)
    )
    assert project_config.chunked_documents_threshold == 50


def test_81_chunked_documents_threshold_default_when_absent(tmp_path):
    path_to_config = tmp_path / "strictdoc_config.py"
    path_to_config.write_text(
        """\
from strictdoc.core.project_config import ProjectConfig


def create_config():
    return ProjectConfig(project_title="No threshold set")
"""
    )
    project_config = ProjectConfigLoader.load_from_path_or_get_default(
        path_to_config=str(path_to_config)
    )
    assert project_config.chunked_documents_threshold == 200


def test_82_chunked_documents_threshold_zero_disables():
    project_config = ProjectConfig(chunked_documents_threshold=0)
    assert project_config.chunked_documents_threshold == 0


def test_83_chunked_documents_threshold_negative_rejected():
    with pytest.raises(AssertionError):
        _ = ProjectConfig(chunked_documents_threshold=-1)
