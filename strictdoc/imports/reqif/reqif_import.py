import os
from pathlib import Path

from strictdoc.backend.dsl.writer import SDWriter
from strictdoc.cli.cli_arg_parser import ImportCommandConfig
from strictdoc.imports.reqif.stage1.reqif_stage1_parser import ReqIFStage1Parser
from strictdoc.imports.reqif.stage2.abstract_parser import (
    AbstractReqIFStage2Parser,
)
from strictdoc.imports.reqif.stage2.doors.parser import (
    DoorsReqIFReqIFStage2Parser,
)
from strictdoc.imports.reqif.stage2.native.parser import (
    StrictDocReqIFStage2Parser,
)


class ReqIFImport:
    @staticmethod
    def import_from_file(import_config: ImportCommandConfig):
        stage2_parser: AbstractReqIFStage2Parser = (
            DoorsReqIFReqIFStage2Parser()
            if import_config.parser == "doors"
            else StrictDocReqIFStage2Parser()
        )
        reqif_bundle = ReqIFStage1Parser.parse(import_config.input_path)

        document = stage2_parser.parse_reqif(reqif_bundle)

        document_content = SDWriter().write(document)
        output_folder = os.path.dirname(import_config.output_path)
        Path(output_folder).mkdir(parents=True, exist_ok=True)
        with open(
            import_config.output_path, "w", encoding="utf8"
        ) as output_file:
            output_file.write(document_content)
