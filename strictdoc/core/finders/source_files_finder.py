import os
from pathlib import Path
from typing import List

from strictdoc.backend.source_file_syntax.reader import (
    SourceFileTraceabilityInfo,
)
from strictdoc.core.document_tree import DocumentTree, FileTree


class SourceFile:
    def __init__(
        self,
        level,
        doctree_root_mount_path,
        in_cwd_source_file_rel_path,
        in_doctree_source_file_rel_path,
        output_path_dir_full_path,
        output_path_file_full_path,
    ):
        assert isinstance(level, int)
        assert os.path.exists(in_cwd_source_file_rel_path)

        self.level = level
        self.doctree_root_mount_path = doctree_root_mount_path
        self.in_cwd_source_file_rel_path = in_cwd_source_file_rel_path
        self.in_doctree_source_file_rel_path = in_doctree_source_file_rel_path
        self.output_path_dir_full_path = output_path_dir_full_path
        self.output_path_file_full_path = output_path_file_full_path
        self.path_depth_prefix = ("../" * (level + 2))[:-1]
        self.traceability_info = None

    def __str__(self):
        return (
            "SourceFile("
            "level: {}, "
            "in_cwd_source_file_rel_path: {}, "
            "in_doctree_source_file_rel_path: {}, "
            "output_path_dir_full_path: {}, "
            "output_path_file_full_path: {}"
            ")".format(
                self.level,
                self.in_cwd_source_file_rel_path,
                self.in_doctree_source_file_rel_path,
                self.output_path_dir_full_path,
                self.output_path_file_full_path,
            )
        )


class SourceFilesFinder:
    @staticmethod
    def find_source_files(
        output_html_root, document_tree: DocumentTree
    ) -> List[SourceFile]:
        found_source_files: List[SourceFile] = []
        the_only_file_tree: FileTree = document_tree.file_tree[0]
        assert os.path.abspath(the_only_file_tree.root_path)

        # TODO: Unify this on the FileTree class level.
        # Introduce #mount_directory method?
        doctree_root_abs_path = the_only_file_tree.root_path
        doctree_root_abs_path = (
            os.path.dirname(doctree_root_abs_path)
            if os.path.isfile(doctree_root_abs_path)
            else doctree_root_abs_path
        )
        doctree_root_mount_path = os.path.basename(doctree_root_abs_path)
        root_level = doctree_root_abs_path.count(os.sep)

        for current_root_path, dirs, files in os.walk(
            doctree_root_abs_path, topdown=False
        ):
            for file in files:
                in_cwd_source_file_rel_path = f"{current_root_path}/{file}"
                in_doctree_source_file_rel_path = os.path.relpath(
                    in_cwd_source_file_rel_path, doctree_root_abs_path
                )
                if file.endswith(".py"):
                    last_folder_in_path = os.path.relpath(
                        current_root_path, doctree_root_abs_path
                    )
                    output_path_dir_full_path = f"{output_html_root}/_source_files/{doctree_root_mount_path}/{last_folder_in_path}"
                    Path(output_path_dir_full_path).mkdir(
                        parents=True, exist_ok=True
                    )

                    output_path_file_full_path = (
                        f"{output_path_dir_full_path}/{file}.html"
                    )

                    level = current_root_path.count(os.sep) - root_level

                    source_file = SourceFile(
                        level,
                        doctree_root_mount_path,
                        in_cwd_source_file_rel_path,
                        in_doctree_source_file_rel_path,
                        output_path_dir_full_path,
                        output_path_file_full_path,
                    )
                    found_source_files.append(source_file)

        return found_source_files
