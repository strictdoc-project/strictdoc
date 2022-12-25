from strictdoc.backend.sdoc.models.type_system import (
    ReferenceType,
    BibEntry,
    FileEntry,
)
from strictdoc.helpers.auto_described import auto_described


@auto_described
class Reference:
    def __init__(self, ref_type, parent):
        self.parent = parent
        self.ref_type = ref_type


@auto_described
class FileReference(Reference):
    def __init__(self, parent, file_entry: FileEntry):
        super().__init__(ReferenceType.FILE, parent)
        self.file_entry = file_entry


@auto_described
class ParentReqReference(Reference):
    def __init__(self, parent, ref_uid):
        super().__init__(ReferenceType.PARENT, parent)
        self.ref_uid = ref_uid


@auto_described
class BibReference(Reference):
    def __init__(self, parent, bib_entry: BibEntry):
        super().__init__(ReferenceType.BIB_REF, parent)
        self.bib_entry = bib_entry
        # TODO Add bib_entry into Parent-Root Document.Bibliography
