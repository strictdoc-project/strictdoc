"""
@relation(SDOC-SRS-72, scope=file)
"""

from typing import List

from reqif.parser import ReqIFParser, ReqIFZParser
from reqif.reqif_bundle import ReqIFBundle, ReqIFZBundle

from strictdoc.backend.reqif.p01_sdoc.reqif_to_sdoc_converter import (
    P01_ReqIFToSDocConverter,
)
from strictdoc.backend.sdoc.models.document import SDocDocument


class ReqIFReader:
    @staticmethod
    def read_from_file(input_path: str) -> List[SDocDocument]:
        converter = P01_ReqIFToSDocConverter()

        documents: List[SDocDocument]
        if input_path.endswith(".reqifz"):
            reqifz_bundle: ReqIFZBundle = ReqIFZParser.parse(input_path)
            assert len(reqifz_bundle.reqif_bundles) > 0
            documents = converter.convert_reqif_bundle(
                next(iter(reqifz_bundle.reqif_bundles.values())),
                enable_mid=True,
                import_markup="HTML",
            )
        else:
            reqif_bundle: ReqIFBundle = ReqIFParser.parse(input_path)
            documents = converter.convert_reqif_bundle(
                reqif_bundle,
                enable_mid=True,
                import_markup="HTML",
            )
        return documents
