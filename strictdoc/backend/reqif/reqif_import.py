import os
from pathlib import Path

from reqif.parser import ReqIFParser

from strictdoc.backend.reqif.import_.abstract_parser import (
    AbstractReqIFStage2Parser,
)
from strictdoc.backend.reqif.import_.native.parser import (
    StrictDocReqIFStage2Parser,
)
from strictdoc.backend.sdoc.writer import SDWriter
from strictdoc.cli.cli_arg_parser import ImportCommandConfig


class ReqIFImport:
    @staticmethod
    def import_from_file(import_config: ImportCommandConfig):
        stage2_parser: AbstractReqIFStage2Parser = StrictDocReqIFStage2Parser()
        reqif_bundle = ReqIFParser.parse(import_config.input_path)
        document = stage2_parser.parse_reqif(reqif_bundle)

        document_content = SDWriter().write(document)
        output_folder = os.path.dirname(import_config.output_path)
        Path(output_folder).mkdir(parents=True, exist_ok=True)
        with open(
            import_config.output_path, "w", encoding="utf8"
        ) as output_file:
            output_file.write(document_content)
