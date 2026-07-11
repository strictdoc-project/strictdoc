import os
from pathlib import Path
from typing import List

from strictdoc.backend.spdx.spdx_generator import SPDXGenerator
from strictdoc.core.format import ExportContext, Format


class SPDXFormat(Format):
    @staticmethod
    def handles() -> List[str]:
        return ["spdx"]

    @staticmethod
    def supported_extensions() -> List[str]:
        return [".spdx"]

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
        output_spdx_root = os.path.join(
            context.project_config.output_dir, "spdx"
        )
        Path(output_spdx_root).mkdir(parents=True, exist_ok=True)
        SPDXGenerator().export_tree(
            context.project_config, context.traceability_index, output_spdx_root
        )
