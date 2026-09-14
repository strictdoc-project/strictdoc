from typing import List

from strictdoc.backend.asciidoc.asciidoc_writer import AsciiDocWriter
from strictdoc.core.format import ExportContext, Format


class AsciiDocFormat(Format):
    @staticmethod
    def handles() -> List[str]:
        return ["asciidoc"]

    @staticmethod
    def supported_extensions() -> List[str]:
        return [".adoc"]

    @staticmethod
    def supports_import() -> bool:
        return False

    @staticmethod
    def supports_export() -> bool:
        return True

    @staticmethod
    def supports_read() -> bool:
        return False

    @staticmethod
    def supports_edit() -> bool:
        return False

    @staticmethod
    def supports_grammar() -> bool:
        return False

    def export_complete_tree(self, context: ExportContext, handle: str) -> None:
        assert handle == "asciidoc", handle
        AsciiDocWriter(context).export_tree()
