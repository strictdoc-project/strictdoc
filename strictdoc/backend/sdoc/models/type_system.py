# mypy: disable-error-code="no-redef,no-untyped-call,no-untyped-def"
from typing import List, Optional, Tuple

from strictdoc.helpers.auto_described import auto_described
from strictdoc.helpers.mid import MID


class RequirementFieldName:
    MID = "MID"
    UID = "UID"
    LEVEL = "LEVEL"
    STATUS = "STATUS"
    TAGS = "TAGS"
    TITLE = "TITLE"

    # {STATEMENT, DESCRIPTION, CONTENT} are aliases.
    # It is assumed that either field is provided for each node.
    STATEMENT = "STATEMENT"
    DESCRIPTION = "DESCRIPTION"
    CONTENT = "CONTENT"

    RATIONALE = "RATIONALE"
    COMMENT = "COMMENT"


RESERVED_NON_META_FIELDS = [
    RequirementFieldName.TITLE,
    RequirementFieldName.STATEMENT,
    RequirementFieldName.DESCRIPTION,
    RequirementFieldName.CONTENT,
    RequirementFieldName.COMMENT,
    RequirementFieldName.RATIONALE,
    RequirementFieldName.LEVEL,
]


class RequirementFieldType:
    STRING = "String"
    SINGLE_CHOICE = "SingleChoice"
    MULTIPLE_CHOICE = "MultipleChoice"
    TAG = "Tag"
    REFERENCE = "Reference"


class GrammarReferenceType:
    PARENT_REQ_REFERENCE = "ParentReqReference"
    CHILD_REQ_REFERENCE = "ChildReqReference"
    FILE_REFERENCE = "FileReference"


@auto_described
class FileEntry:
    def __init__(
        self,
        parent,
        g_file_format: Optional[str],
        g_file_path: str,
        g_line_range: Optional[str],
    ):
        self.parent = parent

        # Default: FileEntryFormat.SOURCECODE  # noqa: ERA001
        self.g_file_format: Optional[str] = g_file_format

        # TODO: Might be worth to prohibit the use of Windows paths altogether.
        self.g_file_path: str = g_file_path
        file_path_posix = g_file_path.replace("\\", "/")
        self.file_path_posix = file_path_posix

        # textX passes an empty string even if there is no LINE_RANGE provided
        # in the SDoc source.
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
            self.line_range: Tuple[int, int] = (
                int(range_components_str[0]),
                int(range_components_str[1]),
            )


class FileEntryFormat:
    SOURCECODE = "Sourcecode"
    PYTHON = "Python"


class ReferenceType:
    PARENT = "Parent"
    CHILD = "Child"
    FILE = "File"

    GRAMMAR_REFERENCE_TYPE_MAP = {
        PARENT: GrammarReferenceType.PARENT_REQ_REFERENCE,
        CHILD: GrammarReferenceType.CHILD_REQ_REFERENCE,
        FILE: GrammarReferenceType.FILE_REFERENCE,
    }


@auto_described
class GrammarElementField:
    def __init__(self):
        self.title: str = ""
        self.human_title: Optional[str] = None
        self.gef_type: str = ""
        self.required: bool = False
        self.mid: MID = MID.create()

    def get_field_human_name(self) -> str:
        if self.human_title is not None:
            return self.human_title
        return self.title


@auto_described
class GrammarElementFieldString(GrammarElementField):
    def __init__(
        self, parent, title: str, human_title: Optional[str], required: str
    ):
        super().__init__()
        self.parent = parent
        self.title: str = title
        self.human_title: Optional[str] = human_title
        self.gef_type = RequirementFieldType.STRING
        self.required: bool = required == "True"
        self.mid: MID = MID.create()


@auto_described
class GrammarElementFieldSingleChoice(GrammarElementField):
    def __init__(
        self,
        parent,
        title: str,
        human_title: Optional[str],
        options: List[str],
        required: str,
    ):
        super().__init__()
        self.parent = parent
        self.title: str = title
        self.human_title: Optional[str] = human_title
        self.gef_type = RequirementFieldType.SINGLE_CHOICE
        self.options: List[str] = options
        self.required: bool = required == "True"
        self.mid: MID = MID.create()


@auto_described
class GrammarElementFieldMultipleChoice(GrammarElementField):
    def __init__(
        self,
        parent,
        title: str,
        human_title: Optional[str],
        options: List[str],
        required: str,
    ):
        super().__init__()
        self.parent = parent
        self.title: str = title
        self.human_title: Optional[str] = human_title
        self.gef_type = RequirementFieldType.MULTIPLE_CHOICE
        self.options: List[str] = options
        self.required: bool = required == "True"
        self.mid: MID = MID.create()


@auto_described
class GrammarElementFieldTag(GrammarElementField):
    def __init__(
        self, parent, title: str, human_title: Optional[str], required: str
    ):
        super().__init__()
        self.parent = parent
        self.title: str = title
        self.human_title: Optional[str] = human_title
        self.gef_type = RequirementFieldType.TAG
        self.required: bool = required == "True"
        self.mid: MID = MID.create()


@auto_described
class GrammarElementRelationParent:
    def __init__(
        self, parent, relation_type: str, relation_role: Optional[str]
    ):
        assert relation_type == "Parent"
        self.parent = parent
        self.relation_type = relation_type
        self.relation_role: Optional[str] = (
            relation_role
            if relation_role is not None and len(relation_role) > 0
            else None
        )
        self.mid: MID = MID.create()

    def __eq__(self, other):
        if not isinstance(other, GrammarElementRelationParent):
            raise NotImplementedError(self, other)
        return (
            self.mid == other.mid
            and self.relation_type == other.relation_type
            and self.relation_role == other.relation_role
        )


@auto_described
class GrammarElementRelationChild:
    def __init__(
        self, parent, relation_type: str, relation_role: Optional[str]
    ):
        assert relation_type == "Child"
        self.parent = parent
        self.relation_type = relation_type
        self.relation_role: Optional[str] = (
            relation_role
            if relation_role is not None and len(relation_role) > 0
            else None
        )
        self.mid: MID = MID.create()


@auto_described
class GrammarElementRelationFile:
    def __init__(self, parent, relation_type: str):
        assert relation_type == "File"
        self.parent = parent
        self.relation_type = relation_type
        self.relation_role: Optional[str] = None
        self.mid: MID = MID.create()


@auto_described
class ViewElementField:
    def __init__(self, parent, name: str, placement: Optional[str]):
        self.parent = parent
        self.name: str = name
        self.placement: Optional[str] = placement


@auto_described
class ViewElementTags:
    def __init__(
        self, parent, object_type: str, visible_fields: List[ViewElementField]
    ):
        self.parent = parent
        self.object_type: str = object_type
        self.visible_fields: List[ViewElementField] = visible_fields


@auto_described
class ViewElementHiddenTag:
    def __init__(self, parent, hidden_tag: str):
        self.parent = parent
        self.hidden_tag: str = hidden_tag
