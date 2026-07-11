"""
The Format abstraction: top-level abstraction for all formats that
StrictDoc can export to and/or import from.

@relation(SDOC-SRS-119, scope=file)
"""

import argparse
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional, Tuple

from strictdoc.helpers.string import create_safe_document_file_name

if TYPE_CHECKING:
    from strictdoc.backend.sdoc.models.document import SDocDocument
    from strictdoc.backend.sdoc.models.document_grammar import DocumentGrammar
    from strictdoc.commands.convert_config import ConvertCommandConfig
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

    @classmethod
    def handle_for_extension(cls, extension: str) -> Optional[str]:
        """
        Map a file extension to one of this Format's handles(), for
        `convert --input-format` auto-discovery. Pairs handles()/
        supported_extensions() positionally when both lists are the same
        length (e.g. ReqIFFormat's ["reqif-sdoc", "reqifz-sdoc"] <->
        [".reqif", ".reqifz"]); otherwise falls back to the first handle.
        Returns None if this Format has no CLI handle at all (e.g.
        JUnitXMLFormat) or doesn't support the given extension.
        """
        handles = cls.handles()
        if not handles:
            return None
        extensions = cls.supported_extensions()
        if extension not in extensions:
            return None
        if len(handles) == len(extensions):
            return handles[extensions.index(extension)]
        return handles[0]

    @staticmethod
    def supports_convert_output() -> bool:
        """Whether `convert --output-format` may target this Format."""
        return False

    def write_converted_document(
        self,
        document: "SDocDocument",
        output_dir: str,
        filename_stem: str,
        project_config: "ProjectConfig",
    ) -> None:
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support being a convert "
            f"output format."
        )

    def import_output_filename_stem(
        self,
        document: "SDocDocument",
        convert_config: "ConvertCommandConfig",  # noqa: ARG002
    ) -> str:
        return create_safe_document_file_name(document.reserved_title)

    @classmethod
    def add_import_arguments(cls, parser: argparse.ArgumentParser) -> None:  # noqa: ARG003
        """
        Override to contribute this Format's own CLI flags to `convert`
        (e.g. ExcelFormat adds --excel-parser, ReqIFFormat adds
        --reqif-profile/--reqif-enable-mid/--reqif-import-markup). A custom
        Format registered via the project config can add its own flags here
        without touching ConvertCommand/ConvertCommandConfig at all -- the
        only thing shared across formats is input_path/output_path/
        --input-format/--output-format/--config. Default: no extra flags.
        """
        return

    @classmethod
    def build_import_options(cls, args: argparse.Namespace) -> object:  # noqa: ARG003
        """
        Pluck this Format's own fields off the parsed argparse.Namespace
        (populated by this same Format's add_import_arguments()) into a
        type-safe, format-specific options object, e.g. a @dataclass. The
        return type is `object` here since ConvertAction dispatches to an
        arbitrary Format by handle and can't know the concrete type -- but
        each override should return its own concrete dataclass, and its own
        import_file() should declare that same concrete type as its
        parameter, so the plucking + consuming stays type-checked within
        that Format's own module.
        """
        raise NotImplementedError(f"{cls.__name__} does not support import.")

    def import_file(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support import."
        )

    def import_folder(self, *args: object, **kwargs: object) -> object:
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support import."
        )
