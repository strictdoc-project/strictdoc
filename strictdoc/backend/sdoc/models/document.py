import uuid
from typing import List, Optional

from strictdoc.backend.sdoc.models.document_config import DocumentConfig
from strictdoc.backend.sdoc.models.document_grammar import DocumentGrammar
from strictdoc.backend.sdoc.models.free_text import FreeText
from strictdoc.core.document_meta import DocumentMeta
from strictdoc.helpers.auto_described import auto_described


@auto_described
class Document:  # pylint: disable=too-many-instance-attributes
    def __init__(  # pylint: disable=too-many-arguments
        self,
        title: str,
        config: Optional[DocumentConfig],
        grammar: Optional[DocumentGrammar],
        free_texts: List[FreeText],
        section_contents,
    ):
        assert isinstance(free_texts, list)

        self.title: str = title
        self.config = config if config else DocumentConfig.default_config(self)
        self.grammar: Optional[DocumentGrammar] = grammar
        self.free_texts: List[FreeText] = free_texts
        self.section_contents = section_contents

        self.ng_level: int = 0
        self.ng_needs_generation = False
        self.meta: Optional[DocumentMeta] = None
        self.node_id = uuid.uuid4().hex

    def assign_meta(self, meta):
        assert isinstance(meta, DocumentMeta)
        self.meta = meta

    def has_any_nodes(self) -> bool:
        return len(self.section_contents) > 0

    def has_any_requirements(self) -> bool:
        task_list = list(self.section_contents)
        while len(task_list) > 0:
            section_or_requirement = task_list.pop(0)
            if section_or_requirement.is_requirement:
                return True
            assert section_or_requirement.is_section, section_or_requirement
            task_list.extend(section_or_requirement.section_contents)
        return False

    @staticmethod
    def get_type_string() -> str:
        return "document"

    @property
    def ng_resolved_custom_level(self):
        return None

    def enumerate_meta_field_titles(self):
        # TODO: currently only enumerating a single element ([0])
        yield from self.grammar.elements[0].enumerate_meta_field_titles()

    def enumerate_custom_content_field_titles(self):
        # TODO: currently only enumerating a single element ([0])
        yield from self.grammar.elements[
            0
        ].enumerate_custom_content_field_titles()

    def set_freetext(self, freetext: Optional[FreeText]):
        if freetext is None:
            self.free_texts = []
            return
        self.free_texts = [freetext]
