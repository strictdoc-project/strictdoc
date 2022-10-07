import os
from pathlib import Path

from reqif.unparser import ReqIFUnparser

from strictdoc.backend.reqif.export.sdoc_to_reqif_converter import (
    SDocToReqIFObjectConverter,
)
from strictdoc.core.traceability_index import TraceabilityIndex


class ReqIFExport:
    @staticmethod
    def export(
        traceability_index: TraceabilityIndex,
        output_reqif_root: str,
    ):
        Path(output_reqif_root).mkdir(parents=True, exist_ok=True)
        output_file_path: str = os.path.join(output_reqif_root, "output.reqif")

        reqif_bundle = SDocToReqIFObjectConverter.convert_document_tree(
            document_tree=traceability_index.document_tree
        )
        reqif_content: str = ReqIFUnparser.unparse(reqif_bundle)

        with open(output_file_path, "w", encoding="utf8") as output_file:
            output_file.write(reqif_content)
