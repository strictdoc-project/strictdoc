"""
@relation(SDOC-SRS-31, SDOC-SRS-101, scope=file)
"""

from typing import Any, Optional, Tuple, Union

from strictdoc.backend.sdoc.models.grammar_element import ReferenceType
from strictdoc.helpers.auto_described import auto_described
from strictdoc.helpers.mid import MID


@auto_described
class FileEntry:
    def __init__(
        self,
        parent: Any,
        g_file_format: Optional[str],
        g_file_path: str,
        g_line_range: Optional[str],
        g_deprecated_file_path: Optional[str] = None,
        function: Optional[str] = None,
        clazz: Optional[str] = None,
        element: Optional[str] = None,
        id: Optional[str] = None,  # noqa: A002
        hash: Optional[str] = None,  # noqa: A002
    ):
        self.parent = parent

        # Default: FileEntryFormat.SOURCECODE  # noqa: ERA001
        self.g_file_format: Optional[str] = g_file_format
        self.g_deprecated_file_path: Optional[str] = None

        if (
            g_deprecated_file_path is not None
            and len(g_deprecated_file_path) > 0
        ):
            g_file_path = g_deprecated_file_path
            self.g_deprecated_file_path = g_deprecated_file_path

        # TODO: Might be worth to prohibit the use of Windows paths altogether.
        self.g_file_path: str = g_file_path
        file_path_posix = g_file_path.replace("\\", "/")
        self.file_path_posix = file_path_posix

        #
        # For optional string fields:
        # The textX parser passes an empty string even if there is no field
        # present in the input. We want to convert such empty strings to None
        # for better semantics and easier handling in the rest of the code.
        #
        g_line_range = (
            g_line_range
            if g_line_range is not None and len(g_line_range) > 0
            else None
        )
        self.deprecated_function = (
            function if function is not None and len(function) > 0 else None
        )
        self.deprecated_clazz = (
            clazz if clazz is not None and len(clazz) > 0 else None
        )
        _id = id if id is not None and len(id) > 0 else None
        element = element if element is not None and len(element) > 0 else None
        _hash = hash if hash is not None and len(hash) > 0 else None

        self.g_line_range: Optional[str] = g_line_range
        self.line_range: Optional[Tuple[int, int]] = None
        if g_line_range is not None:
            range_components_str = g_line_range.split(", ")
            assert len(range_components_str) == 2, range_components_str
            self.line_range = (
                int(range_components_str[0]),
                int(range_components_str[1]),
            )

        self.id: Optional[str] = _id
        if element is not None:
            self.element: Optional[str] = element
        elif self.deprecated_function is not None:
            self.element = "function"
            self.id = self.deprecated_function
        elif self.deprecated_clazz is not None:
            self.element = "class"
            self.id = self.deprecated_clazz
        else:
            self.element = None

        # Placeholder for drift-detection hash (no runtime functionality yet).
        self.hash: Optional[str] = _hash

    def __setattr__(self, name: str, value: Union[str, Any]) -> None:
        # Ignore legacy function and clazz from textX post-init. The attributes are already converted to
        # during __init__.
        if name in ("function", "clazz"):
            return
        object.__setattr__(self, name, value)

    def function(self) -> Optional[str]:
        if self.deprecated_function is not None:
            return self.deprecated_function

        if self.element == "function":
            return self.id

        return None

    def clazz(self) -> Optional[str]:
        if self.deprecated_clazz is not None:
            return self.deprecated_clazz

        if self.element == "class":
            return self.id

        return None


class FileEntryFormat:
    SOURCECODE = "Sourcecode"
    PYTHON = "Python"


@auto_described
class Reference:
    def __init__(self, ref_type: str, parent: Any):
        self.parent = parent
        self.ref_type: str = ref_type
        self.role: Optional[str] = None


@auto_described
class FileReference(Reference):
    """
    @relation(SDOC-SRS-145, scope=function)
    """

    def __init__(
        self, parent: Any, g_file_entry: FileEntry, role: Optional[str] = None
    ):
        super().__init__(ReferenceType.FILE, parent)
        self.g_file_entry: FileEntry = g_file_entry
        self.role: Optional[str] = (
            role if role is not None and len(role) > 0 else None
        )
        self.mid = MID.create()

    def get_posix_path(self) -> str:
        return self.g_file_entry.file_path_posix

    def get_file_format(self) -> Optional[str]:
        return self.g_file_entry.g_file_format


@auto_described
class ParentReqReference(Reference):
    def __init__(self, parent: Any, ref_uid: str, role: Optional[str]):
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
    def __init__(self, parent: Any, ref_uid: str, role: str):
        super().__init__(ReferenceType.CHILD, parent)
        self.ref_uid = ref_uid
        # When ROLE: field is not provided for a child reference, the
        # textX still passes relation_uid as an empty string (instead of None
        # as one could expect).
        self.role: Optional[str] = (
            role if role is not None and len(role) > 0 else None
        )
        self.mid = MID.create()
