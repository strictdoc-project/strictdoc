from strictdoc.backend.sdoc_source_code.models.source_file_info import (
    SourceFileTraceabilityInfo,
)
from strictdoc.backend.sdoc_source_code.models.source_node import SourceNode


class SourceWriter:
    def write(
        self,
        trace_info: SourceFileTraceabilityInfo,
        rewrites: dict[SourceNode, bytes],
    ) -> bytes:
        src = trace_info.file_bytes

        output = bytearray()
        prev_end = 0

        for source_node_ in trace_info.source_nodes:
            if source_node_ not in rewrites:
                continue

            rewrite = rewrites[source_node_]
            output += src[prev_end : source_node_.start_byte]

            output += rewrite

            prev_end = source_node_.end_byte

        # Possible trailing whitespace after last token.
        if prev_end < len(src):
            output += src[prev_end:]

        return bytes(output)
