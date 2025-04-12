from abc import ABC, abstractmethod
from typing import Generator, List, Optional, Union

from strictdoc.backend.sdoc.models.document_config import DocumentConfig
from strictdoc.backend.sdoc.models.document_grammar import DocumentGrammar
from strictdoc.core.document_meta import DocumentMeta


class SDocNodeFieldIF(ABC):
    parent: "SDocNodeIF"


class SDocNodeIF(ABC):
    node_type: str
    ng_resolved_custom_level: Optional[str]

    @abstractmethod
    def is_normative_node(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def is_text_node(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_debug_info(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_document(self) -> Optional["SDocDocumentIF"]:
        raise NotImplementedError

    @abstractmethod
    def get_including_document(self) -> Optional["SDocDocumentIF"]:
        raise NotImplementedError

    @abstractmethod
    def get_parent_or_including_document(self) -> "SDocDocumentIF":
        raise NotImplementedError


class SDocCompositeNodeIF(SDocNodeIF):
    section_contents: List["SDocSectionContentIF"]

    @abstractmethod
    def get_requirement_prefix(self) -> str:
        raise NotImplementedError


class SDocSectionIF(ABC):
    parent: Union["SDocDocumentIF", "SDocSectionIF"]
    ng_resolved_custom_level: Optional[str]
    section_contents: List["SDocSectionContentIF"]

    @abstractmethod
    def get_document(self) -> Optional["SDocDocumentIF"]:
        raise NotImplementedError

    @abstractmethod
    def get_requirement_prefix(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_debug_info(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_display_title(self, include_toc_number: bool = True) -> str:
        raise NotImplementedError


class SDocDocumentIF(ABC):
    config: DocumentConfig
    grammar: Optional[DocumentGrammar]
    meta: Optional[DocumentMeta]
    section_contents: List["SDocSectionContentIF"]
    included_documents: List["SDocDocumentIF"]
    is_bundle_document: bool

    @abstractmethod
    def get_requirement_prefix(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_debug_info(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def iterate_included_documents_depth_first(
        self,
    ) -> Generator["SDocDocumentIF", None, None]:
        raise NotImplementedError

    @abstractmethod
    def get_display_title(self, include_toc_number: bool = True) -> str:
        raise NotImplementedError


class SDocDocumentFromFileIF:
    parent: Union[SDocDocumentIF, SDocSectionIF]
    ng_resolved_custom_level: Optional[str]

    @abstractmethod
    def has_any_requirements(self) -> bool:
        raise NotImplementedError

    @property
    def section_contents(self) -> List[SDocDocumentIF]:
        raise NotImplementedError


SDocSectionContentIF = Union[
    SDocCompositeNodeIF,
    SDocNodeIF,
    SDocSectionIF,
    SDocDocumentFromFileIF,
]


SDocDocumentContentIF = Union[
    SDocCompositeNodeIF,
    SDocDocumentFromFileIF,
    SDocNodeIF,
    SDocSectionIF,
]


SDocElementIF = Union[
    SDocNodeIF,
    SDocCompositeNodeIF,
    SDocSectionIF,
    SDocDocumentIF,
    SDocDocumentFromFileIF,
]
