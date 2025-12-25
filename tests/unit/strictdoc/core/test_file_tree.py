import os
import tempfile
from pathlib import Path

from strictdoc.core.file_tree import File, FileFinder, FileTree, Folder


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
