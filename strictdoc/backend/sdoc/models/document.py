# mypy: disable-error-code="union-attr,type-arg"
from typing import Generator, List, Optional

from strictdoc.backend.sdoc.models.document_config import DocumentConfig
from strictdoc.backend.sdoc.models.document_grammar import DocumentGrammar
from strictdoc.backend.sdoc.models.document_view import DocumentView
from strictdoc.backend.sdoc.models.free_text import FreeText
from strictdoc.core.document_meta import DocumentMeta
from strictdoc.helpers.auto_described import auto_described
from strictdoc.helpers.mid import MID


@auto_described
class SDocDocumentContext:
    def __init__(self) -> None:
        self.title_number_string: Optional[str] = None


@auto_described
class SDocDocument:
    def __init__(
        self,
        mid: Optional[str],
        title: str,
        config: Optional[DocumentConfig],
        view: Optional[DocumentView],
        grammar: Optional[DocumentGrammar],
        free_texts: List[FreeText],
        section_contents: List,
        is_bundle_document: bool = False,
    ) -> None:
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
        self.section_contents: List = section_contents

        self.is_bundle_document: bool = is_bundle_document

        # FIXME: Plain list of all fragments found in the document.
        self.fragments_from_files: List = []

        self.ng_level: int = 0
        self.ng_needs_generation = False
        self.ng_has_requirements = False

        self.meta: Optional[DocumentMeta] = None

        self.reserved_mid: MID = MID(mid) if mid is not None else MID.create()
        self.mid_permanent: bool = mid is not None
        self.included_documents: List[SDocDocument] = []
        self.context: SDocDocumentContext = SDocDocumentContext()

        self.ng_including_document_reference: Optional = None  # type: ignore[valid-type]
        self.ng_including_document_from_file: Optional = None  # type: ignore[valid-type]

    @property
    def uid(self) -> Optional[str]:
        return self.config.uid

    @property
    def is_section(self) -> bool:
        return True

    @property
    def is_root_included_document(self) -> bool:
        return self.document_is_included()

    @property
    def is_requirement(self) -> bool:
        return False

    @property
    def is_composite_requirement(self) -> bool:
        return False

    def get_display_node_type(self) -> str:
        return "Document"

    def get_node_type_string(self) -> Optional[str]:
        return None

    def get_type_string(self) -> str:
        return "document" if not self.document_is_included() else "section"

    def get_debug_info(self) -> str:
        debug_components: List[str] = [f"TITLE = '{self.title}'"]
        if self.meta is not None:
            debug_components.append(
                f" ({self.meta.input_doc_rel_path.relative_path})"
            )
        return f"Document({', '.join(debug_components)})"

    def document_is_included(self) -> bool:
        return self.ng_including_document_reference.get_document() is not None

    def get_including_document(self) -> Optional["SDocDocument"]:
        # FIXME: Fix no-any-return when the circular references between
        #        SDocDocument and DocumentReference are fixed.
        return self.ng_including_document_reference.get_document()  # type: ignore[no-any-return]

    def iterate_included_documents_depth_first(
        self,
    ) -> Generator["SDocDocument", None, None]:
        for included_document_ in self.included_documents:
            yield included_document_
            yield from included_document_.iterate_included_documents_depth_first()

    @property
    def reserved_uid(self) -> Optional[str]:
        return self.config.uid

    def assign_meta(self, meta: DocumentMeta) -> None:
        assert isinstance(meta, DocumentMeta)
        self.meta = meta

    def has_any_nodes(self) -> bool:
        return len(self.section_contents) > 0

    def has_any_toc_nodes(self) -> bool:
        for node_ in self.section_contents:
            if node_.__class__.__name__ == "DocumentFromFile":
                return True
            if node_.is_section:
                if node_.ng_resolved_custom_level != "None":
                    return True
                # Skip nodes without a TOC level.
                continue
            return True
        return False

    def has_any_requirements(self) -> bool:
        from strictdoc.backend.sdoc.models.document_from_file import (
            DocumentFromFile,
        )

        task_list = list(self.section_contents)
        while len(task_list) > 0:
            section_or_requirement = task_list.pop(0)
            if isinstance(section_or_requirement, DocumentFromFile):
                if section_or_requirement.has_any_requirements():
                    return True
                continue
            if section_or_requirement.is_requirement:
                if section_or_requirement.node_type == "TEXT":
                    continue
                return True
            assert section_or_requirement.is_section, section_or_requirement
            task_list.extend(section_or_requirement.section_contents)
        return False

    def get_display_title(self) -> str:
        return self.title

    @property
    def ng_resolved_custom_level(self) -> Optional[str]:
        return None

    @property
    def requirement_prefix(self) -> str:
        return self.get_requirement_prefix()

    def get_requirement_prefix(self) -> str:
        return self.config.get_requirement_prefix()

    def enumerate_meta_field_titles(self) -> Generator[str, None, None]:
        # FIXME: currently only enumerating a single element ([0])
        yield from self.grammar.elements[0].enumerate_meta_field_titles()

    def enumerate_custom_content_field_titles(
        self,
    ) -> Generator[str, None, None]:
        # FIXME: currently only enumerating a single element ([0])
        yield from self.grammar.elements[
            0
        ].enumerate_custom_content_field_titles()
