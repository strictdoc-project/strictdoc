# mypy: disable-error-code="arg-type,no-untyped-call,no-untyped-def,var-annotated"
import os
from enum import Enum
from pathlib import Path
from typing import List

from strictdoc.core.file_tree import File, FileFinder
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.source_tree import SourceTree
from strictdoc.helpers.auto_described import auto_described


class SourceFileType(Enum):
    PYTHON = [".py"]
    C = [".c"]
    CPP = [".cpp", ".cc"]
    TEX = [".tex"]
    # Is there an idiomatic file extension for Jinja templates?
    # https://stackoverflow.com/questions/29590931/is-there-an-idiomatic-file-extension-for-jinja-templates
    TOML = [".toml"]
    JINJA = [".jinja", ".jinja2", ".j2", ".html.jinja"]
    JAVASCRIPT = [".js"]
    YAML = [".yaml", ".yml"]
    RST = [".rst"]
    SDOC = [".sdoc"]

    UNKNOWN = []

    @classmethod
    def create_from_path(cls, path_to_file: str) -> "SourceFileType":
        if path_to_file.endswith(".py"):
            return cls.PYTHON
        if path_to_file.endswith(".c"):
            return cls.C
        for enum_value in SourceFileType.CPP.value:
            if path_to_file.endswith(enum_value):
                return cls.CPP
        if path_to_file.endswith(".tex"):
            return cls.TEX
        if path_to_file.endswith(".toml"):
            return cls.TOML
        for enum_value in SourceFileType.JINJA.value:
            if path_to_file.endswith(enum_value):
                return cls.JINJA
        if path_to_file.endswith(".js"):
            return cls.JAVASCRIPT
        for enum_value in SourceFileType.YAML.value:
            if path_to_file.endswith(enum_value):
                return cls.YAML
        for enum_value in SourceFileType.RST.value:
            if path_to_file.endswith(enum_value):
                return cls.RST
        if path_to_file.endswith(".sdoc"):
            return cls.SDOC

        return cls.UNKNOWN

    @staticmethod
    def all() -> List[str]:  # noqa: A003
        all_extensions = []
        for enum_value in SourceFileType:
            all_extensions += enum_value.value
        return all_extensions


@auto_described
class SourceFile:  # pylint: disable=too-many-instance-attributes
    def __init__(
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
        self.file_name = os.path.basename(full_path)
        self.in_doctree_source_file_rel_path = in_doctree_source_file_rel_path
        self.in_doctree_source_file_rel_path_posix: str = (
            in_doctree_source_file_rel_path.replace("\\", "/")
        )
        self.output_dir_full_path = output_dir_full_path
        self.output_file_full_path = output_file_full_path
        self.path_depth_prefix = ("../" * (level + 1))[:-1]

        self.file_type: SourceFileType = SourceFileType.create_from_path(
            in_doctree_source_file_rel_path
        )

        self.traceability_info = None
        self.is_referenced = False

    def is_python_file(self):
        return self.file_type == SourceFileType.PYTHON

    def is_c_file(self):
        return self.file_type == SourceFileType.C

    def is_cpp_file(self):
        return self.file_type == SourceFileType.CPP

    def is_tex_file(self):
        return self.file_type == SourceFileType.TEX

    def is_toml_file(self):
        return self.file_type == SourceFileType.TOML

    def is_jinja_file(self):
        return self.file_type == SourceFileType.JINJA

    def is_javascript_file(self):
        return self.file_type == SourceFileType.JAVASCRIPT

    def is_yaml_file(self):
        return self.file_type == SourceFileType.YAML

    def is_rst_file(self):
        return self.file_type == SourceFileType.RST

    def is_sdoc_file(self):
        return self.file_type == SourceFileType.SDOC


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
                project_config.export_output_html_root,
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
