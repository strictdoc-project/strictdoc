import os


class FileOrFolderEntry:
    def get_full_path(self):
        raise NotImplementedError

    def get_level(self):
        raise NotImplementedError


class File(FileOrFolderEntry):
    def __init__(self, level, full_path):
        assert os.path.isfile(full_path)
        self.level = level
        self.full_path = full_path

    def get_full_path(self):
        return self.full_path

    def get_level(self):
        return self.level


class FileTree(FileOrFolderEntry):
    def __init__(self, level=0):
        self.level = level
        self.root_path = None
        self.files = []
        self.subfolder_trees = []

    def __repr__(self):
        return "FileTree: {} files: {}".format(self.root_path, self.files)

    def get_full_path(self):
        return self.root_path

    def get_level(self):
        return self.level

    def get_folder_name(self):
        return os.path.basename(os.path.normpath(self.root_path))

    def set(self, root_path, files, subfolders):
        assert os.path.isdir(root_path)

        self.root_path = root_path
        for file in files:
            full_file_path = os.path.join(self.root_path, file)
            self.files.append(File(self.level + 1, full_file_path))

        for _ in subfolders:
            self.subfolder_trees.append(FileTree(self.level + 1))

    def dump(self):
        print(self)
        for subfolder in self.subfolder_trees:
            subfolder.dump()


class DocumentTree:
    def __init__(self, file_tree, document_list, document_map):
        assert isinstance(file_tree, FileTree)
        assert isinstance(document_list, list)
        assert isinstance(document_map, dict)
        self.file_tree = file_tree
        self.document_list = document_list
        self.document_map = document_map

    def __repr__(self):
        return "DocumentTree: {} document_list: {}".format(self.file_tree, self.document_list)
