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


def test_55_include_paths_with_parentheses_in_filenames():
    """
    Verify that parentheses in file and folder names have no effect on the
    inclusion of files.

    This test ensures a proper fix for the issue reported in:
    https://github.com/strictdoc-project/strictdoc/issues/3235
    """

    with tempfile.TemporaryDirectory() as tmp_dir:
        path_to_file1 = os.path.join(tmp_dir, "docs", "input(1).sdoc")
        path_to_file2 = os.path.join(tmp_dir, "docs", "sub(2)", "input.sdoc")

        Path(path_to_file2).parent.mkdir(parents=True, exist_ok=True)

        Path(path_to_file1).touch()
        Path(path_to_file2).touch()

        file_tree = FileFinder.find_files_with_extensions(
            root_path=tmp_dir,
            ignored_dirs=[],
            extensions=[".sdoc"],
            include_paths=["/docs/"],
            exclude_paths=[],
        )

        assert isinstance(file_tree, FileTree)
        assert isinstance(file_tree.root_folder_or_file, Folder)

        folder: Folder = file_tree.root_folder_or_file
        assert len(folder.subfolder_trees) == 1, folder.subfolder_trees

        docs_folder = folder.subfolder_trees[0]
        assert docs_folder.full_path == os.path.join(tmp_dir, "docs")
        assert len(docs_folder.files) == 1
        assert docs_folder.files[0].full_path == path_to_file1

        assert len(docs_folder.subfolder_trees) == 1
        subfolder = docs_folder.subfolder_trees[0]
        assert subfolder.full_path == os.path.join(tmp_dir, "docs", "sub(2)")
        assert len(subfolder.files) == 1
        assert subfolder.files[0].full_path == path_to_file2


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


def test_56_include_paths_skip_folders_without_included_files():
    """
    The walk does not enter the folders that cannot contain an included file,
    so these folders are not in the file tree.
    """

    with tempfile.TemporaryDirectory() as tmp_dir:
        path_to_included_file1 = os.path.join(
            tmp_dir, "tests", "integration", "a.itest"
        )
        path_to_included_file2 = os.path.join(
            tmp_dir, "tests", "integration", "sub", "b.itest"
        )
        path_to_skipped_file1 = os.path.join(
            tmp_dir, "tests", "unit", "c.itest"
        )
        path_to_skipped_file2 = os.path.join(tmp_dir, "build", "d.itest")
        for path_ in (
            path_to_included_file1,
            path_to_included_file2,
            path_to_skipped_file1,
            path_to_skipped_file2,
        ):
            Path(path_).parent.mkdir(parents=True, exist_ok=True)
            Path(path_).touch()

        file_tree = FileFinder.find_files_with_extensions(
            root_path=tmp_dir,
            ignored_dirs=[],
            extensions=None,
            include_paths=["/tests/integration/**.itest"],
            exclude_paths=[],
        )

        found_files = [file_.full_path for _, file_, _ in file_tree.iterate()]
        assert found_files == [path_to_included_file1, path_to_included_file2]

        root_folder = file_tree.root_folder_or_file
        assert isinstance(root_folder, Folder)
        assert [f.folder_name for f in root_folder.subfolder_trees] == ["tests"]
        tests_folder = root_folder.subfolder_trees[0]
        assert [f.folder_name for f in tests_folder.subfolder_trees] == [
            "integration"
        ]


def test_57_include_paths_not_anchored_keep_all_folders():
    """
    A mask that does not start with "/" can match in any folder, so the walk
    enters all folders.
    """

    with tempfile.TemporaryDirectory() as tmp_dir:
        path_to_file1 = os.path.join(tmp_dir, "docs", "a.sdoc")
        path_to_file2 = os.path.join(tmp_dir, "build", "docs", "b.sdoc")
        for path_ in (path_to_file1, path_to_file2):
            Path(path_).parent.mkdir(parents=True, exist_ok=True)
            Path(path_).touch()

        file_tree = FileFinder.find_files_with_extensions(
            root_path=tmp_dir,
            ignored_dirs=[],
            extensions=[".sdoc"],
            include_paths=["docs/"],
            exclude_paths=[],
        )

        found_files = sorted(
            file_.full_path for _, file_, _ in file_tree.iterate()
        )
        assert found_files == sorted([path_to_file1, path_to_file2])


def test_58_subfolders_and_files_are_sorted():
    """
    Subfolders are in alphanumeric order, so "folder2" comes before
    "folder10". Files are in the order of their names.
    """

    with tempfile.TemporaryDirectory() as tmp_dir:
        for folder_name_ in ("folder10", "folder2", "folder1"):
            for file_name_ in ("b.sdoc", "a.sdoc"):
                path_to_file = os.path.join(tmp_dir, folder_name_, file_name_)
                Path(path_to_file).parent.mkdir(parents=True, exist_ok=True)
                Path(path_to_file).touch()

        file_tree = FileFinder.find_files_with_extensions(
            root_path=tmp_dir,
            ignored_dirs=[],
            extensions=[".sdoc"],
            include_paths=[],
            exclude_paths=[],
        )

        root_folder = file_tree.root_folder_or_file
        assert isinstance(root_folder, Folder)
        assert [f.folder_name for f in root_folder.subfolder_trees] == [
            "folder1",
            "folder2",
            "folder10",
        ]
        for subfolder_ in root_folder.subfolder_trees:
            assert [f.file_name for f in subfolder_.files] == [
                "a.sdoc",
                "b.sdoc",
            ]


def test_59_folder_name_of_paths_that_need_normalization():
    with tempfile.TemporaryDirectory() as tmp_dir:
        path_to_folder = os.path.join(tmp_dir, "folder")
        Path(path_to_folder, "subfolder").mkdir(parents=True)

        assert Folder(path_to_folder, ".", 0).folder_name == "folder"
        assert Folder(path_to_folder + os.sep, ".", 0).folder_name == "folder"
        assert (
            Folder(os.path.join(path_to_folder, "."), ".", 0).folder_name
            == "folder"
        )
        assert (
            Folder(
                os.path.join(path_to_folder, "subfolder", ".."), ".", 0
            ).folder_name
            == "folder"
        )
