import os
from pathlib import Path
from typing import List

from strictdoc.backend.json.json_generator import JSONGenerator
from strictdoc.core.format import ExportContext, Format


class JSONFormat(Format):
    @staticmethod
    def handles() -> List[str]:
        return ["json"]

    @staticmethod
    def supported_extensions() -> List[str]:
        return [".json"]

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
        assert handle in self.handles(), handle
        output_json_root = os.path.join(
            context.project_config.output_dir, "json"
        )
        Path(output_json_root).mkdir(parents=True, exist_ok=True)
        JSONGenerator().export_tree(
            context.traceability_index,
            context.project_config,
            output_json_root,
        )
