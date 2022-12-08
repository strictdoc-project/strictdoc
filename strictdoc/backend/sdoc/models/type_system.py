from typing import List


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
