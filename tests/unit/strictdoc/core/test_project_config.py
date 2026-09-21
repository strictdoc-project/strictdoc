import os
import tempfile

import pytest

from strictdoc.backend.sdoc.sdoc_format import SDocFormat
from strictdoc.core.project_config import (
    ProjectConfig,
    ProjectConfigLoader,
    ProjectFeature,
)
from strictdoc.features.html2pdf.html2pdf_format import HTML2PDFFormat


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


def test_11__project_features__all_features_expands_via_constructor():
    project_config = ProjectConfig(project_features=["ALL_FEATURES", "SEARCH"])
    assert project_config.project_features == ProjectFeature.all()


def test_12__project_features__all_features_expands_when_assigned_after_construction(
    tmp_path,
):
    """
    An extending create_config() commonly assigns project_features to an
    already-constructed ProjectConfig (`config.project_features = [...]`),
    bypassing the ALL_FEATURES expansion that __init__ would otherwise do.
    validate_and_finalize(), which every ProjectConfigLoader path calls,
    must still expand it.
    """
    config_path = tmp_path / "strictdoc_config.py"
    config_path.write_text(
        """\
from strictdoc.core.project_config import ProjectConfig

def create_config() -> ProjectConfig:
    config = ProjectConfig()
    config.project_features = ["ALL_FEATURES", "SEARCH"]
    return config
""",
        encoding="utf8",
    )

    project_config = ProjectConfigLoader.load(str(tmp_path))

    assert project_config.project_features == ProjectFeature.all()


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


def test_34_exclude_paths_from_gitignore_tracked_separately(tmp_path):
    (tmp_path / ".gitignore").write_text(
        "output/\n# a comment\n\nbuild/\n",
        encoding="utf8",
    )
    project_config = ProjectConfig(exclude_doc_paths=["/docs/drafts/"])
    project_config.input_paths = [str(tmp_path)]
    project_config.validate_and_finalize()

    assert project_config.exclude_paths_from_gitignore == [
        "/.git/",
        "output/",
        "build/",
    ]
    # The explicitly configured exclude is not mistaken for a gitignore one.
    assert "/docs/drafts/" not in project_config.exclude_paths_from_gitignore
    # Both still end up in the merged list used for actual filtering.
    assert project_config.exclude_doc_paths == [
        "/docs/drafts/",
        "/.git/",
        "output/",
        "build/",
    ]


#
# Editable document extensions.
#
def test_40_editable_document_extensions_only_sdoc():
    # SDocFormat is the base/always-available format, used here to test
    # the get_editable_document_extensions() mechanism itself (iterate
    # formats -> keep supports_edit() ones -> collect
    # supported_extensions()), independent of which formats a real
    # project happens to have configured.
    project_config = ProjectConfig(formats=[SDocFormat()])
    assert project_config.get_editable_document_extensions() == [".sdoc"]


def test_41_editable_document_extensions_excludes_non_editable_format():
    # HTML2PDFFormat is used (instead of a fake/stub Format) because it is
    # a real, permanently non-editable format: PDF output is exported
    # only, never edited through the UI, and supports_edit() is
    # guaranteed to stay False. This keeps the test meaningful without
    # inventing a throwaway Format subclass.
    project_config = ProjectConfig(formats=[SDocFormat(), HTML2PDFFormat()])
    extensions = project_config.get_editable_document_extensions()
    assert extensions == [".sdoc"]
    assert ".pdf" not in extensions


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
        config, _ = ProjectConfigLoader.load_from_path_or_get_default(
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
        config, _ = ProjectConfigLoader.load_from_path_or_get_default(
            path_to_config=path
        )
        assert config.project_title == "NonCanonical"
    finally:
        os.unlink(path)


def test_80_lazy_document_loading_threshold_from_config(tmp_path):
    path_to_config = tmp_path / "strictdoc_config.py"
    path_to_config.write_text(
        """\
from strictdoc.core.project_config import ProjectConfig


def create_config():
    return ProjectConfig(lazy_document_loading_threshold=50)
"""
    )
    project_config, _ = ProjectConfigLoader.load_from_path_or_get_default(
        path_to_config=str(path_to_config)
    )
    assert project_config.lazy_document_loading_threshold == 50


def test_81_lazy_document_loading_threshold_default_when_absent(tmp_path):
    path_to_config = tmp_path / "strictdoc_config.py"
    path_to_config.write_text(
        """\
from strictdoc.core.project_config import ProjectConfig


def create_config():
    return ProjectConfig(project_title="No threshold set")
"""
    )
    project_config, _ = ProjectConfigLoader.load_from_path_or_get_default(
        path_to_config=str(path_to_config)
    )
    assert project_config.lazy_document_loading_threshold == 200


def test_82_lazy_document_loading_threshold_zero_disables():
    project_config = ProjectConfig(lazy_document_loading_threshold=0)
    assert project_config.lazy_document_loading_threshold == 0


def test_83_lazy_document_loading_threshold_negative_rejected():
    with pytest.raises(AssertionError):
        _ = ProjectConfig(lazy_document_loading_threshold=-1)
