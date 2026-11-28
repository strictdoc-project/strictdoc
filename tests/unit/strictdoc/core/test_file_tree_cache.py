"""
@relation(SDOC-SRS-142, scope=file)
"""

import glob
import os
import pickle
import time
from pathlib import Path
from typing import Any, List, Optional

import pytest

from strictdoc.core.file_system import file_tree
from strictdoc.core.file_system.file_tree import FileFinder

OLD_SECONDS = 60


def find_files(
    root: Path,
    *,
    include_paths: Optional[List[str]] = None,
    exclude_paths: Optional[List[str]] = None,
    cached: bool,
) -> List[str]:
    arguments: Any = {
        "root_path": str(root / "project"),
        "ignored_dirs": [str(root / "project" / "output_dir")],
        "extensions": None,
        "include_paths": include_paths or [],
        "exclude_paths": exclude_paths or [],
    }
    if cached:
        arguments["path_to_cache_dir"] = str(root / "cache")
    found_tree = FileFinder.find_files_with_extensions(**arguments)
    return [
        file_.rel_path.relative_path for _, file_, _ in found_tree.iterate()
    ]


def assert_same_as_without_cache(root: Path, **kwargs: Any) -> List[str]:
    found_files = find_files(root, cached=True, **kwargs)
    assert found_files == find_files(root, cached=False, **kwargs)
    return found_files


def create_files(root: Path, *paths: str) -> None:
    for path_ in paths:
        path = root / "project" / path_
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"content of {path_}\n")


def make_folders_old(root: Path) -> None:
    """
    Move the mtimes of all folders out of the window in which the cache does
    not trust a folder.
    """
    old_time = time.time() - OLD_SECONDS
    for folder_path_, _, _ in os.walk(root / "project"):
        os.utime(folder_path_, (old_time, old_time))


def count_scans(monkeypatch: pytest.MonkeyPatch) -> List[str]:
    scanned_folders: List[str] = []
    scandir = os.scandir

    def scandir_(path: Any) -> Any:
        scanned_folders.append(str(path))
        return scandir(path)

    monkeypatch.setattr(file_tree.os, "scandir", scandir_)
    return scanned_folders


def test_01_unchanged_folders_are_not_scanned_again(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    create_files(tmp_path, "a.py", "src/b.py", "src/sub/c.py", "docs/d.txt")
    make_folders_old(tmp_path)
    first_run = assert_same_as_without_cache(tmp_path)

    scanned_folders = count_scans(monkeypatch)
    second_run = find_files(tmp_path, cached=True)

    assert second_run == first_run
    assert scanned_folders == []


def test_02_added_and_removed_files_are_found(tmp_path: Path) -> None:
    create_files(tmp_path, "a.py", "src/b.py", "src/c.py")
    make_folders_old(tmp_path)
    assert_same_as_without_cache(tmp_path)

    create_files(tmp_path, "src/new.py", "new_folder/e.py")
    (tmp_path / "project" / "src" / "c.py").unlink()

    found_files = assert_same_as_without_cache(tmp_path)
    assert "src/new.py" in found_files
    assert "new_folder/e.py" in found_files
    assert "src/c.py" not in found_files


def test_03_recent_folder_is_scanned_again(tmp_path: Path) -> None:
    """
    A file system with coarse timestamps can keep the mtime of a folder when
    a file is added right after the scan. A folder with an mtime close to
    the time the cache was written is scanned again.
    """
    create_files(tmp_path, "src/a.py")
    folder = tmp_path / "project" / "src"
    recent_time = time.time()
    os.utime(folder, (recent_time, recent_time))
    assert_same_as_without_cache(tmp_path)

    create_files(tmp_path, "src/b.py")
    os.utime(folder, (recent_time, recent_time))

    assert "src/b.py" in assert_same_as_without_cache(tmp_path)


def test_04_file_that_turns_binary_is_skipped(tmp_path: Path) -> None:
    create_files(tmp_path, "src/a.py", "src/b.py")
    make_folders_old(tmp_path)
    assert assert_same_as_without_cache(tmp_path) == ["src/a.py", "src/b.py"]

    folder = tmp_path / "project" / "src"
    folder_stat = os.stat(folder)
    (folder / "b.py").write_bytes(b"binary\x00content")
    # Writing a file keeps the mtime of its folder.
    assert os.stat(folder).st_mtime_ns == folder_stat.st_mtime_ns

    assert assert_same_as_without_cache(tmp_path) == ["src/a.py"]


def test_05_folder_with_symlink_is_never_reused(tmp_path: Path) -> None:
    create_files(tmp_path, "src/a.py", "targets/file.py")
    (tmp_path / "project" / "targets" / "folder").mkdir()
    link = tmp_path / "project" / "src" / "link.py"
    try:
        link.symlink_to(tmp_path / "project" / "targets" / "file.py")
    except OSError:  # pragma: no cover
        pytest.skip("Symbolic links are not supported.")
    make_folders_old(tmp_path)
    assert "src/link.py" in assert_same_as_without_cache(tmp_path)

    (path_to_cache,) = glob.glob(str(tmp_path / "cache" / "file_listing" / "*"))
    with open(path_to_cache, "rb") as cache_file:
        cached_folders = pickle.load(cache_file)["folders"]
    assert str(tmp_path / "project" / "src") not in cached_folders
    assert str(tmp_path / "project" / "targets") in cached_folders

    # The link now points to a folder, and the folder of the link keeps its
    # mtime.
    folder = tmp_path / "project" / "src"
    folder_stat = os.stat(folder)
    link.unlink()
    link.symlink_to(tmp_path / "project" / "targets" / "folder")
    os.utime(folder, ns=(folder_stat.st_atime_ns, folder_stat.st_mtime_ns))

    assert "src/link.py" not in assert_same_as_without_cache(tmp_path)


def test_06_changed_filters_discard_the_cache(tmp_path: Path) -> None:
    create_files(tmp_path, "src/a.py", "tests/b.py", "docs/c.txt")
    make_folders_old(tmp_path)
    assert assert_same_as_without_cache(tmp_path, include_paths=["/src/"]) == [
        "src/a.py"
    ]

    assert assert_same_as_without_cache(
        tmp_path, include_paths=["/src/", "/tests/"]
    ) == ["src/a.py", "tests/b.py"]
    assert assert_same_as_without_cache(tmp_path, exclude_paths=["/docs/"]) == [
        "src/a.py",
        "tests/b.py",
    ]


def test_07_excluded_and_ignored_folders_stay_out(tmp_path: Path) -> None:
    create_files(
        tmp_path,
        "a.py",
        "build/b.py",
        "output_dir/c.py",
        "src/d.py",
        "src/output/e.py",
        "src/folder10/f.py",
        "src/folder2/g.py",
    )
    make_folders_old(tmp_path)

    first_run = assert_same_as_without_cache(
        tmp_path, exclude_paths=["/build/"]
    )
    second_run = assert_same_as_without_cache(
        tmp_path, exclude_paths=["/build/"]
    )

    assert first_run == second_run
    assert first_run == [
        "a.py",
        "src/d.py",
        "src/folder2/g.py",
        "src/folder10/f.py",
    ]
