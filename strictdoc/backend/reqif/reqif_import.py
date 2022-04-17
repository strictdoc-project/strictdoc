from reqif.parser import ReqIFParser

from strictdoc.backend.reqif.import_.reqif_to_sdoc_converter import (
    ReqIFToSDocConverter,
)
from strictdoc.cli.cli_arg_parser import ImportReqIFCommandConfig


class ReqIFImport:
    @staticmethod
    def import_from_file(import_config: ImportReqIFCommandConfig):
        stage2_parser: ReqIFToSDocConverter = ReqIFToSDocConverter()
        reqif_bundle = ReqIFParser.parse(import_config.input_path)
        document = stage2_parser.convert_reqif_bundle(reqif_bundle)
        return document
