from typing import Optional, List

from strictdoc.backend.sdoc.models.node import Node


class SectionContext:
    def __init__(self):
        self.title_number_string = None


class Section(Node):  # pylint: disable=too-many-instance-attributes
    def __init__(  # pylint: disable=too-many-arguments
        self,
        parent,
        uid,
        level: Optional[str],
        title,
        free_texts,
        section_contents: List[Node],
    ):
        self.parent = parent
        self.uid = uid
        self.level: Optional[str] = level
        self.title = title

        self.free_texts = free_texts
        self.section_contents = section_contents

        self.ng_level = None
        self.ng_sections = []
        self.ng_has_requirements = False
        self.ng_document_reference = None
        self.context = SectionContext()

    def __str__(self):
        return f"Section(level: {self.ng_level}, title: {self.title})"

    def __repr__(self):
        return self.__str__()

    @property
    def document(self):
        return self.ng_document_reference.get_document()

    @property
    def is_requirement(self):
        return False

    @property
    def is_composite_requirement(self):
        return False

    @property
    def is_section(self):
        return True


class FreeText:
    def __init__(self, parent, parts: List):
        assert isinstance(parts, list)
        self.parent = parent
        self.parts = parts
        self.ng_level = None

    def __str__(self):
        return f"FreeText(parts={self.parts})"

    def __repr__(self):
        return self.__str__()

    @property
    def is_requirement(self):
        return False

    @property
    def is_section(self):
        return False
