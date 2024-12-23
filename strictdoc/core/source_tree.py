# mypy: disable-error-code="no-untyped-def,var-annotated"
import os
from enum import Enum
from typing import Dict, List, Sequence

from strictdoc.core.file_tree import File, FileTree
from strictdoc.helpers.auto_described import auto_described


class SourceFileType(Enum):
    PYTHON = [".py"]
    C = [".h", ".c"]
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
        if path_to_file.endswith(".h") or path_to_file.endswith(".c"):
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
class SourceFile:
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


class SourceTree:
    def __init__(
        self,
        file_tree: FileTree,
        source_files: Sequence[SourceFile],
        map_file_to_source: Dict[File, SourceFile],
    ):
        self.file_tree = file_tree
        self.source_files = source_files
        self.map_file_to_source = map_file_to_source

    def get_source_for_file(self, file):
        assert isinstance(file, File)
        return self.map_file_to_source[file]
