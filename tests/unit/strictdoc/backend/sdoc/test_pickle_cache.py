import os
from unittest import mock

from strictdoc.backend.sdoc.pickle_cache import PickleCache
from strictdoc.core.project_config import ProjectConfig
from strictdoc.helpers.md5 import get_file_md5


def create_project_config(tmp_path) -> ProjectConfig:
    project_config = ProjectConfig.default_config()
    project_config.output_dir = str(tmp_path / "output")
    project_config.dir_for_sdoc_cache = str(tmp_path / "cache")
    return project_config


def test_01_cache_miss_when_no_cache_file_exists(tmp_path):
    project_config = create_project_config(tmp_path)
    input_file = tmp_path / "document.sdoc"
    input_file.write_text("content")

    assert (
        PickleCache.read_from_cache(str(input_file), project_config, "sdoc")
        is None
    )


def test_02_cache_hit_reuses_content_and_does_not_rehash_when_unchanged(
    tmp_path,
):
    project_config = create_project_config(tmp_path)
    input_file = tmp_path / "document.sdoc"
    input_file.write_text("content")

    PickleCache.save_to_cache(
        "parsed-content", str(input_file), project_config, "sdoc"
    )

    with mock.patch(
        "strictdoc.backend.sdoc.pickle_cache.get_file_md5"
    ) as get_file_md5_mock:
        result = PickleCache.read_from_cache(
            str(input_file), project_config, "sdoc"
        )

    assert result == "parsed-content"
    # The fast (stat-only) path must not need to hash the file's content.
    get_file_md5_mock.assert_not_called()


def test_03_cache_miss_when_file_content_changes(tmp_path):
    project_config = create_project_config(tmp_path)
    input_file = tmp_path / "document.sdoc"
    input_file.write_text("content")

    PickleCache.save_to_cache(
        "parsed-content", str(input_file), project_config, "sdoc"
    )

    input_file.write_text("different content, different size")

    assert (
        PickleCache.read_from_cache(str(input_file), project_config, "sdoc")
        is None
    )


def test_04_cache_hit_via_content_hash_when_mtime_changes_but_content_does_not(
    tmp_path,
):
    project_config = create_project_config(tmp_path)
    input_file = tmp_path / "document.sdoc"
    input_file.write_text("content")

    PickleCache.save_to_cache(
        "parsed-content", str(input_file), project_config, "sdoc"
    )

    # Simulate a git checkout: mtime changes, content and size do not.
    future_time = os.stat(input_file).st_mtime + 3600
    os.utime(input_file, (future_time, future_time))

    with mock.patch(
        "strictdoc.backend.sdoc.pickle_cache.get_file_md5",
        wraps=get_file_md5,
    ) as get_file_md5_mock:
        result = PickleCache.read_from_cache(
            str(input_file), project_config, "sdoc"
        )
        assert result == "parsed-content"
        # The mtime mismatch forces exactly one content-hash fallback check.
        get_file_md5_mock.assert_called_once()

    # The entry is healed after the content-hash fallback, so a subsequent
    # read hits the fast (stat-only) path again.
    with mock.patch(
        "strictdoc.backend.sdoc.pickle_cache.get_file_md5"
    ) as get_file_md5_mock:
        result = PickleCache.read_from_cache(
            str(input_file), project_config, "sdoc"
        )
        assert result == "parsed-content"
        get_file_md5_mock.assert_not_called()
