from typing import List


class GrammarElementField:
    pass


class GrammarElementFieldString(GrammarElementField):
    def __init__(self, parent, title: str, field_type: str, required: str):
        self.parent = parent
        self.title: str = title
        self.field_type: str = field_type
        self.required: bool = required == "True"


class GrammarElementFieldSingleChoice(GrammarElementField):
    def __init__(  # pylint: disable=too-many-arguments
        self,
        parent,
        title: str,
        field_type: str,
        options: List[str],
        required: str,
    ):
        self.parent = parent
        self.title: str = title
        self.field_type: str = field_type
        self.options: List[str] = options
        self.required: bool = required == "True"


class GrammarElementFieldMultipleChoice(GrammarElementField):
    def __init__(  # pylint: disable=too-many-arguments
        self,
        parent,
        title: str,
        field_type: str,
        options: List[str],
        required: str,
    ):
        self.parent = parent
        self.title: str = title
        self.field_type: str = field_type
        self.options: List[str] = options
        self.required: bool = required == "True"


class GrammarElementFieldTag(GrammarElementField):
    def __init__(self, parent, title: str, field_type: str, required: str):
        self.parent = parent
        self.title: str = title
        self.field_type: str = field_type
        self.required: bool = required == "True"
