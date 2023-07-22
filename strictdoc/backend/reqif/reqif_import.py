from typing import List

from reqif.parser import ReqIFParser
from reqif.reqif_bundle import ReqIFBundle

from strictdoc.backend.reqif.p01_sdoc.reqif_to_sdoc_converter import (
    P01_ReqIFToSDocConverter,
)
from strictdoc.backend.reqif.p11_polarion.reqif_to_sdoc_converter import (
    P11_ReqIFToSDocConverter,
)
from strictdoc.backend.reqif.sdoc_reqif_fields import ReqIFProfile
from strictdoc.backend.sdoc.models.document import Document
from strictdoc.cli.cli_arg_parser import ImportReqIFCommandConfig


class ReqIFImport:
    @staticmethod
    def import_from_file(
        import_config: ImportReqIFCommandConfig,
    ) -> List[Document]:
        converter = ReqIFImport.select_reqif_profile(import_config)

        reqif_bundle: ReqIFBundle = ReqIFParser.parse(import_config.input_path)
        documents: List[Document] = converter.convert_reqif_bundle(reqif_bundle)
        return documents

    @staticmethod
    def select_reqif_profile(import_config: ImportReqIFCommandConfig):
        if (
            import_config.profile is None
            or import_config.profile == ReqIFProfile.P01_SDOC
        ):
            return P01_ReqIFToSDocConverter()
        if import_config.profile == ReqIFProfile.P11_POLARION:
            return P11_ReqIFToSDocConverter()
        raise NotImplementedError(
            f"Unsupported profile: {import_config.profile}"
        )
