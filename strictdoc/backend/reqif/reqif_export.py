import os
from pathlib import Path

from reqif.unparser import ReqIFUnparser

from strictdoc.backend.reqif.p01_sdoc.sdoc_to_reqif_converter import (
    P01_SDocToReqIFObjectConverter,
)
from strictdoc.backend.reqif.sdoc_reqif_fields import ReqIFProfile
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex


class ReqIFExport:
    @staticmethod
    def export(
        project_config: ProjectConfig,
        traceability_index: TraceabilityIndex,
        output_reqif_root: str,
    ):
        Path(output_reqif_root).mkdir(parents=True, exist_ok=True)
        output_file_path: str = os.path.join(output_reqif_root, "output.reqif")

        if project_config.reqif_profile == ReqIFProfile.P01_SDOC:
            reqif_bundle = P01_SDocToReqIFObjectConverter.convert_document_tree(
                document_tree=traceability_index.document_tree
            )
        else:
            raise NotImplementedError(
                f"Requirements profile does not implement the ReqIF export yet: "
                f"{project_config.reqif_profile}."
            )
        reqif_content: str = ReqIFUnparser.unparse(reqif_bundle)

        with open(output_file_path, "w", encoding="utf8") as output_file:
            output_file.write(reqif_content)
