import os


class FileOrFolderEntry:
    def get_full_path(self):
        raise NotImplementedError

    def get_level(self):
        raise NotImplementedError

    def is_folder(self):
        raise NotImplementedError


class File(FileOrFolderEntry):
    def __init__(self, level, full_path):
        assert os.path.isfile(full_path)
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


class FileTree(FileOrFolderEntry):
    def __init__(self, root_path, level):
        assert os.path.isdir(root_path)
        assert os.path.isabs(root_path)

        self.root_path = root_path
        self.level = level
        self.files = []
        self.subfolder_trees = []
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


class DocumentTree:
    def __init__(self, file_tree, document_list, map_docs_by_paths):
        assert isinstance(file_tree, list)
        assert isinstance(document_list, list)
        assert isinstance(map_docs_by_paths, dict)
        self.file_tree = file_tree
        self.document_list = document_list
        self.map_docs_by_paths = map_docs_by_paths

        self.source_files = None  # attached later.

    def __repr__(self):
        return "DocumentTree: {} document_list: {}".format(
            self.file_tree, self.document_list
        )

    def get_document_by_path(self, doc_full_path):
        document = self.map_docs_by_paths[doc_full_path]
        return document

    def attach_source_files(self, source_files):
        self.source_files = source_files
