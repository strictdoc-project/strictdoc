import os
import tempfile
from pathlib import Path

from strictdoc.core.file_system.document_finder import DocumentFinder
from strictdoc.core.file_system.file_tree import Folder


def test_01_document_finder_build_file_tree_includes_markdown_files(
    default_project_config,
):
    with tempfile.TemporaryDirectory() as temp_dir:
        Path(os.path.join(temp_dir, "a.sdoc")).touch()
        Path(os.path.join(temp_dir, "b.md")).touch()
        Path(os.path.join(temp_dir, "c.markdown")).touch()
        Path(os.path.join(temp_dir, "ignored.txt")).touch()

        default_project_config.input_paths = [temp_dir]

        file_trees, _ = DocumentFinder._build_file_tree(default_project_config)

        assert len(file_trees) == 1
        root_folder_or_file = file_trees[0].root_folder_or_file
        assert isinstance(root_folder_or_file, Folder)

        file_names = [file_.file_name for file_ in root_folder_or_file.files]
        assert "a.sdoc" in file_names
        assert "b.md" in file_names
        assert "c.markdown" in file_names
        assert "ignored.txt" not in file_names
