# mypy: disable-error-code="no-redef,no-untyped-def"
import os.path
from typing import List

from reqif.parser import ReqIFParser, ReqIFZParser
from reqif.reqif_bundle import ReqIFBundle, ReqIFZBundle

from strictdoc.backend.reqif.p01_sdoc.reqif_to_sdoc_converter import (
    P01_ReqIFToSDocConverter,
)
from strictdoc.backend.reqif.sdoc_reqif_fields import ReqIFProfile
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.cli.cli_arg_parser import ImportReqIFCommandConfig
from strictdoc.core.project_config import ProjectConfig


class ReqIFImport:
    @staticmethod
    def import_from_file(
        import_config: ImportReqIFCommandConfig, project_config: ProjectConfig
    ) -> List[SDocDocument]:
        converter = ReqIFImport.select_reqif_profile(import_config)

        assert os.path.isfile(import_config.input_path), (
            import_config.input_path
        )

        if import_config.input_path.endswith(".reqifz"):
            reqifz_bundle: ReqIFZBundle = ReqIFZParser.parse(
                import_config.input_path
            )
            assert len(reqifz_bundle.reqif_bundles) > 0
            documents: List[SDocDocument] = converter.convert_reqif_bundle(
                next(iter(reqifz_bundle.reqif_bundles.values())),
                enable_mid=import_config.reqif_enable_mid
                or project_config.reqif_enable_mid,
                import_markup=import_config.reqif_import_markup
                if import_config.reqif_import_markup is not None
                else project_config.reqif_import_markup,
            )
        else:
            reqif_bundle: ReqIFBundle = ReqIFParser.parse(
                import_config.input_path
            )
            documents: List[SDocDocument] = converter.convert_reqif_bundle(
                reqif_bundle,
                enable_mid=import_config.reqif_enable_mid
                or project_config.reqif_enable_mid,
                import_markup=import_config.reqif_import_markup
                if import_config.reqif_import_markup is not None
                else project_config.reqif_import_markup,
            )
        return documents

    @staticmethod
    def select_reqif_profile(import_config: ImportReqIFCommandConfig):
        if (
            import_config.profile is None
            or import_config.profile == ReqIFProfile.P01_SDOC
        ):
            return P01_ReqIFToSDocConverter()
        raise NotImplementedError(
            f"Unsupported profile: {import_config.profile}"
        )
