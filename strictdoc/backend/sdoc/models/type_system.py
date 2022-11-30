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
    TYPE_VALUE = "TypeValue"


class ReferenceType:
    PARENT = "Parent"
    FILE = "File"


class GrammarElementField:
    def __init__(self):
        self.title: str = ""
        self.required: bool = False


class GrammarElementFieldString(GrammarElementField):
    def __init__(self, parent, title: str, required: str):
        super().__init__()
        self.parent = parent
        self.title: str = title
        self.required: bool = required == "True"

    def __str__(self):
        return (
            "GrammarElementFieldString("
            f"parent: {self.parent}, "
            f"title: {self.title}, "
            f"required: {self.required}"
            ")"
        )


class GrammarElementFieldSingleChoice(GrammarElementField):
    def __init__(self, parent, title: str, options: List[str], required: str):
        super().__init__()
        self.parent = parent
        self.title: str = title
        self.options: List[str] = options
        self.required: bool = required == "True"


class GrammarElementFieldMultipleChoice(GrammarElementField):
    def __init__(self, parent, title: str, options: List[str], required: str):
        super().__init__()
        self.parent = parent
        self.title: str = title
        self.options: List[str] = options
        self.required: bool = required == "True"


class GrammarElementFieldTag(GrammarElementField):
    def __init__(self, parent, title: str, required: str):
        super().__init__()
        self.parent = parent
        self.title: str = title
        self.required: bool = required == "True"
