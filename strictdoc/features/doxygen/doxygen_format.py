import os
from typing import List

from strictdoc.core.format import ExportContext, Format
from strictdoc.features.doxygen.generator import DoxygenGenerator


class DoxygenFormat(Format):
    @staticmethod
    def handles() -> List[str]:
        return ["doxygen"]

    @staticmethod
    def supported_extensions() -> List[str]:
        return [".tag"]

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
    def supports_grammar() -> bool:
        return False

    def export_complete_tree(self, context: ExportContext, handle: str) -> None:
        assert handle in self.handles(), handle
        output_doxygen_root = os.path.join(
            context.project_config.output_dir, "doxygen"
        )
        doxygen_generator = DoxygenGenerator(
            project_config=context.project_config
        )
        doxygen_generator.export(
            traceability_index=context.traceability_index,
            path_to_output_dir=output_doxygen_root,
        )
