# mypy: disable-error-code="no-untyped-call,no-untyped-def"
from typing import Optional

from strictdoc.backend.sdoc.models.type_system import (
    FileEntry,
    ReferenceType,
)
from strictdoc.helpers.auto_described import auto_described
from strictdoc.helpers.mid import MID


@auto_described
class Reference:
    def __init__(self, ref_type: str, parent):
        self.parent = parent
        self.ref_type: str = ref_type
        self.role: Optional[str] = None


@auto_described
class FileReference(Reference):
    def __init__(
        self, parent, g_file_entry: FileEntry, role: Optional[str] = None
    ):
        super().__init__(ReferenceType.FILE, parent)
        self.g_file_entry: FileEntry = g_file_entry
        self.role: Optional[str] = (
            role if role is not None and len(role) > 0 else None
        )
        self.mid = MID.create()

    def get_posix_path(self) -> str:
        return self.g_file_entry.file_path_posix

    def get_native_path(self) -> str:
        return self.g_file_entry.g_file_path

    def get_file_format(self) -> Optional[str]:
        return self.g_file_entry.g_file_format


@auto_described
class ParentReqReference(Reference):
    def __init__(self, parent, ref_uid: str, role: Optional[str]):
        super().__init__(ReferenceType.PARENT, parent)
        self.ref_uid: str = ref_uid
        # When ROLE: field is not provided for a parent reference, the
        # textX still passes relation_uid as an empty string (instead of None
        # as one could expect).
        self.role: Optional[str] = (
            role if role is not None and len(role) > 0 else None
        )
        self.mid = MID.create()


@auto_described
class ChildReqReference(Reference):
    def __init__(self, parent, ref_uid, role: str):
        super().__init__(ReferenceType.CHILD, parent)
        self.ref_uid = ref_uid
        # When ROLE: field is not provided for a child reference, the
        # textX still passes relation_uid as an empty string (instead of None
        # as one could expect).
        self.role: Optional[str] = (
            role if role is not None and len(role) > 0 else None
        )
        self.mid = MID.create()
