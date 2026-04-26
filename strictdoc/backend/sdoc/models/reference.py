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
        function: Optional[str] = None,
        clazz: Optional[str] = None,
        element: Optional[str] = None,
        id: Optional[str] = None,  # noqa: A002
        hash: Optional[str] = None,  # noqa: A002
    ):
        self.parent = parent

        # Default: FileEntryFormat.SOURCECODE  # noqa: ERA001
        self.g_file_format: Optional[str] = g_file_format

        # TODO: Might be worth to prohibit the use of Windows paths altogether.
        self.g_file_path: str = g_file_path
        file_path_posix = g_file_path.replace("\\", "/")
        self.file_path_posix = file_path_posix

        # The textX parser passes an empty string even if there is no LINE_RANGE
        # provided in the SDoc source.
        g_line_range = (
            g_line_range
            if g_line_range is not None and len(g_line_range) > 0
            else None
        )

        self.g_line_range: Optional[str] = g_line_range
        self.line_range: Optional[Tuple[int, int]] = None
        if g_line_range is not None:
            range_components_str = g_line_range.split(", ")
            assert len(range_components_str) == 2, range_components_str
            self.line_range = (
                int(range_components_str[0]),
                int(range_components_str[1]),
            )

        # Ad-hoc conversion from legacy SDoc FUNCTION/CLASS fields to new element/id for backward compatibility.
        _function = (
            function if function is not None and len(function) > 0 else None
        )
        _clazz = clazz if clazz is not None and len(clazz) > 0 else None

        _id = id if id is not None and len(id) > 0 else None
        if element is not None:
            self.element: Optional[str] = element if len(element) > 0 else None
            self.id: Optional[str] = _id
        elif _function is not None:
            self.element = "function"
            self.id = _function
        elif _clazz is not None:
            self.element = "class"
            self.id = _clazz
        else:
            self.element = None
            self.id = _id

        # Placeholder for drift-detection hash (no runtime functionality yet).
        self.hash: Optional[str] = (
            hash if hash is not None and len(hash) > 0 else None
        )

    def __setattr__(self, name: str, value: Union[str, Any]) -> None:
        # Ignore legacy function and clazz from textX post-init. The attributes are already converted to
        # during __init__.
        if name in ("function", "clazz"):
            return
        object.__setattr__(self, name, value)

    def __getattr__(self, name: str) -> Optional[str]:
        # Handle ad-hoc conversion of element / id to legacy function / clazz.
        if name == "function":
            element = object.__getattribute__(self, "element")
            id_ = object.__getattribute__(self, "id")
            return id_ if element == "function" else None
        if name == "clazz":
            element = object.__getattribute__(self, "element")
            id_ = object.__getattribute__(self, "id")
            return id_ if element == "class" else None
        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{name}'"
        )


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
