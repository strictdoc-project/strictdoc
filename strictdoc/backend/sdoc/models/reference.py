from typing import Optional

from strictdoc.backend.sdoc.models.type_system import (
    BibEntry,
    FileEntry,
    ReferenceType,
)
from strictdoc.helpers.auto_described import auto_described


@auto_described
class Reference:
    def __init__(self, ref_type, parent):
        self.parent = parent
        self.ref_type = ref_type


@auto_described
class FileReference(Reference):
    def __init__(self, parent, g_file_entry: FileEntry):
        super().__init__(ReferenceType.FILE, parent)
        self.g_file_entry: FileEntry = g_file_entry

    def get_posix_path(self) -> str:
        return self.g_file_entry.file_path_posix

    def get_file_format(self) -> Optional[str]:
        return self.g_file_entry.g_file_format


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
