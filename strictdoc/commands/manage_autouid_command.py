import sys
from typing import Dict

from strictdoc.backend.sdoc.errors.document_tree_error import DocumentTreeError
from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.backend.sdoc.writer import SDWriter
from strictdoc.backend.sdoc_source_code.marker_writer import MarkerWriter
from strictdoc.backend.sdoc_source_code.models.source_file_info import (
    SourceFileTraceabilityInfo,
)
from strictdoc.backend.sdoc_source_code.source_writer import SourceWriter
from strictdoc.core.analyzers.document_stats import (
    DocumentStats,
    DocumentTreeStats,
)
from strictdoc.core.analyzers.document_uid_analyzer import DocumentUIDAnalyzer
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.core.traceability_index_builder import TraceabilityIndexBuilder
from strictdoc.helpers.parallelizer import Parallelizer
from strictdoc.helpers.sha256 import get_random_sha256, get_sha256, is_sha256
from strictdoc.helpers.string import (
    create_safe_acronym,
)


def generate_code_hash(
    *, project: bytes, file_path: bytes, instance: bytes, code: bytes
) -> bytes:
    """
    Generate hash for drift detection as suggested by Linux kernel requirements template:

    "${PROJECT}${FILE_PATH}${INSTANCE}${CODE}" | sha256sum".
    """

    assert isinstance(project, bytes)
    assert isinstance(file_path, bytes)
    assert isinstance(instance, bytes)
    assert isinstance(code, bytes)

    hash_input = project + file_path + instance + code
    return bytes(get_sha256(hash_input), encoding="utf8")


class ManageAutoUIDCommand:
    @staticmethod
    def execute(
        *, project_config: ProjectConfig, parallelizer: Parallelizer
    ) -> None:
        """
        @relation(SDOC-SRS-85, scope=function)
        """

        # FIXME: Traceability Index is coupled with HTML output.
        project_config.export_output_html_root = "NOT_RELEVANT"

        try:
            traceability_index: TraceabilityIndex = (
                TraceabilityIndexBuilder.create(
                    project_config=project_config,
                    parallelizer=parallelizer,
                )
            )
        except DocumentTreeError as exc:
            print(exc.to_print_message())  # noqa: T201
            sys.exit(1)

        document_tree_stats: DocumentTreeStats = (
            DocumentUIDAnalyzer.analyze_document_tree(traceability_index)
        )

        if project_config.autouuid_include_sections:
            document_stats_: DocumentStats
            for document_stats_ in document_tree_stats.single_document_stats:
                document_acronym = create_safe_acronym(
                    document_stats_.document.title
                )
                for section in document_stats_.sections_without_uid:
                    auto_uid = document_tree_stats.get_auto_section_uid(
                        document_acronym, section
                    )
                    section.reserved_uid = auto_uid

        for (
            prefix,
            prefix_requirements,
        ) in document_tree_stats.requirements_per_prefix.items():
            next_number = document_tree_stats.get_next_requirement_uid_number(
                prefix
            )

            for requirement in prefix_requirements.requirements_no_uid:
                requirement_prefix = requirement.get_prefix()
                requirement_uid = f"{requirement_prefix}{next_number}"
                requirement.set_field_value(
                    field_name="UID",
                    form_field_index=0,
                    value=requirement_uid,
                )
                next_number += 1

        for (
            trace_info_
        ) in traceability_index.get_file_traceability_index().trace_infos:
            ManageAutoUIDCommand._rewrite_source_file(
                trace_info_, project_config
            )

        for document in traceability_index.document_tree.document_list:
            assert document.meta is not None

            # Most recently, we parse JUnit XML, Gcov JSON files or SDoc
            # documents generated from source code comments.
            # These must not be written back.
            if (
                not document.meta.document_filename.endswith(".sdoc")
                or document.autogen
            ):
                continue

            document_content = SDWriter(project_config).write(document)
            document_meta = document.meta
            with open(
                document_meta.input_doc_full_path, "w", encoding="utf8"
            ) as output_file:
                output_file.write(document_content)

    @staticmethod
    def _rewrite_source_file(
        trace_info: SourceFileTraceabilityInfo,
        project_config: ProjectConfig,
    ) -> None:
        """
        NOTE: This only updates the source code with the new calculated value.
              All links in the graph database and links in the search index are
              not modified for now.
        """

        assert trace_info.source_file is not None
        # FIXME: These conditions for skipping the writes may be insufficient.
        if (
            not trace_info.source_file.in_doctree_source_file_rel_path_posix.endswith(
                ".c"
            )
            or not trace_info.source_file.is_referenced
        ):
            return

        with open(trace_info.source_file.full_path, "rb") as source_file_:
            file_bytes = source_file_.read()

        file_rewrites = {}
        for source_node_ in trace_info.source_nodes:
            function = source_node_.function
            if function is None or function.code_byte_range is None:
                continue

            # Not all source readers create rewritable byte ranges. There is
            # nothing to rewrite for such nodes. Skipping them here.
            if source_node_.comment_byte_range is None:
                continue

            if "SPDX-Req-ID" not in source_node_.fields:
                continue

            node_rewrites: Dict[str, str] = {}

            # If the source node has the SPDX-REQ-ID but it is not yet a valid
            # SHA256 identifier, create one and patch the node.
            existing_req_id = source_node_.fields["SPDX-Req-ID"]
            if not is_sha256(existing_req_id):
                hash_spdx_id_str = get_random_sha256()
                hash_spdx_id = bytes(hash_spdx_id_str, encoding="utf8")

                if (sdoc_node_ := source_node_.sdoc_node) is not None:
                    sdoc_node_.set_field_value(
                        field_name="MID",
                        form_field_index=0,
                        value=hash_spdx_id_str,
                    )
                node_rewrites["SPDX-Req-ID"] = hash_spdx_id_str

            existing_req_hash = source_node_.fields.get("SPDX-REQ-HKey", None)
            if existing_req_hash is not None and existing_req_hash != "TBD":
                # FIXME: Shall we assume that a HKey can only be TBD, a
                #        valid SHA256, or simply be missing?
                assert is_sha256(existing_req_hash), existing_req_hash
            else:
                assert source_node_.sdoc_node is not None
                sdoc_node: SDocNode = source_node_.sdoc_node

                # FILE_PATH: The file the code resides in, relative to the root of the project repository.
                file_path = bytes(
                    trace_info.source_file.in_doctree_source_file_rel_path_posix,
                    encoding="utf8",
                )

                # INSTANCE:	The requirement template instance, minus tags with hash strings.
                instance_bytes = bytearray()
                for (
                    field_name_,
                    field_values_,
                ) in sdoc_node.ordered_fields_lookup.items():
                    if field_name_ in (
                        "MID",
                        "HASH",
                        "SPDX-Req-ID",
                        "SPDX-Req-HKey",
                    ):
                        continue
                    for field_value_ in field_values_:
                        instance_bytes += bytes(
                            field_value_.get_text_value(), encoding="utf8"
                        )

                # CODE: The code that the SPDX-Req applies to.
                code = file_bytes[
                    function.code_byte_range.start : function.code_byte_range.end
                ]

                # This is important for Windows. Otherwise, the hash key will be calculated incorrectly.
                code = code.replace(b"\r\n", b"\n")

                hash_spdx_hash = generate_code_hash(
                    project=bytes(
                        project_config.project_title, encoding="utf8"
                    ),
                    file_path=file_path,
                    instance=bytes(instance_bytes),
                    code=code,
                )
                hash_spdx_hash_str = hash_spdx_hash.decode("utf8")
                sdoc_node.set_field_value(
                    field_name="HASH",
                    form_field_index=0,
                    value=hash_spdx_hash_str,
                )

            if len(node_rewrites) > 0:
                patched_node = MarkerWriter().write(
                    source_node_,
                    rewrites={
                        "SPDX-Req-ID": hash_spdx_id,
                        "SPDX-Req-HKey": hash_spdx_hash,
                    },
                    comment_file_bytes=file_bytes[
                        source_node_.comment_byte_range.start : source_node_.comment_byte_range.end
                    ],
                )
                file_rewrites[source_node_] = patched_node

        source_writer = SourceWriter()
        output_string = source_writer.write(
            trace_info, rewrites=file_rewrites, file_bytes=file_bytes
        )

        with open(trace_info.source_file.full_path, "wb") as source_file_:
            source_file_.write(output_string)
