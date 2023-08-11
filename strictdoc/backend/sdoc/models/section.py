from typing import List, Optional, Union

from strictdoc.backend.sdoc.document_reference import DocumentReference
from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.models.free_text import FreeText
from strictdoc.backend.sdoc.models.node import Node
from strictdoc.helpers.auto_described import auto_described
from strictdoc.helpers.mid import MID


@auto_described
class SectionContext:
    def __init__(self):
        self.title_number_string = None


@auto_described
class Section(Node):  # pylint: disable=too-many-instance-attributes
    def __init__(  # pylint: disable=too-many-arguments
        self,
        parent,
        uid,
        custom_level: Optional[str],
        title,
        requirement_prefix: Optional[str],
        free_texts: List[FreeText],
        section_contents: List[Node],
    ):
        self.parent = parent

        # TODO: Remove .uid, keep reserved_uid only.
        meaningful_uid: Optional[str] = None
        if uid is not None and len(uid) > 0:
            meaningful_uid = uid
        self.uid: Optional[str] = meaningful_uid
        self.reserved_uid: Optional[str] = meaningful_uid

        self.title = title
        self.requirement_prefix: Optional[str] = requirement_prefix

        self.free_texts: List[FreeText] = free_texts
        self.section_contents = section_contents

        # HEF4
        self.custom_level: Optional[str] = custom_level
        self.ng_resolved_custom_level: Optional[str] = custom_level

        self.ng_level: Optional[int] = None
        self.ng_has_requirements = False
        self.ng_document_reference: Optional[DocumentReference] = None
        self.context = SectionContext()
        self.mid: MID = MID.create()

    @staticmethod
    def get_type_string() -> str:
        return "section"

    def get_title(self):
        return self.title

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

    def get_requirement_prefix(self) -> str:
        if self.requirement_prefix is not None:
            return self.requirement_prefix
        parent: Union[Section, Document] = self.parent
        return parent.get_requirement_prefix()
