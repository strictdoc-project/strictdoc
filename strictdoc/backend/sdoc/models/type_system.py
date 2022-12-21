import os
from typing import List, Optional


class RequirementFieldName:
    UID = "UID"
    LEVEL = "LEVEL"
    STATUS = "STATUS"
    TAGS = "TAGS"
    REFS = "REFS"
    TITLE = "TITLE"
    STATEMENT = "STATEMENT"
    RATIONALE = "RATIONALE"
    COMMENT = "COMMENT"


RESERVED_NON_META_FIELDS = [
    RequirementFieldName.REFS,
    RequirementFieldName.TITLE,
    RequirementFieldName.STATEMENT,
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
    FILE_REFERENCE = "FileReference"


class FileEntry:
    def __init__(self, parent, file_format: Optional[str], file_path: str):
        self.parent = parent
        self.file_format = file_format  # Default: FileEntryFormat.SOURCECODE
        self.file_path = file_path

        path_forward_slashes = file_path.replace("\\", "/")
        self.path_forward_slashes = path_forward_slashes
        self.path_normalized = os.path.normpath(path_forward_slashes)

    def __str__(self):
        return (
            f"FileEntry("
            f"parent = {self.parent.__class__.__name__},"
            f" file_format = {self.file_format},"
            f" file_path = {self.file_path},"
            f" path_forward_slashes = {self.path_forward_slashes},"
            f" path_normalized = {self.path_normalized})"
        )


class FileEntryFormat:
    SOURCECODE = "Sourcecode"
    PYTHON = "Python"


class ReferenceType:
    PARENT = "Parent"
    FILE = "File"

    GRAMMAR_REFERENCE_TYPE_MAP = {
        PARENT: GrammarReferenceType.PARENT_REQ_REFERENCE,
        FILE: GrammarReferenceType.FILE_REFERENCE,
    }


class GrammarElementField:
    def __init__(self):
        self.title: str = ""
        self.gef_type: str = ""
        self.required: bool = False


class GrammarElementFieldString(GrammarElementField):
    def __init__(self, parent, title: str, required: str):
        super().__init__()
        self.parent = parent
        self.title: str = title
        self.gef_type = RequirementFieldType.STRING
        self.required: bool = required == "True"

    def __str__(self):
        return (
            "GrammarElementFieldString("
            f"parent: {self.parent}, "
            f"title: {self.title}, "
            f"gef_type: {self.gef_type}, "
            f"required: {self.required}"
            ")"
        )


class GrammarElementFieldSingleChoice(GrammarElementField):
    def __init__(self, parent, title: str, options: List[str], required: str):
        super().__init__()
        self.parent = parent
        self.title: str = title
        self.gef_type = RequirementFieldType.SINGLE_CHOICE
        self.options: List[str] = options
        self.required: bool = required == "True"

    def __str__(self):
        return (
            "GrammarElementFieldSingleChoice("
            f"parent: {self.parent}, "
            f"title: {self.title}, "
            f"gef_type: {self.gef_type}({', '.join(self.options)}), "
            f"required: {self.required}"
            ")"
        )


class GrammarElementFieldMultipleChoice(GrammarElementField):
    def __init__(self, parent, title: str, options: List[str], required: str):
        super().__init__()
        self.parent = parent
        self.title: str = title
        self.gef_type = RequirementFieldType.MULTIPLE_CHOICE
        self.options: List[str] = options
        self.required: bool = required == "True"

    def __str__(self):
        return (
            "GrammarElementFieldMultipleChoice("
            f"parent: {self.parent}, "
            f"title: {self.title}, "
            f"gef_type: {self.gef_type}({', '.join(self.options)}), "
            f"required: {self.required}"
            ")"
        )


class GrammarElementFieldTag(GrammarElementField):
    def __init__(self, parent, title: str, required: str):
        super().__init__()
        self.parent = parent
        self.title: str = title
        self.gef_type = RequirementFieldType.TAG
        self.required: bool = required == "True"

    def __str__(self):
        return (
            "GrammarElementFieldTag("
            f"parent: {self.parent}, "
            f"title: {self.title}, "
            f"gef_type: {self.gef_type}, "
            f"required: {self.required}"
            ")"
        )


class GrammarElementFieldReference(GrammarElementField):
    def __init__(self, parent, title: str, types: List[str], required: str):
        super().__init__()
        self.parent = parent
        self.gef_type = RequirementFieldType.REFERENCE
        self.title: str = title
        self.types: List[str] = types
        self.required: bool = required == "True"

    def __str__(self):
        return (
            "GrammarElementFieldReference("
            f"parent: {self.parent}, "
            f"title: {self.title}, "
            f"gef_type: {self.gef_type}({', '.join(self.types)}), "
            f"required: {self.required}"
            ")"
        )
