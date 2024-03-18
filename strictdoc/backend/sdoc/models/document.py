from typing import List, Optional

from strictdoc.backend.sdoc.models.document_bibliography import (
    DocumentBibliography,
)
from strictdoc.backend.sdoc.models.document_config import DocumentConfig
from strictdoc.backend.sdoc.models.document_grammar import DocumentGrammar
from strictdoc.backend.sdoc.models.document_view import DocumentView
from strictdoc.backend.sdoc.models.free_text import FreeText
from strictdoc.core.document_meta import DocumentMeta
from strictdoc.helpers.auto_described import auto_described
from strictdoc.helpers.mid import MID


@auto_described
class SDocDocument:  # pylint: disable=too-many-instance-attributes
    def __init__(
        self,
        mid: Optional[str],
        title: str,
        config: Optional[DocumentConfig],
        view: Optional[DocumentView],
        grammar: Optional[DocumentGrammar],
        bibliography: Optional[DocumentBibliography],
        free_texts,
        section_contents,
    ):
        assert isinstance(free_texts, list)

        self.title: str = title
        self.reserved_title: str = title
        self.config: DocumentConfig = (
            config
            if config is not None
            else DocumentConfig.default_config(self)
        )
        self.view: DocumentView = (
            view if view is not None else DocumentView.create_default(self)
        )
        self.grammar: Optional[DocumentGrammar] = grammar
        self.bibliography: Optional[DocumentBibliography] = bibliography
        self.free_texts: List[FreeText] = free_texts
        self.section_contents = section_contents

        # FIXME: Plain list of all fragments found in the document.
        self.fragments_from_files: List = []

        self.ng_level: int = 0
        self.ng_needs_generation = False
        self.ng_uses_old_refs_field: bool = False
        self.ng_at_least_one_relations_field: bool = False

        self.meta: Optional[DocumentMeta] = None

        self.reserved_mid: MID = MID(mid) if mid is not None else MID.create()
        self.mid_permanent: bool = mid is not None
        self.document_is_included: bool = False
        self.included_documents: List["SDocDocument"] = []

        self.ng_including_document_reference: Optional = None

    def document_is_included(self):
        return self.ng_including_document_reference.get_document() is not None

    def get_included_document(self):
        return self.ng_including_document_reference.get_document()

    @property
    def reserved_uid(self) -> Optional[str]:
        return self.config.uid

    def assign_meta(self, meta):
        assert isinstance(meta, DocumentMeta)
        self.meta = meta

    def has_any_nodes(self) -> bool:
        return len(self.section_contents) > 0

    def has_any_toc_nodes(self) -> bool:
        for node_ in self.section_contents:
            if node_.is_section:
                if node_.ng_resolved_custom_level != "None":
                    return True
                # Skip nodes without a TOC level.
                continue
            return True
        return False

    def has_any_requirements(self) -> bool:
        from strictdoc.backend.sdoc.models.document_from_file import (
            FragmentFromFile,
        )

        task_list = list(self.section_contents)
        while len(task_list) > 0:
            section_or_requirement = task_list.pop(0)
            if isinstance(section_or_requirement, FragmentFromFile):
                if section_or_requirement.has_any_requirements():
                    return True
                continue
            if section_or_requirement.is_requirement:
                return True
            assert section_or_requirement.is_section, section_or_requirement
            task_list.extend(section_or_requirement.section_contents)
        return False

    def get_title(self):
        return self.title

    @staticmethod
    def get_type_string() -> str:
        return "document"

    @property
    def ng_resolved_custom_level(self):
        return None

    def get_requirement_prefix(self) -> str:
        return self.config.get_requirement_prefix()

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
