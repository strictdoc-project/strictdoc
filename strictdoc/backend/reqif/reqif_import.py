from typing import List

from reqif.parser import ReqIFParser
from reqif.reqif_bundle import ReqIFBundle

from strictdoc.backend.reqif.import_.reqif_to_sdoc_converter import (
    ReqIFToSDocConverter,
)
from strictdoc.backend.sdoc.models.document import Document
from strictdoc.cli.cli_arg_parser import ImportReqIFCommandConfig


class ReqIFImport:
    @staticmethod
    def import_from_file(
        import_config: ImportReqIFCommandConfig,
    ) -> List[Document]:
        stage2_parser: ReqIFToSDocConverter = ReqIFToSDocConverter()
        reqif_bundle: ReqIFBundle = ReqIFParser.parse(import_config.input_path)
        documents: List[Document] = stage2_parser.convert_reqif_bundle(
            reqif_bundle
        )
        return documents
