"""
@relation(SDOC-SRS-109, scope=file)
"""

from typing import Generator, List, Optional

from strictdoc.backend.sdoc.document_reference import DocumentReference
from strictdoc.backend.sdoc.models.document_config import DocumentConfig
from strictdoc.backend.sdoc.models.document_grammar import DocumentGrammar
from strictdoc.backend.sdoc.models.document_view import DocumentView
from strictdoc.backend.sdoc.models.model import (
    SDocDocumentContentIF,
    SDocDocumentFromFileIF,
    SDocDocumentIF,
    SDocNodeIF,
    SDocSectionIF,
)
from strictdoc.core.document_meta import DocumentMeta
from strictdoc.helpers.auto_described import auto_described
from strictdoc.helpers.mid import MID


@auto_described
class SDocDocumentContext:
    def __init__(self) -> None:
        self.title_number_string: Optional[str] = None


@auto_described
class SDocDocument(SDocDocumentIF):
    def __init__(
        self,
        mid: Optional[str],
        title: str,
        config: Optional[DocumentConfig],
        view: Optional[DocumentView],
        grammar: Optional[DocumentGrammar],
        section_contents: List[SDocDocumentContentIF],
        is_bundle_document: bool = False,
    ) -> None:
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
        self.section_contents: List[SDocDocumentContentIF] = section_contents

        self.is_bundle_document: bool = is_bundle_document

        self.fragments_from_files: List[SDocDocumentFromFileIF] = []

        self.ng_level: int = 0
        self.ng_has_requirements = False

        self.meta: Optional[DocumentMeta] = None

        self.reserved_mid: MID = MID(mid) if mid is not None else MID.create()
        self.mid_permanent: bool = mid is not None
        self.included_documents: List[SDocDocumentIF] = []
        self.context: SDocDocumentContext = SDocDocumentContext()

        self.ng_including_document_reference: Optional[DocumentReference] = None
        self.ng_including_document_from_file: Optional[
            SDocDocumentFromFileIF
        ] = None

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
        if self.ng_including_document_reference is None:
            return False
        return self.ng_including_document_reference.get_document() is not None

    def get_including_document(self) -> Optional["SDocDocumentIF"]:
        if self.ng_including_document_reference is None:
            return None
        return self.ng_including_document_reference.get_document()

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
            # Skip nodes without a TOC level.
            if (
                isinstance(node_, SDocSectionIF)
                and node_.ng_resolved_custom_level == "None"
            ):
                continue
            return True
        return False

    def has_any_requirements(self) -> bool:
        task_list: List[SDocDocumentContentIF] = list(self.section_contents)
        while len(task_list) > 0:
            section_or_requirement = task_list.pop(0)
            if isinstance(section_or_requirement, SDocDocumentFromFileIF):
                if section_or_requirement.has_any_requirements():
                    return True
                continue
            if isinstance(section_or_requirement, SDocNodeIF):
                if section_or_requirement.node_type == "TEXT":
                    continue
                return True
            task_list.extend(section_or_requirement.section_contents)
        return False

    def get_display_title(
        self,
        include_toc_number: bool = True,  # noqa: ARG002
    ) -> str:
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
        assert self.grammar is not None
        assert self.grammar.elements is not None
        # FIXME: currently only enumerating a single element ([0])
        yield from self.grammar.elements[0].enumerate_meta_field_titles()

    def enumerate_custom_content_field_titles(
        self,
    ) -> Generator[str, None, None]:
        assert self.grammar is not None
        assert self.grammar.elements is not None
        # FIXME: currently only enumerating a single element ([0])
        yield from self.grammar.elements[
            0
        ].enumerate_custom_content_field_titles()
