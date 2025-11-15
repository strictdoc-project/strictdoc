from dataclasses import dataclass

from tree_sitter import Node


@dataclass
class ByteRange:
    start: int
    end: int

    @classmethod
    def create_from_ts_node(cls, node: Node) -> "ByteRange":
        return cls(
            start=node.start_byte,
            end=node.end_byte,
        )
