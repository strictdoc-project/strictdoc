from typing import Any

from strictdoc.backend.sdoc_source_code.models.source_node import SourceNode


class MarkerWriter:
    def write(
        self,
        source_node: SourceNode,
        rewrites: dict[Any, bytes],
        comment_file_bytes: bytes,
    ) -> bytes:
        output = bytearray()
        prev_end = 0

        for field_name_ in source_node.fields.keys():
            if field_name_ not in rewrites:
                continue

            rewrite = rewrites[field_name_]
            location = source_node.fields_locations[field_name_]

            output += comment_file_bytes[prev_end : location[0]]

            output += bytes(field_name_, encoding="utf8") + b": "
            output += rewrite

            prev_end = location[1]

        # Possible trailing whitespace after last token.
        if prev_end < len(comment_file_bytes):
            output += comment_file_bytes[prev_end:]

        return bytes(output)
