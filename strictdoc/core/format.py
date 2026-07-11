"""
The Format abstraction: top-level abstraction for all formats that
StrictDoc can export to and/or import from.

@relation(SDOC-SRS-119, scope=file)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional, Tuple

if TYPE_CHECKING:
    from strictdoc.backend.sdoc.models.document import SDocDocument
    from strictdoc.backend.sdoc.models.document_grammar import DocumentGrammar
    from strictdoc.core.file_system.file_tree import File
    from strictdoc.core.project_config import ProjectConfig
    from strictdoc.core.traceability_index import TraceabilityIndex
    from strictdoc.export.html.document_type import DocumentType
    from strictdoc.export.html.html_templates import HTMLTemplates
    from strictdoc.helpers.parallelizer import Parallelizer


@dataclass
class ExportContext:
    """
    Shared, per-export() call state that Format.export_complete_tree()
    implementations pull from. html_templates/bundle_* fields are only
    populated when an HTML-based format (html, html2pdf) was requested, since
    building them is expensive and only those formats need them.
    """

    project_config: "ProjectConfig"
    traceability_index: "TraceabilityIndex"
    parallelizer: "Parallelizer"
    html_templates: Optional["HTMLTemplates"] = None
    bundle_traceability_index: Optional["TraceabilityIndex"] = None
    bundle_document: Optional["SDocDocument"] = None


class Format(ABC):
    @staticmethod
    @abstractmethod
    def handles() -> List[str]:
        """The CLI/config handle(s) this Format reacts to, e.g. ['html']."""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def supported_extensions() -> List[str]:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def supports_import() -> bool:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def supports_export() -> bool:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def supports_read() -> bool:
        raise NotImplementedError

    @staticmethod
    def read_extensions() -> List[str]:
        """
        Extensions this Format auto-discovers/reads as native DocumentFinder
        tree-building input. Distinct from supported_extensions(), since not
        every extension a Format is generally associated with is also one it
        natively reads today (e.g. ReqIFFormat reads ".reqif" but not
        ".reqifz", even though supported_extensions() lists both).
        """
        return []

    def read_from_file(
        self, doc_file: "File", project_config: "ProjectConfig"
    ) -> "SDocDocument":
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support reading."
        )

    @staticmethod
    @abstractmethod
    def supports_grammar() -> bool:
        raise NotImplementedError

    @staticmethod
    def grammar_extensions() -> List[str]:
        return []

    def read_grammar(
        self, doc_file: "File", project_config: "ProjectConfig"
    ) -> "DocumentGrammar":
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support reading a grammar."
        )

    @abstractmethod
    def export_complete_tree(self, context: ExportContext, handle: str) -> None:
        raise NotImplementedError

    def export_single_document(
        self,
        context: ExportContext,
        document: "SDocDocument",
        specific_documents: Optional[Tuple["DocumentType", ...]] = None,
    ) -> None:
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support exporting a "
            f"single document."
        )

    def import_file(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support import."
        )

    def import_folder(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support import."
        )
