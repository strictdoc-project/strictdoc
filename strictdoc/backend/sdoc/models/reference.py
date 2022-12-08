import os


class Reference:
    def __init__(self, parent, ref_type, path):
        self.parent = parent
        self.ref_type = ref_type
        self.path = path.strip()

    def __str__(self):
        return f"Reference(ref_type = {self.ref_type}, path = {self.path})"

    def __repr__(self):
        return self.__str__()


class FileReference(Reference):
    def __init__(self, parent, ref_type, path):
        super().__init__(parent, ref_type, path)
        path_forward_slashes = path.replace("\\", "/")
        self.path_forward_slashes = path_forward_slashes
        self.path_normalized = os.path.normpath(path_forward_slashes)

    def __str__(self):
        return (
            f"FileReference(ref_type = {self.ref_type},"
            f" path = {self.path},"
            f" path_forward_slashes = {self.path_forward_slashes},"
            f" path_normalized = {self.path_normalized})"
        )


class ParentReqReference(Reference):
    pass
