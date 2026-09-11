import os
import tempfile
from pathlib import Path
from unittest.mock import patch

from strictdoc.core.file_system.file_tree import (
    File,
    FileFinder,
    FileTree,
    Folder,
    PathFinder,
)


def test_01():
    with tempfile.TemporaryDirectory() as tmp_dir:
        path_to_file1 = os.path.join(tmp_dir, "file1.py")
        path_to_file2 = os.path.join(tmp_dir, "file2.py")
        path_to_file3 = os.path.join(tmp_dir, "file3.py")
        Path(path_to_file1).touch()
        Path(path_to_file2).touch()
        Path(path_to_file3).touch()

        file_tree = FileFinder.find_files_with_extensions(
            root_path=tmp_dir,
            ignored_dirs=[],
            extensions=[".py"],
            include_paths=[],
            exclude_paths=[],
        )

        assert isinstance(file_tree, FileTree)
        assert isinstance(file_tree.root_folder_or_file, Folder)

        folder: Folder = file_tree.root_folder_or_file
        assert folder.full_path == tmp_dir
        assert len(folder.files) == 3

        found_file1 = folder.files[0]
        assert isinstance(found_file1, File)
        assert found_file1.full_path == path_to_file1

        found_file2 = folder.files[1]
        assert isinstance(found_file2, File)
        assert found_file2.full_path == path_to_file2

        found_file3 = folder.files[2]
        assert isinstance(found_file3, File)
        assert found_file3.full_path == path_to_file3


def test_50_include_paths():
    with tempfile.TemporaryDirectory() as tmp_dir:
        path_to_file1 = os.path.join(tmp_dir, "file1.py")
        path_to_file2 = os.path.join(tmp_dir, "file2.py")
        path_to_file3 = os.path.join(tmp_dir, "file3.py")
        Path(path_to_file1).touch()
        Path(path_to_file2).touch()
        Path(path_to_file3).touch()

        file_tree = FileFinder.find_files_with_extensions(
            root_path=tmp_dir,
            ignored_dirs=[],
            extensions=[".py"],
            include_paths=["file1.py"],
            exclude_paths=[],
        )

        assert isinstance(file_tree, FileTree)
        assert isinstance(file_tree.root_folder_or_file, Folder)

        folder: Folder = file_tree.root_folder_or_file
        assert folder.full_path == tmp_dir
        assert len(folder.files) == 1

        found_file1 = folder.files[0]
        assert isinstance(found_file1, File)
        assert found_file1.full_path == path_to_file1


def test_52_exclude_paths():
    with tempfile.TemporaryDirectory() as tmp_dir:
        path_to_file1 = os.path.join(tmp_dir, "file1.py")
        path_to_file2 = os.path.join(tmp_dir, "file2.py")
        path_to_file3 = os.path.join(tmp_dir, "file3.py")
        Path(path_to_file1).touch()
        Path(path_to_file2).touch()
        Path(path_to_file3).touch()

        file_tree = FileFinder.find_files_with_extensions(
            root_path=tmp_dir,
            ignored_dirs=[],
            extensions=[".py"],
            include_paths=[],
            exclude_paths=["file3.py"],
        )

        assert isinstance(file_tree, FileTree)
        assert isinstance(file_tree.root_folder_or_file, Folder)

        folder: Folder = file_tree.root_folder_or_file
        assert folder.full_path == tmp_dir
        assert len(folder.files) == 2

        found_file1 = folder.files[0]
        assert isinstance(found_file1, File)
        assert found_file1.full_path == path_to_file1

        found_file2 = folder.files[1]
        assert isinstance(found_file2, File)
        assert found_file2.full_path == path_to_file2


def test_53_both_include_and_exclude_paths():
    with tempfile.TemporaryDirectory() as tmp_dir:
        path_to_file1 = os.path.join(tmp_dir, "file1.py")
        path_to_file2 = os.path.join(tmp_dir, "file2.py")
        path_to_file3 = os.path.join(tmp_dir, "file3.py")
        Path(path_to_file1).touch()
        Path(path_to_file2).touch()
        Path(path_to_file3).touch()

        file_tree = FileFinder.find_files_with_extensions(
            root_path=tmp_dir,
            ignored_dirs=[],
            extensions=[".py"],
            include_paths=["file*.py"],
            exclude_paths=["file3.py"],
        )

        assert isinstance(file_tree, FileTree)
        assert isinstance(file_tree.root_folder_or_file, Folder)

        folder: Folder = file_tree.root_folder_or_file
        assert folder.full_path == tmp_dir
        assert len(folder.files) == 2

        found_file1 = folder.files[0]
        assert isinstance(found_file1, File)
        assert found_file1.full_path == path_to_file1

        found_file2 = folder.files[1]
        assert isinstance(found_file2, File)
        assert found_file2.full_path == path_to_file2


def test_55_dev_path_bypasses_include_and_exclude_filters():
    with tempfile.TemporaryDirectory() as tmp_dir:
        ignored_dir = os.path.join(tmp_dir, "ignored")
        Path(ignored_dir).mkdir()
        included_file = os.path.join(ignored_dir, "included.sdoc")
        excluded_file = os.path.join(ignored_dir, "excluded.sdoc")
        Path(included_file).touch()
        Path(excluded_file).touch()

        file_tree = FileFinder.find_files_with_extensions(
            root_path=tmp_dir,
            ignored_dirs=[],
            extensions=[".sdoc"],
            include_paths=["/docs/"],
            exclude_paths=["/ignored/"],
            dev_include_paths=["/ignored/included.sdoc"],
        )

        found_files = [file_ for _, file_, _ in file_tree.iterate()]
        assert len(found_files) == 1
        assert found_files[0].full_path == included_file


def test_56_exclude_filter_applies_without_dev_paths():
    with tempfile.TemporaryDirectory() as tmp_dir:
        ignored_file = os.path.join(tmp_dir, "ignored.sdoc")
        Path(ignored_file).touch()

        file_tree = FileFinder.find_files_with_extensions(
            root_path=tmp_dir,
            ignored_dirs=[],
            extensions=[".sdoc"],
            include_paths=[],
            exclude_paths=["/ignored.sdoc"],
        )

        assert list(file_tree.iterate()) == []


def test_57_system_ignored_directory_cannot_be_dev_included():
    with tempfile.TemporaryDirectory() as tmp_dir:
        ignored_dir = os.path.join(tmp_dir, "ignored")
        Path(ignored_dir).mkdir()
        excluded_file = os.path.join(ignored_dir, "excluded.sdoc")
        Path(excluded_file).touch()

        file_tree = FileFinder.find_files_with_extensions(
            root_path=tmp_dir,
            extensions=[".sdoc"],
            include_paths=[],
            exclude_paths=[],
            dev_include_paths=["/ignored/excluded.sdoc"],
            ignored_dirs=[ignored_dir],
        )

        assert list(file_tree.iterate()) == []


def test_54_exclude_paths():
    """
    Verify that spaces in filenames have no effect on the exclusion/inclusion
    of files.

    This test ensures a proper fix for the issue reported in:
    https://github.com/strictdoc-project/strictdoc/issues/2594
    """

    with tempfile.TemporaryDirectory() as tmp_dir:
        path_to_file1 = os.path.join(tmp_dir, "file1.py")
        path_to_file2 = os.path.join(tmp_dir, "file2.py")
        path_to_file3 = os.path.join(tmp_dir, "dev/file 3.log")

        Path(path_to_file3).parent.mkdir(parents=True, exist_ok=True)

        Path(path_to_file1).touch()
        Path(path_to_file2).touch()
        Path(path_to_file3).touch()

        file_tree = FileFinder.find_files_with_extensions(
            root_path=tmp_dir,
            ignored_dirs=[],
            extensions=[".py", ".log"],
            include_paths=[],
            exclude_paths=["**/*.log"],
        )

        assert isinstance(file_tree, FileTree)
        assert isinstance(file_tree.root_folder_or_file, Folder)

        folder: Folder = file_tree.root_folder_or_file
        assert folder.full_path == tmp_dir
        assert len(folder.files) == 2

        # Verify that the .log file is not found.
        assert len(folder.subfolder_trees) == 1, folder.subfolder_trees
        subfolder = folder.subfolder_trees[0]
        assert subfolder.full_path == os.path.join(tmp_dir, "dev")
        assert len(subfolder.files) == 0
        assert len(subfolder.subfolder_trees) == 0


def test_60_find_directories_with_include_paths_and_windows_separators():
    """
    Verify that the find_directories method correctly handles include paths with
    Windows-style path separators.

    This test ensures a proper fix for the issue reported in:
    https://github.com/strictdoc-project/strictdoc/issues/2776
    """

    with tempfile.TemporaryDirectory() as tmp_dir:
        assets_dir = os.path.join(
            tmp_dir, "prod_requirements", "req", "_assets"
        )
        Path(assets_dir).mkdir(parents=True)

        original_relpath = os.path.relpath

        def relpath_with_windows_separators(path, start=None):
            return original_relpath(path, start=start).replace("/", "\\")

        with patch(
            "strictdoc.core.file_system.file_tree.os.path.relpath",
            relpath_with_windows_separators,
        ):
            directories = PathFinder.find_directories(
                tmp_dir,
                "_assets",
                include_paths=["prod_requirements/"],
                exclude_paths=[],
            )

        assert directories == [assets_dir]
