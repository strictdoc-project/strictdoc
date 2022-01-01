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
    pass


class ParentReqReference(Reference):
    pass
