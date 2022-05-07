import os
import tempfile
from pathlib import Path

from strictdoc.core.file_tree import FileFinder, FileTree, Folder, File


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
            extensions={".py"},
        )

        assert isinstance(file_tree, FileTree)
        assert isinstance(file_tree.root_folder_or_file, Folder)

        folder: Folder = file_tree.root_folder_or_file
        assert folder.root_path == tmp_dir
        assert len(folder.files) == 3

        found_file1 = folder.files[0]
        assert isinstance(found_file1, File)
        assert found_file1.root_path == path_to_file1

        found_file2 = folder.files[1]
        assert isinstance(found_file2, File)
        assert found_file2.root_path == path_to_file2

        found_file3 = folder.files[2]
        assert isinstance(found_file3, File)
        assert found_file3.root_path == path_to_file3
