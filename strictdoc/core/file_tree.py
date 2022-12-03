import collections
import os
from typing import Dict, Optional, Set, List

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
    def __init__(self, level, full_path):
        assert os.path.isfile(full_path)
        assert os.path.isabs(full_path)
        self.level = level
        self.full_path = full_path
        self.root_path = full_path
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
        return os.path.basename(self.full_path)

    def get_folder_path(self) -> str:
        return os.path.dirname(self.full_path)

    def mount_folder(self) -> str:
        return os.path.basename(os.path.dirname(self.root_path))


class Folder(FileOrFolderEntry):
    def __init__(self, root_path, level):
        assert os.path.isdir(root_path)
        assert os.path.isabs(root_path)

        self.root_path = root_path
        self.level = level
        self.files = []
        self.subfolder_trees = []
        self.parent_folder = None
        self.has_sdoc_content = False

    def __repr__(self):
        return f"Folder: (root_path: {self.root_path}, files: {self.files})"

    def is_folder(self):
        return True

    def get_full_path(self):
        return self.root_path

    def get_level(self):
        return self.level

    def get_folder_name(self):
        return os.path.basename(os.path.normpath(self.root_path))

    def mount_folder(self):
        return os.path.basename(self.root_path)

    def set(self, files):
        for file in files:
            full_file_path = os.path.join(self.root_path, file)
            self.files.append(File(self.level + 1, full_file_path))

    def add_subfolder_tree(self, subfolder_tree):
        assert isinstance(subfolder_tree, Folder)
        self.subfolder_trees.append(subfolder_tree)

    def set_parent_folder(self, parent_folder):
        assert isinstance(parent_folder, Folder)
        self.parent_folder = parent_folder

    def dump(self):
        print(self)
        for subfolder in self.subfolder_trees:
            subfolder.dump()


class FileTree:
    def __init__(self, *, root_folder_or_file):
        self.root_folder_or_file = root_folder_or_file

    @staticmethod
    def create_single_file_tree(root_path):
        single_file = File(0, root_path)
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
        *, root_path: str, ignored_dirs: List[str], extensions: Set[str]
    ):
        assert os.path.isdir(root_path)
        assert os.path.isabs(root_path)
        assert isinstance(extensions, set)

        root_level: int = root_path.count(os.sep)

        root_folder: Folder = Folder(root_path, 0)
        folder_map: Dict[str, Folder] = {root_path: root_folder}

        for current_root_path, dirs, files in os.walk(root_path, topdown=True):
            if current_root_path in ignored_dirs:
                dirs[:] = []
                continue

            dirs[:] = [
                d
                for d in dirs
                if (
                    not d.startswith(".")
                    and not d.startswith("_")
                    and "tests" not in d
                    and "integration" not in d
                )
            ]
            dirs.sort(key=alphanumeric_sort)

            current_root_path_level: int = (
                current_root_path.count(os.sep) - root_level
            )

            current_tree = folder_map.setdefault(
                current_root_path,
                Folder(current_root_path, current_root_path_level),
            )

            def filter_source_files(_files):
                _source_files = []
                for file in _files:
                    _, file_extension = os.path.splitext(file)
                    if file_extension in extensions:
                        _source_files.append(file)
                return _source_files

            files = filter_source_files(files)
            files.sort(key=alphanumeric_sort)
            current_tree.set(files)
            if len(files) > 0:
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
