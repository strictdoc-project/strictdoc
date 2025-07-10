"""
@relation(SDOC-SRS-72, scope=file)
"""

# mypy: disable-error-code="arg-type,no-untyped-def"
import os
from pathlib import Path

from reqif.reqif_bundle import ReqIFZBundle
from reqif.unparser import ReqIFUnparser, ReqIFZUnparser

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
        reqifz: bool,
    ):
        Path(output_reqif_root).mkdir(parents=True, exist_ok=True)

        if project_config.reqif_profile == ReqIFProfile.P01_SDOC:
            reqif_bundle = P01_SDocToReqIFObjectConverter.convert_document_tree(
                document_tree=traceability_index.document_tree,
                multiline_is_xhtml=project_config.reqif_multiline_is_xhtml,
                enable_mid=project_config.reqif_enable_mid,
            )
        else:
            raise NotImplementedError(
                f"Requirements profile does not implement the ReqIF export yet: "
                f"{project_config.reqif_profile}."
            )

        output_file_path: str
        if not reqifz:
            output_file_path = os.path.join(output_reqif_root, "output.reqif")
            reqif_content: str = ReqIFUnparser.unparse(reqif_bundle)
            with open(output_file_path, "w", encoding="utf8") as output_file:
                output_file.write(reqif_content)
        else:
            output_file_path = os.path.join(output_reqif_root, "output.reqifz")
            reqifz_bundle = ReqIFZBundle(
                reqif_bundles={"document_tree.reqif": reqif_bundle},
                attachments={},
            )
            reqifz_content_bytes = ReqIFZUnparser.unparse(reqifz_bundle)
            with open(output_file_path, "wb") as output_file:
                output_file.write(reqifz_content_bytes)
