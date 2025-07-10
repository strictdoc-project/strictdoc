"""
@relation(SDOC-SRS-18, scope=file)
"""

from abc import ABC, abstractmethod
from typing import Generator, List, Optional, Union

from strictdoc.backend.sdoc.models.document_config import (
    DocumentConfig,
)
from strictdoc.core.document_meta import DocumentMeta
from strictdoc.helpers.mid import MID


class RequirementFieldName:
    MID = "MID"
    UID = "UID"
    PREFIX = "PREFIX"
    LEVEL = "LEVEL"
    STATUS = "STATUS"
    TAGS = "TAGS"
    TITLE = "TITLE"

    # {STATEMENT, DESCRIPTION, CONTENT} are aliases.
    # It is assumed that either field is provided for each node.
    STATEMENT = "STATEMENT"
    DESCRIPTION = "DESCRIPTION"
    CONTENT = "CONTENT"

    RATIONALE = "RATIONALE"
    COMMENT = "COMMENT"


RESERVED_NON_META_FIELDS = [
    RequirementFieldName.TITLE,
    RequirementFieldName.STATEMENT,
    RequirementFieldName.DESCRIPTION,
    RequirementFieldName.CONTENT,
    RequirementFieldName.COMMENT,
    RequirementFieldName.RATIONALE,
    RequirementFieldName.LEVEL,
]


class SDocNodeFieldIF(ABC):
    parent: "SDocNodeIF"


class SDocNodeIF(ABC):
    reserved_mid: MID
    node_type: str
    ng_level: Optional[int]
    ng_resolved_custom_level: Optional[str]
    section_contents: List["SDocElementIF"]

    # FIXME: Get rid of @property everywhere.
    @property
    def reserved_uid(self) -> Optional[str]:
        raise NotImplementedError

    @property
    def reserved_title(self) -> Optional[str]:
        raise NotImplementedError

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

    @abstractmethod
    def get_prefix(self) -> Optional[str]:
        raise NotImplementedError


class SDocSectionIF(ABC):
    parent: Union["SDocDocumentIF", "SDocSectionIF"]
    ng_level: Optional[int]
    ng_resolved_custom_level: Optional[str]
    section_contents: List["SDocElementIF"]

    @abstractmethod
    def get_document(self) -> Optional["SDocDocumentIF"]:
        raise NotImplementedError

    @abstractmethod
    def get_prefix(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_debug_info(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_display_title(self, include_toc_number: bool = True) -> str:
        raise NotImplementedError


class SDocGrammarIF:
    pass


class SDocDocumentIF(ABC):
    config: DocumentConfig
    grammar: Optional[SDocGrammarIF]
    meta: Optional[DocumentMeta]
    section_contents: List["SDocElementIF"]
    included_documents: List["SDocDocumentIF"]
    is_bundle_document: bool
    ng_level: Optional[int]

    @abstractmethod
    def get_prefix(self) -> str:
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

    @property
    def ng_resolved_custom_level(self) -> Optional[str]:
        raise NotImplementedError


class SDocDocumentFromFileIF(ABC):
    parent: Union[SDocDocumentIF, SDocSectionIF]
    ng_resolved_custom_level: Optional[str]

    @abstractmethod
    def iterate_nodes(
        self,
        element_type: Optional[str] = None,
    ) -> Generator[SDocNodeIF, None, None]:
        raise NotImplementedError

    @property
    def section_contents(self) -> List[SDocDocumentIF]:
        raise NotImplementedError


SDocElementIF = Union[
    SDocNodeIF,
    SDocSectionIF,
    SDocDocumentIF,
    SDocDocumentFromFileIF,
]
