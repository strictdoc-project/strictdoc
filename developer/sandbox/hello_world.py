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

# Python3 program to add two numbers

number1 = input("First number: ")
number2 = input("\nSecond number: ")

# STRICTDOC RANGE BEGIN: REQ-FILE-REF, REQ-FILE-REF2
# Adding two numbers
# User might also enter float numbers
sum = float(number1) + float(number2)
# STRICTDOC RANGE END: REQ-FILE-REF, REQ-FILE-REF2

# Display the sum
# will print value in float
# STRICTDOC RANGE BEGIN: REQ-FILE-REF, REQ-FILE-REF2
print("The sum of {0} and {1} is {2}".format(number1, number2, sum))
# STRICTDOC RANGE END: REQ-FILE-REF, REQ-FILE-REF2

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

    # STRICTDOC RANGE BEGIN: REQ-FILE-REF2
    print("The sum of {0} and {1} is {2}".format(number1, number2, sum))
    # STRICTDOC RANGE END: REQ-FILE-REF2
