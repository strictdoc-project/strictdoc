from typing import List

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc_source_code.test_reports.junit_xml_reader import (
    JUnitXMLReader,
)
from strictdoc.core.file_system.file_tree import File
from strictdoc.core.format import ExportContext, Format
from strictdoc.core.project_config import ProjectConfig


class JUnitXMLFormat(Format):
    """
    Read-only Format for JUnit XML test reports.

    No CLI --formats/import counterpart exists; this Format is only used by
    DocumentFinder's native tree-building discovery.
    """

    @staticmethod
    def handles() -> List[str]:
        return []

    @staticmethod
    def supported_extensions() -> List[str]:
        return [".junit.xml"]

    @staticmethod
    def supports_import() -> bool:
        return False

    @staticmethod
    def supports_export() -> bool:
        return False

    @staticmethod
    def supports_read() -> bool:
        return True

    @staticmethod
    def supports_edit() -> bool:
        return False

    @staticmethod
    def read_extensions() -> List[str]:
        return [".junit.xml"]

    def read_from_file(
        self, doc_file: File, project_config: ProjectConfig
    ) -> SDocDocument:
        return JUnitXMLReader.read_from_file(doc_file, project_config)

    @staticmethod
    def supports_grammar() -> bool:
        return False

    def export_complete_tree(self, context: ExportContext, handle: str) -> None:
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support export."
        )
