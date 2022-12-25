import uuid
from typing import Optional

from strictdoc.backend.sdoc.models.document_config import DocumentConfig
from strictdoc.backend.sdoc.models.document_grammar import DocumentGrammar
from strictdoc.core.document_meta import DocumentMeta
from strictdoc.helpers.auto_described import auto_described


@auto_described
class Document:  # pylint: disable=too-many-instance-attributes
    def __init__(  # pylint: disable=too-many-arguments
        self,
        title,
        config: Optional[DocumentConfig],
        grammar: Optional[DocumentGrammar],
        free_texts,
        section_contents,
    ):
        assert isinstance(free_texts, list)

        self.title = title
        self.config = config if config else DocumentConfig.default_config(self)
        self.grammar: Optional[DocumentGrammar] = grammar
        self.free_texts = free_texts
        self.section_contents = section_contents

        self.ng_level: int = 0
        self.ng_needs_generation = False
        self.meta: Optional[DocumentMeta] = None
        self.node_id = uuid.uuid4().hex

    def assign_meta(self, meta):
        assert isinstance(meta, DocumentMeta)
        self.meta = meta

    @property
    def level(self):
        return None

    def enumerate_meta_field_titles(self):
        # TODO: currently only enumerating a single element ([0])
        for field_title in self.grammar.elements[
            0
        ].enumerate_meta_field_titles():
            yield field_title

    def enumerate_custom_content_field_titles(self):
        # TODO: currently only enumerating a single element ([0])
        for field_title in self.grammar.elements[
            0
        ].enumerate_custom_content_field_titles():
            yield field_title
