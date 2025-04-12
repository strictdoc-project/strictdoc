"""
@relation(SDOC-SRS-99, scope=file)
"""

# mypy: disable-error-code="attr-defined,no-untyped-call,no-untyped-def,union-attr"
from typing import List, Optional, Union

from strictdoc.backend.sdoc.document_reference import DocumentReference
from strictdoc.backend.sdoc.models.model import (
    SDocDocumentIF,
    SDocSectionContentIF,
    SDocSectionIF,
)
from strictdoc.helpers.auto_described import auto_described
from strictdoc.helpers.mid import MID


@auto_described
class SectionContext:
    def __init__(self):
        self.title_number_string = None


@auto_described
class SDocSection(SDocSectionIF):
    def __init__(
        self,
        parent: Union[SDocDocumentIF, SDocSectionIF],
        mid: Optional[str],
        uid: Optional[str],
        custom_level: Optional[str],
        title: str,
        requirement_prefix: Optional[str],
        section_contents: List[SDocSectionContentIF],
    ):
        self.parent: Union[SDocDocumentIF, SDocSectionIF] = parent

        # TODO: Remove .uid, keep reserved_uid only.
        meaningful_uid: Optional[str] = None
        if uid is not None and len(uid) > 0:
            meaningful_uid = uid
        self.uid: Optional[str] = meaningful_uid
        self.reserved_uid: Optional[str] = meaningful_uid

        self.title: str = title
        self.reserved_title = title
        self.requirement_prefix: Optional[str] = requirement_prefix

        self.section_contents = section_contents

        # HEF4
        self.custom_level: Optional[str] = custom_level
        self.ng_resolved_custom_level: Optional[str] = custom_level

        self.ng_level: Optional[int] = None
        self.ng_has_requirements = False
        self.ng_document_reference: Optional[DocumentReference] = None
        self.ng_including_document_reference: Optional[DocumentReference] = None
        self.context = SectionContext()

        self.reserved_mid: MID = MID(mid) if mid is not None else MID.create()
        self.mid_permanent: bool = mid is not None

        # This is always true, unless the node is filtered out with --filter-requirements.
        self.ng_whitelisted = True

    @staticmethod
    def get_type_string() -> str:
        return "section"

    def get_display_node_type(self) -> str:
        return "Section"

    def get_node_type_string(self) -> Optional[str]:
        return None

    def get_debug_info(self) -> str:
        debug_components: List[str] = [f"TITLE = '{self.title}'"]
        if self.document is not None:
            debug_components.append(
                f"document = {self.document.get_debug_info()}"
            )
        return f"Section({', '.join(debug_components)})"

    @property
    def is_root_included_document(self):
        return False

    def get_display_title(self, include_toc_number: bool = True) -> str:
        if include_toc_number and self.context.title_number_string is not None:
            return f"{self.context.title_number_string}. {self.title}"
        return self.title

    # FIXME: Remove this method, use get_document() instead.
    @property
    def document(self) -> Optional[SDocDocumentIF]:
        return self.ng_document_reference.get_document()

    def get_document(self) -> Optional[SDocDocumentIF]:
        return self.ng_document_reference.get_document()

    def get_including_document(self):
        return self.ng_including_document_reference.get_document()

    @property
    def parent_or_including_document(self) -> SDocDocumentIF:
        including_document_or_none = (
            self.ng_including_document_reference.get_document()
        )
        if including_document_or_none is not None:
            return including_document_or_none

        document: Optional[SDocDocumentIF] = (
            self.ng_document_reference.get_document()
        )
        assert document is not None, (
            "A valid requirement must always have a reference to the document."
        )
        return document

    def document_is_included(self):
        return self.ng_including_document_reference.get_document() is not None

    @property
    def is_requirement(self):
        return False

    @property
    def is_composite_requirement(self):
        return False

    @property
    def is_section(self):
        return True

    def has_any_text_nodes(self):
        return any(
            node_.__class__.__name__ == "SDocNode" and node_.node_type == "TEXT"
            for node_ in self.section_contents
        )

    @property
    def is_root(self) -> bool:
        return self.document.config.root is True

    def get_requirement_prefix(self) -> str:
        if self.requirement_prefix is not None:
            return self.requirement_prefix
        parent: Union[SDocSectionIF, SDocDocumentIF] = self.parent
        return parent.get_requirement_prefix()

    def blacklist_if_needed(self) -> None:
        for node_ in self.section_contents:
            if node_.ng_whitelisted:
                return

        self.ng_whitelisted = False

        # If it turns out that all child nodes are blacklisted,
        # go up and blacklist the parent node if needed.
        if isinstance(self.parent, SDocSection) and self.parent.ng_whitelisted:
            self.parent.blacklist_if_needed()
