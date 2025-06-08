from abc import ABC, abstractmethod
from typing import Generator, List, Optional, Union

from strictdoc.backend.sdoc.models.document_config import DocumentConfig
from strictdoc.core.document_meta import DocumentMeta


class SDocNodeFieldIF(ABC):
    parent: "SDocNodeIF"


class SDocNodeIF(ABC):
    node_type: str
    ng_level: Optional[int]
    ng_resolved_custom_level: Optional[str]
    section_contents: List["SDocSectionContentIF"]

    @abstractmethod
    def is_normative_node(self) -> bool:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def is_text_node(self) -> bool:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def get_debug_info(self) -> str:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def get_document(self) -> Optional["SDocDocumentIF"]:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def get_including_document(self) -> Optional["SDocDocumentIF"]:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def get_parent_or_including_document(self) -> "SDocDocumentIF":
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def get_prefix(self) -> Optional[str]:
        raise NotImplementedError  # pragma: no cover


class SDocSectionIF(ABC):
    parent: Union["SDocDocumentIF", "SDocSectionIF"]
    ng_level: Optional[int]
    ng_resolved_custom_level: Optional[str]
    section_contents: List["SDocSectionContentIF"]

    @abstractmethod
    def get_document(self) -> Optional["SDocDocumentIF"]:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def get_prefix(self) -> str:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def get_debug_info(self) -> str:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def get_display_title(self, include_toc_number: bool = True) -> str:
        raise NotImplementedError  # pragma: no cover


class SDocGrammarIF:
    pass


class SDocDocumentIF(ABC):
    config: DocumentConfig
    grammar: Optional[SDocGrammarIF]
    meta: Optional[DocumentMeta]
    section_contents: List["SDocSectionContentIF"]
    included_documents: List["SDocDocumentIF"]
    is_bundle_document: bool
    ng_level: Optional[int]

    @abstractmethod
    def get_prefix(self) -> str:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def get_debug_info(self) -> str:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def iterate_included_documents_depth_first(
        self,
    ) -> Generator["SDocDocumentIF", None, None]:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def get_display_title(self, include_toc_number: bool = True) -> str:
        raise NotImplementedError  # pragma: no cover

    @property
    def ng_resolved_custom_level(self) -> Optional[str]:
        raise NotImplementedError  # pragma: no cover


class SDocDocumentFromFileIF(ABC):
    parent: Union[SDocDocumentIF, SDocSectionIF]
    ng_resolved_custom_level: Optional[str]

    @abstractmethod
    def iterate_nodes(
        self,
        element_type: Optional[str] = None,
    ) -> Generator[SDocNodeIF, None, None]:
        raise NotImplementedError  # pragma: no cover

    @property
    def section_contents(self) -> List[SDocDocumentIF]:
        raise NotImplementedError  # pragma: no cover


SDocSectionContentIF = Union[
    SDocNodeIF,
    SDocSectionIF,
    SDocDocumentFromFileIF,
]


SDocDocumentContentIF = Union[
    SDocDocumentFromFileIF,
    SDocNodeIF,
    SDocSectionIF,
]


SDocElementIF = Union[
    SDocNodeIF,
    SDocSectionIF,
    SDocDocumentIF,
    SDocDocumentFromFileIF,
]
