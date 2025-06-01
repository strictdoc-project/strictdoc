# mypy: disable-error-code="no-untyped-call"
import os
from pathlib import Path
from typing import List

from strictdoc.core.file_tree import File, FileFinder
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.source_tree import SourceFile, SourceTree


class SourceFilesFinder:
    @staticmethod
    def find_source_files(
        project_config: ProjectConfig,
    ) -> SourceTree:
        map_file_to_source = {}
        found_source_files: List[SourceFile] = []

        # TODO: Unify this on the FileTree class level.
        doctree_root_abs_path = (
            project_config.source_root_path
            if project_config.source_root_path is not None
            else os.getcwd()
        )
        doctree_root_abs_path = (
            os.path.dirname(doctree_root_abs_path)
            if os.path.isfile(doctree_root_abs_path)
            else doctree_root_abs_path
        )

        assert isinstance(project_config.output_dir, str)

        exclude_paths = project_config.exclude_source_paths + ["**.DS_Store"]

        file_tree = FileFinder.find_files_with_extensions(
            root_path=doctree_root_abs_path,
            ignored_dirs=[project_config.output_dir],
            extensions=None,
            include_paths=project_config.include_source_paths,
            exclude_paths=exclude_paths,
        )
        root_level = doctree_root_abs_path.count(os.sep)

        file: File
        for _, file, _ in file_tree.iterate():
            in_doctree_source_file_rel_path = os.path.relpath(
                file.full_path, doctree_root_abs_path
            )
            last_folder_in_path: str = os.path.relpath(
                file.folder_path, doctree_root_abs_path
            )
            output_dir_full_path: str = os.path.join(
                project_config.export_output_html_root,
                "_source_files",
                last_folder_in_path,
            )
            Path(output_dir_full_path).mkdir(parents=True, exist_ok=True)

            output_file_name = f"{file.file_name}.html"
            output_file_full_path = os.path.join(
                output_dir_full_path, output_file_name
            )

            level = file.folder_path.count(os.sep) - root_level

            source_file = SourceFile(
                level,
                file.full_path,
                in_doctree_source_file_rel_path,
                output_dir_full_path,
                output_file_full_path,
            )
            found_source_files.append(source_file)
            map_file_to_source[file] = source_file

        source_tree = SourceTree(
            file_tree, found_source_files, map_file_to_source
        )
        return source_tree
