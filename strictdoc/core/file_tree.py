import functools
import os
from typing import Dict, Iterator, List, Optional, Tuple, Union

from typing_extensions import TypeAlias

from strictdoc.helpers.path_filter import PathFilter
from strictdoc.helpers.paths import SDocRelativePath
from strictdoc.helpers.sorting import alphanumeric_sort

FileOrFolderEntry: TypeAlias = Union["File", "Folder"]


class File:
    def __init__(self, level: int, full_path: str, rel_path: SDocRelativePath):
        assert os.path.isfile(full_path)
        assert os.path.isabs(full_path)
        assert isinstance(rel_path, SDocRelativePath)

        self.level: int = level
        self.full_path: str = full_path
        self.rel_path: SDocRelativePath = rel_path
        self.folder_path: str = os.path.dirname(self.full_path)
        self.mount_folder: str = os.path.basename(self.folder_path)
        self.file_name: str = os.path.basename(self.full_path)
        self.files = [self]
        self.subfolder_trees: List[Folder] = []

    def is_folder(self) -> bool:
        return False

    def has_extension(self, extension: str) -> bool:
        return self.full_path.endswith(extension)


class Folder:
    def __init__(self, full_path: str, rel_path: str, level: int) -> None:
        assert os.path.isdir(full_path)
        assert os.path.isabs(full_path)
        assert isinstance(rel_path, str)

        self.full_path: str = full_path
        self.rel_path: str = rel_path if rel_path != "." else ""
        self.folder_name: str = os.path.basename(os.path.normpath(full_path))
        self.mount_folder: str = os.path.basename(self.full_path)
        self.level: int = level
        self.files: List[File] = []
        self.subfolder_trees: List[Folder] = []
        self.parent_folder: Optional[Folder] = None
        self.has_sdoc_content = False

    def __repr__(self) -> str:
        return f"Folder: (root_path: {self.full_path}, files: {self.files})"

    def is_folder(self) -> bool:
        return True

    def has_content(self) -> bool:
        if len(self.files) > 0:
            return True
        for subfolder_ in self.subfolder_trees:
            if subfolder_.has_content():
                return True
        return False

    def add_subfolder_tree(self, subfolder_tree: "Folder") -> None:
        assert isinstance(subfolder_tree, Folder)
        self.subfolder_trees.append(subfolder_tree)

    def set_parent_folder(self, parent_folder: "Folder") -> None:
        assert isinstance(parent_folder, Folder)
        self.parent_folder = parent_folder


class FileTree:
    def __init__(self, *, root_folder_or_file: FileOrFolderEntry) -> None:
        self.root_folder_or_file: FileOrFolderEntry = root_folder_or_file

    @staticmethod
    def create_single_file_tree(root_path: str) -> "FileTree":
        single_file = File(1, root_path, SDocRelativePath(""))
        return FileTree(root_folder_or_file=single_file)

    def iterate(self) -> Iterator[Tuple[Union[Folder, File], File, str]]:
        file_tree_mount_folder = self.root_folder_or_file.mount_folder

        task_list = [self.root_folder_or_file]
        while len(task_list) > 0:
            current_tree = task_list.pop(0)

            for doc_file in current_tree.files:
                yield self.root_folder_or_file, doc_file, file_tree_mount_folder

            task_list.extend(current_tree.subfolder_trees)


class FileFinder:
    @staticmethod
    def find_files_with_extensions(
        *,
        root_path: str,
        ignored_dirs: List[str],
        extensions: Optional[List[str]],
        include_paths: List[str],
        exclude_paths: List[str],
    ) -> FileTree:
        assert os.path.isdir(root_path)
        assert os.path.isabs(root_path), root_path
        assert not root_path.endswith("/"), root_path

        extensions_tuple = tuple(extensions) if extensions is not None else ()

        path_filter_includes = PathFilter(
            include_paths, positive_or_negative=True
        )
        path_filter_excludes = PathFilter(
            exclude_paths, positive_or_negative=False
        )
        root_level: int = root_path.count(os.sep)

        root_folder: Folder = Folder(root_path, ".", 0)
        folder_map: Dict[str, Folder] = {root_path: root_folder}

        for current_root_path, dirs, files in os.walk(root_path, topdown=True):
            if current_root_path in ignored_dirs:
                dirs[:] = []
                continue

            current_root_relative_path = os.path.relpath(
                current_root_path, start=root_path
            )
            current_root_relative_path = (
                (current_root_relative_path + "/")
                if current_root_relative_path != "."
                else ""
            )

            if path_filter_excludes.match(current_root_relative_path):
                dirs[:] = []
                continue

            dirs[:] = [
                d
                for d in dirs
                if (not d.startswith(".") and d not in ("output", "Output"))
            ]
            dirs.sort(key=alphanumeric_sort)

            current_root_path_level: int = (
                current_root_path.count(os.sep) - root_level
            )

            current_tree = folder_map.setdefault(
                current_root_path,
                Folder(
                    current_root_path,
                    current_root_relative_path,
                    current_root_path_level,
                ),
            )

            for file in files:
                if len(extensions_tuple) > 0 and not file.endswith(
                    extensions_tuple
                ):
                    continue

                full_file_path = os.path.join(current_root_path, file)
                rel_file_path = os.path.join(current_root_relative_path, file)

                if path_filter_excludes.match(rel_file_path):
                    continue

                if path_filter_includes.match(rel_file_path):
                    current_tree.files.append(
                        File(
                            current_tree.level + 1,
                            full_file_path,
                            SDocRelativePath(rel_file_path),
                        )
                    )

            def file_path_sort_key(lhs: File, rhs: File) -> int:
                return (rhs.file_name < lhs.file_name) - (
                    lhs.file_name < rhs.file_name
                )

            sort_key = functools.cmp_to_key(file_path_sort_key)
            current_tree.files.sort(key=sort_key)

            if len(current_tree.files) > 0:
                current_tree.has_sdoc_content = True

            if current_root_path == root_path:
                continue

            current_parent_path = os.path.dirname(current_root_path)

            # Top-down search assumes we have seen the parent before.
            assert current_parent_path in folder_map, (
                current_parent_path,
                folder_map,
            )

            current_parent_folder: Folder = folder_map[current_parent_path]
            current_tree.set_parent_folder(current_parent_folder)
            if current_tree.has_sdoc_content:
                parent_folder_cursor: Optional[Folder] = current_parent_folder
                while (
                    parent_folder_cursor
                    and not parent_folder_cursor.has_sdoc_content
                ):
                    parent_folder_cursor.has_sdoc_content = True
                    parent_folder_cursor = parent_folder_cursor.parent_folder

            current_parent_folder.add_subfolder_tree(current_tree)

        file_tree_structure = FileTree(
            root_folder_or_file=folder_map[root_path]
        )
        return file_tree_structure


class PathFinder:
    @staticmethod
    def find_directories(
        root_path: str,
        directory: str,
        include_paths: List[str],
        exclude_paths: List[str],
    ) -> List[str]:
        assert os.path.isdir(root_path)
        assert os.path.isabs(root_path)

        path_filter_includes = PathFilter(
            include_paths, positive_or_negative=True
        )
        path_filter_excludes = PathFilter(
            exclude_paths, positive_or_negative=False
        )

        directories = []
        # Declare str type to make os.path.relpath type checking happy.
        current_root_path: str
        for current_root_path, dirs, _ in os.walk(root_path, topdown=True):
            current_root_relative_path: str = os.path.relpath(
                current_root_path, start=root_path
            )
            current_root_relative_path = (
                current_root_relative_path + "/"
                if current_root_relative_path != "."
                else ""
            )

            if len(current_root_relative_path) > 0:
                if path_filter_excludes.match(
                    current_root_relative_path
                ) or not path_filter_includes.match(current_root_relative_path):
                    dirs[:] = []
                    continue

            dirs[:] = [
                d
                for d in dirs
                if not d.startswith(".")
                and not d.startswith("__")
                and d not in ("build", "output", "Output", "tests")
            ]

            if os.path.basename(current_root_path) == directory:
                directories.append(current_root_path)

        return directories
