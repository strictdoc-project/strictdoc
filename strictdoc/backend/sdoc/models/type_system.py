from typing import List


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
