import os

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
        return "File: {}".format(self.full_path)

    def is_folder(self):
        return False

    def get_full_path(self):
        return self.full_path

    def get_level(self):
        return self.level

    def get_file_name(self):
        return os.path.basename(self.full_path)

    def mount_folder(self):
        return os.path.basename(os.path.dirname(self.root_path))


class FileTree(FileOrFolderEntry):
    def __init__(self, root_path, level):
        assert os.path.isdir(root_path)
        assert os.path.isabs(root_path)

        self.root_path = root_path
        self.level = level
        self.files = []
        self.subfolder_trees = []
        self.parent_tree = None
        self.has_sdoc_content = False

    def __repr__(self):
        return "FileTree: (root_path: {}, files: {})".format(
            self.root_path, self.files
        )

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
        assert isinstance(subfolder_tree, FileTree)
        self.subfolder_trees.append(subfolder_tree)

    def sort_subfolder_trees(self):
        self.subfolder_trees.sort(key=lambda subfolder: subfolder.root_path)

    def dump(self):
        print(self)
        for subfolder in self.subfolder_trees:
            subfolder.dump()

    def set_parent_tree(self, parent_tree):
        assert isinstance(parent_tree, FileTree)
        self.parent_tree = parent_tree


class FileTreeStructure:
    def __init__(self, root_file_tree):
        self.root_file_tree = root_file_tree

    @staticmethod
    def create_single_file(root_path):
        single_file = File(0, root_path)
        return FileTreeStructure(single_file)

    def iterate(self):
        file_tree_mount_folder = self.root_file_tree.mount_folder()

        task_list = [self.root_file_tree]
        while len(task_list) > 0:
            current_tree = task_list.pop(0)

            for doc_file in current_tree.files:
                yield self.root_file_tree, doc_file, file_tree_mount_folder

            task_list.extend(current_tree.subfolder_trees)


class FileFinder:
    @staticmethod
    def find_files(root_path):
        assert os.path.isdir(root_path)
        assert os.path.isabs(root_path)

        root_level = root_path.count(os.sep)

        root_tree = FileTree(root_path, 0)
        tree_map = {root_path: root_tree}

        for current_root_path, dirs, files in os.walk(root_path, topdown=True):
            dirs[:] = [
                d
                for d in dirs
                if not d.startswith(".") and not d.startswith("_")
            ]
            dirs.sort(key=alphanumeric_sort)

            current_root_path_level = (
                current_root_path.count(os.sep) - root_level
            )

            if current_root_path not in tree_map:
                tree_map[current_root_path] = FileTree(
                    current_root_path, current_root_path_level
                )
            current_tree = tree_map[current_root_path]

            files = [f for f in files if f.endswith(".sdoc")]
            files.sort(key=alphanumeric_sort)
            current_tree.set(files)
            if len(files) > 0:
                current_tree.has_sdoc_content = True

            if current_root_path == root_path:
                continue

            current_parent_path = os.path.dirname(current_root_path)

            # top-down search assumes we have seen the parent before.
            assert current_parent_path in tree_map

            current_parent_tree = tree_map[current_parent_path]
            current_tree.set_parent_tree(current_parent_tree)
            if current_tree.has_sdoc_content:
                current_parent_cursor = current_parent_tree
                while (
                    current_parent_cursor
                    and not current_parent_cursor.has_sdoc_content
                ):
                    current_parent_cursor.has_sdoc_content = True
                    current_parent_cursor = current_parent_cursor.parent_tree

            current_parent_tree.add_subfolder_tree(current_tree)

        file_tree_structure = FileTreeStructure(tree_map[root_path])
        return file_tree_structure


class PathFinder:
    @staticmethod
    def find_directories(root_path, directory):
        assert os.path.isdir(root_path)
        assert os.path.isabs(root_path)
        directories = []
        for current_root_path, dirs, files in os.walk(root_path, topdown=True):
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            if os.path.basename(current_root_path) == directory:
                directories.append(current_root_path)
        return directories
