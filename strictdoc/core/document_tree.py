class FileTree:
    def __init__(self, level=0):
        self.level = level
        self.root_path = None
        self.files = None
        self.subfolder_trees = []

    def __repr__(self):
        return "FileTree: {} files: {}".format(self.root_path, self.files)

    def set(self, root_path, files, subfolders):
        assert not self.root_path

        self.root_path = root_path
        self.files = files

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
