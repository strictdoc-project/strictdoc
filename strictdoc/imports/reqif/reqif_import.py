import os
from pathlib import Path

from reqif.parser import ReqIFParser

from strictdoc.backend.dsl.writer import SDWriter
from strictdoc.cli.cli_arg_parser import ImportCommandConfig
from strictdoc.imports.reqif.stage2.abstract_parser import (
    AbstractReqIFStage2Parser,
)
from strictdoc.imports.reqif.stage2.fm_studio.parser import (
    FMStudioReqIFStage2Parser,
)
from strictdoc.imports.reqif.stage2.native.parser import (
    StrictDocReqIFStage2Parser,
)


class ReqIFImport:
    @staticmethod
    def import_from_file(import_config: ImportCommandConfig):
        stage2_parser: AbstractReqIFStage2Parser = (
            FMStudioReqIFStage2Parser()
            if import_config.parser == "fm-studio"
            else StrictDocReqIFStage2Parser()
        )
        reqif_bundle = ReqIFParser.parse(import_config.input_path)
        document = stage2_parser.parse_reqif(reqif_bundle)

        document_content = SDWriter().write(document)
        output_folder = os.path.dirname(import_config.output_path)
        Path(output_folder).mkdir(parents=True, exist_ok=True)
        with open(
            import_config.output_path, "w", encoding="utf8"
        ) as output_file:
            output_file.write(document_content)
