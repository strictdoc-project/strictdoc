# mypy: disable-error-code="no-untyped-def"
from strictdoc.core.file_tree import File


class SourceTree:
    def __init__(self, file_tree, source_files, map_file_to_source):
        self.file_tree = file_tree
        self.source_files = source_files
        self.map_file_to_source = map_file_to_source

    def get_source_for_file(self, file):
        assert isinstance(file, File)
        return self.map_file_to_source[file]
