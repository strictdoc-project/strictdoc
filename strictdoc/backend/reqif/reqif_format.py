import argparse
from typing import List

from strictdoc.backend.reqif.reqif_export import ReqIFExport
from strictdoc.backend.reqif.reqif_import import ReqIFImport, ReqIFImportOptions
from strictdoc.backend.reqif.reqif_reader import ReqIFReader
from strictdoc.backend.reqif.sdoc_reqif_fields import ReqIFProfile
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.commands._shared import (
    _check_reqif_import_markup,
    _check_reqif_profile,
)
from strictdoc.core.file_system.file_tree import File
from strictdoc.core.format import ExportContext, Format
from strictdoc.core.project_config import ProjectConfig


class ReqIFFormat(Format):
    @staticmethod
    def handles() -> List[str]:
        return ["reqif-sdoc", "reqifz-sdoc"]

    @classmethod
    def add_import_arguments(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--reqif-profile",
            type=_check_reqif_profile,
            default=ReqIFProfile.P01_SDOC,
            help="An argument that selects the ReqIF import/export profile.",
        )
        parser.add_argument(
            "--reqif-enable-mid",
            default=False,
            action="store_true",
            help=(
                "Controls whether StrictDoc's MID field will be mapped to ReqIF "
                "SPEC-OBJECT's IDENTIFIER and vice versa when exporting/importing."
            ),
        )
        parser.add_argument(
            "--reqif-import-markup",
            default=None,
            type=_check_reqif_import_markup,
            help=(
                "Controls which MARKUP option the imported SDoc documents will have. "
                "This value is RST as what StrictDoc has by default but very often "
                "the requirements tools use the (X)HTML markup for multiline fields in "
                "which case HTML is the best option."
            ),
        )

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
    def supports_edit() -> bool:
        return False

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

    @classmethod
    def build_import_options(
        cls, args: argparse.Namespace
    ) -> ReqIFImportOptions:
        return ReqIFImportOptions(
            input_path=args.input_path,
            reqif_profile=args.reqif_profile,
            reqif_enable_mid=args.reqif_enable_mid,
            reqif_import_markup=args.reqif_import_markup,
        )

    def import_file(  # type: ignore[override]
        self,
        import_options: ReqIFImportOptions,
        project_config: ProjectConfig,
    ) -> List[SDocDocument]:
        return ReqIFImport.import_from_file(import_options, project_config)
