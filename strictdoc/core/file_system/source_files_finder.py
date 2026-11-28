import os
from typing import List

from strictdoc.core.file_system.file_tree import File, FileFinder
from strictdoc.core.file_system.source_tree import SourceFile, SourceTree
from strictdoc.core.project_config import ProjectConfig


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

        file_tree = FileFinder.find_files_with_extensions(
            root_path=doctree_root_abs_path,
            ignored_dirs=[project_config.output_dir],
            extensions=None,
            include_paths=project_config.include_source_paths,
            exclude_paths=project_config.exclude_source_paths,
            path_to_cache_dir=project_config.get_path_to_cache_dir(),
        )
        root_level = doctree_root_abs_path.count(os.sep)
        # The found paths start with the root prefix because FileFinder joins
        # the root path and the names it finds. Cutting the prefix off gives
        # the same result as os.path.relpath(), without the cost of
        # normalizing both paths for every file.
        root_prefix: str = (
            doctree_root_abs_path
            if doctree_root_abs_path.endswith(os.sep)
            else doctree_root_abs_path + os.sep
        )
        source_files_output_dir = os.path.join(
            project_config.export_output_html_root, "_source_files"
        )

        file: File
        for _, file, _ in file_tree.iterate():
            assert file.full_path.startswith(root_prefix), file.full_path
            in_doctree_source_file_rel_path = file.full_path[len(root_prefix) :]
            last_folder_in_path: str = (
                file.folder_path[len(root_prefix) :]
                if file.folder_path != doctree_root_abs_path
                else "."
            )
            # The page writer creates this folder when it writes the page.
            output_dir_full_path: str = os.path.join(
                source_files_output_dir, last_folder_in_path
            )

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
