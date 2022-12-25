import os
from pathlib import Path
from typing import List

from strictdoc.cli.cli_arg_parser import ExportCommandConfig
from strictdoc.core.file_tree import FileFinder, File
from strictdoc.core.source_tree import SourceTree
from strictdoc.helpers.auto_described import auto_described


@auto_described
class SourceFile:  # pylint: disable=too-many-instance-attributes
    def __init__(  # pylint: disable=too-many-arguments
        self,
        level,
        full_path,
        in_doctree_source_file_rel_path,
        output_dir_full_path,
        output_file_full_path,
    ):
        assert isinstance(level, int)
        assert os.path.exists(full_path)

        self.level = level
        self.full_path = full_path
        self.in_doctree_source_file_rel_path = in_doctree_source_file_rel_path
        self.output_dir_full_path = output_dir_full_path
        self.output_file_full_path = output_file_full_path
        self.path_depth_prefix = ("../" * (level + 1))[:-1]

        _, file_extension = os.path.splitext(in_doctree_source_file_rel_path)
        self.extension = file_extension

        self.traceability_info = None
        self.is_referenced = False

    def is_python_file(self):
        return self.extension == ".py"

    def is_c_file(self):
        return self.extension == ".c"

    def is_cpp_file(self):
        return self.extension == ".cpp"

    def is_tex_file(self):
        return self.extension == ".tex"


class SourceFilesFinder:
    @staticmethod
    def find_source_files(config: ExportCommandConfig) -> SourceTree:
        map_file_to_source = {}
        found_source_files: List[SourceFile] = []

        # TODO: Unify this on the FileTree class level.
        # Introduce #mount_directory method?
        doctree_root_abs_path = os.getcwd()
        doctree_root_abs_path = (
            os.path.dirname(doctree_root_abs_path)
            if os.path.isfile(doctree_root_abs_path)
            else doctree_root_abs_path
        )

        file_tree = FileFinder.find_files_with_extensions(
            root_path=doctree_root_abs_path,
            ignored_dirs=[config.output_dir],
            extensions={".py", ".c", ".cpp", ".tex"},
        )
        root_level = doctree_root_abs_path.count(os.sep)

        file: File
        for _, file, _ in file_tree.iterate():
            in_doctree_source_file_rel_path = os.path.relpath(
                file.root_path, doctree_root_abs_path
            )
            last_folder_in_path: str = os.path.relpath(
                file.get_folder_path(), doctree_root_abs_path
            )
            output_dir_full_path: str = os.path.join(
                config.output_html_root,
                "_source_files",
                last_folder_in_path,
            )
            Path(output_dir_full_path).mkdir(parents=True, exist_ok=True)

            output_file_name = f"{file.get_file_name()}.html"
            output_file_full_path = os.path.join(
                output_dir_full_path, output_file_name
            )

            level = file.get_folder_path().count(os.sep) - root_level

            source_file = SourceFile(
                level,
                file.root_path,
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
