from strictdoc.backend.sdoc_source_code.models.source_file_info import (
    SourceFileTraceabilityInfo,
)
from strictdoc.backend.sdoc_source_code.models.source_node import SourceNode


class SourceWriter:
    def write(
        self,
        trace_info: SourceFileTraceabilityInfo,
        rewrites: dict[SourceNode, bytes],
        file_bytes: bytes,
    ) -> bytes:
        output = bytearray()
        prev_end = 0

        for source_node_ in trace_info.source_nodes:
            if source_node_.comment_byte_range is None:
                continue

            if source_node_ not in rewrites:
                continue

            rewrite = rewrites[source_node_]
            output += file_bytes[
                prev_end : source_node_.comment_byte_range.start
            ]

            output += rewrite

            prev_end = source_node_.comment_byte_range.end

        # Possible trailing whitespace after last token.
        if prev_end < len(file_bytes):
            output += file_bytes[prev_end:]

        return bytes(output)
