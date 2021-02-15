class Reference(object):
    def __init__(self, parent, ref_type, path):
        self.parent = parent
        self.ref_type = ref_type
        self.path = path.strip()

    def __str__(self):
        return "Reference: <ref_type = {}, path = {}>".format(
            self.ref_type, self.path
        )

    def __repr__(self):
        return self.__str__()


class FileReference(Reference):
    def __init__(self, parent, ref_type, path):
        super(FileReference, self).__init__(parent, ref_type, path)


class ParentReqReference(Reference):
    def __init__(self, parent, ref_type, path):
        super(ParentReqReference, self).__init__(parent, ref_type, path)
