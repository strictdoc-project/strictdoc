import collections
import functools
import os
from typing import Dict, List, Optional

from strictdoc.helpers.path_filter import PathFilter
from strictdoc.helpers.sorting import alphanumeric_sort


class FileOrFolderEntry:
    def get_full_path(self):
        raise NotImplementedError

    def get_level(self):
        raise NotImplementedError

    def is_folder(self):
        raise NotImplementedError

    def mount_folder(self):
        raise NotImplementedError


class File(FileOrFolderEntry):
    def __init__(self, level, full_path, rel_path: str):
        assert os.path.isfile(full_path)
        assert os.path.isabs(full_path)
        assert isinstance(rel_path, str)
        self.level = level
        self.full_path = full_path
        self.root_path = full_path
        self.rel_path = rel_path
        self.file_name = os.path.basename(self.full_path)
        self.files = [self]
        self.subfolder_trees = []

    def __repr__(self):
        return f"File: {self.full_path}"

    def is_folder(self):
        return False

    def get_full_path(self):
        return self.full_path

    def get_level(self) -> int:
        return self.level

    def get_file_name(self) -> str:
        return self.file_name

    def get_folder_path(self) -> str:
        return os.path.dirname(self.full_path)

    def mount_folder(self) -> str:
        return os.path.basename(os.path.dirname(self.root_path))


class Folder(FileOrFolderEntry):  # pylint: disable=too-many-instance-attributes
    def __init__(self, root_path: str, rel_path: str, level):
        assert os.path.isdir(root_path)
        assert os.path.isabs(root_path)
        assert isinstance(rel_path, str)

        self.root_path: str = root_path
        self.rel_path: str = rel_path if rel_path != "." else ""
        self.folder_name: str = os.path.basename(os.path.normpath(root_path))
        self.level = level
        self.files: List[File] = []
        self.subfolder_trees: List[Folder] = []
        self.parent_folder: Optional[Folder] = None
        self.has_sdoc_content = False

    def __repr__(self):
        return f"Folder: (root_path: {self.root_path}, files: {self.files})"

    def is_folder(self):
        return True

    def get_full_path(self):
        return self.root_path

    def get_level(self):
        return self.level

    def mount_folder(self):
        return os.path.basename(self.root_path)

    def set(self, files):
        for file in files:
            full_file_path = os.path.join(self.root_path, file)
            rel_file_path = os.path.join(self.rel_path, file)
            self.files.append(
                File(self.level + 1, full_file_path, rel_file_path)
            )

    def add_subfolder_tree(self, subfolder_tree):
        assert isinstance(subfolder_tree, Folder)
        self.subfolder_trees.append(subfolder_tree)

    def set_parent_folder(self, parent_folder):
        assert isinstance(parent_folder, Folder)
        self.parent_folder = parent_folder


class FileTree:
    def __init__(self, *, root_folder_or_file):
        self.root_folder_or_file = root_folder_or_file

    @staticmethod
    def create_single_file_tree(root_path):
        single_file = File(0, root_path, "")
        return FileTree(root_folder_or_file=single_file)

    def iterate(self):
        file_tree_mount_folder = self.root_folder_or_file.mount_folder()

        task_list = [self.root_folder_or_file]
        while len(task_list) > 0:
            current_tree = task_list.pop(0)

            for doc_file in current_tree.files:
                yield self.root_folder_or_file, doc_file, file_tree_mount_folder

            task_list.extend(current_tree.subfolder_trees)

    def iterate_directories(self):
        task_list = collections.deque([self.root_folder_or_file])
        while task_list:
            file_tree_or_file = task_list.popleft()
            if isinstance(file_tree_or_file, File):
                yield file_tree_or_file
            elif isinstance(file_tree_or_file, Folder):
                if not file_tree_or_file.has_sdoc_content:
                    continue
                yield file_tree_or_file
                task_list.extendleft(reversed(file_tree_or_file.files))
                task_list.extendleft(
                    reversed(file_tree_or_file.subfolder_trees)
                )

    def __str__(self):
        dump = ""
        for file_or_tree in self.iterate():
            dump += str(file_or_tree)
            dump += "\n"
        return dump

    def __repr__(self):
        return self.__str__()


class FileFinder:
    @staticmethod
    def find_files_with_extensions(
        *,
        root_path: str,
        ignored_dirs: List[str],
        extensions: List[str],
        include_paths: List[str],
        exclude_paths: List[str],
    ):
        assert os.path.isdir(root_path)
        assert os.path.isabs(root_path)
        assert isinstance(extensions, list), extensions

        extensions_tuple = tuple(extensions)
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

            dirs[:] = [
                d
                for d in dirs
                if (not d.startswith(".") and not d.startswith("_"))
            ]
            dirs.sort(key=alphanumeric_sort)

            rel_path = os.path.relpath(current_root_path, start=root_path)
            rel_path = rel_path if rel_path != "." else ""

            current_root_path_level: int = (
                current_root_path.count(os.sep) - root_level
            )

            current_tree = folder_map.setdefault(
                current_root_path,
                Folder(current_root_path, rel_path, current_root_path_level),
            )

            for file in files:
                if not file.endswith(extensions_tuple):
                    continue
                full_file_path = os.path.join(current_root_path, file)
                rel_file_path = os.path.join(rel_path, file)

                if path_filter_excludes.match(rel_file_path):
                    continue

                if path_filter_includes.match(rel_file_path):
                    current_tree.files.append(
                        File(
                            current_tree.level + 1,
                            full_file_path,
                            rel_file_path,
                        )
                    )

            def file_path_sort_key(lhs: File, rhs: File):
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

            # top-down search assumes we have seen the parent before.
            assert current_parent_path in folder_map

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
    def find_directories(root_path, directory):
        assert os.path.isdir(root_path)
        assert os.path.isabs(root_path)
        directories = []
        for current_root_path, dirs, _ in os.walk(root_path, topdown=True):
            dirs[:] = [
                d
                for d in dirs
                if not d.startswith(".")
                and d != "output"
                and d != "Output"
                and d != "tests"
            ]
            if os.path.basename(current_root_path) == directory:
                directories.append(current_root_path)
        return directories
