from typing import Optional, List

from strictdoc.backend.sdoc.models.node import Node
from strictdoc.core.document_meta import DocumentMeta


class Fragment:  # pylint: disable=too-many-instance-attributes
    def __init__(  # pylint: disable=too-many-arguments
        self,
        uid,
        level: Optional[str],
        title,
        free_texts,
        section_contents: List[Node],
    ):
        self.uid = uid
        self.level: Optional[str] = level
        self.title = title

        self.free_texts = free_texts
        self.section_contents = section_contents

        self.ng_sections = []
        self.ng_level = 0
        self.ng_needs_generation = False
        self.meta: Optional[DocumentMeta] = None

    def __str__(self):
        return (
            f"Fragment("
            f"id: {id(self)}, "
            f"section_contents: {self.section_contents})"
        )

    def __repr__(self):
        return self.__str__()

    def assign_meta(self, meta):
        assert isinstance(meta, DocumentMeta)
        self.meta = meta
