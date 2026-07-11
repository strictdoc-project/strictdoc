from typing import List

from strictdoc.backend.reqif.reqif_export import ReqIFExport
from strictdoc.backend.reqif.reqif_import import ReqIFImport
from strictdoc.backend.reqif.reqif_reader import ReqIFReader
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.commands.import_reqif_config import ImportReqIFCommandConfig
from strictdoc.core.file_system.file_tree import File
from strictdoc.core.format import ExportContext, Format
from strictdoc.core.project_config import ProjectConfig


class ReqIFFormat(Format):
    @staticmethod
    def handles() -> List[str]:
        return ["reqif-sdoc", "reqifz-sdoc"]

    @staticmethod
    def supported_extensions() -> List[str]:
        return [".reqif", ".reqifz"]

    @staticmethod
    def supports_import() -> bool:
        return True

    @staticmethod
    def supports_export() -> bool:
        return True

    @staticmethod
    def supports_read() -> bool:
        return True

    @staticmethod
    def read_extensions() -> List[str]:
        # Only ".reqif" is auto-discovered as native tree-building input
        # today, not ".reqifz" (even though both are listed in
        # supported_extensions() for export-naming purposes).
        return [".reqif"]

    def read_from_file(
        self,
        doc_file: File,
        project_config: ProjectConfig,  # noqa: ARG002
    ) -> SDocDocument:
        reqif_documents = ReqIFReader.read_from_file(doc_file.full_path)
        assert len(reqif_documents) >= 0
        return reqif_documents[0]

    @staticmethod
    def supports_grammar() -> bool:
        return False

    def export_complete_tree(self, context: ExportContext, handle: str) -> None:
        assert handle in self.handles(), handle
        output_reqif_root = f"{context.project_config.output_dir}/reqif"
        ReqIFExport.export(
            project_config=context.project_config,
            traceability_index=context.traceability_index,
            output_reqif_root=output_reqif_root,
            reqifz=handle == "reqifz-sdoc",
        )

    def import_file(  # type: ignore[override]
        self,
        import_config: ImportReqIFCommandConfig,
        project_config: ProjectConfig,
    ) -> List[SDocDocument]:
        return ReqIFImport.import_from_file(import_config, project_config)
