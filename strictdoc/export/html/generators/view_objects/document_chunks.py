"""
Chunk slicing for lazily-loaded document content.
"""

from dataclasses import dataclass
from typing import List, Sequence

#
# How many document nodes are rendered per lazily-loaded chunk.
#
CHUNK_SIZE = 100


@dataclass
class DocumentChunk:
    """
    A window into a document's node sequence.

    first_node_mid is a cursor into the document's node sequence: chunks are
    recomputed per request, so the cursor MID is resolved against the current
    node order at render time. size is the requested window length.
    """

    index: int
    first_node_mid: str
    size: int


def slice_chunks(
    node_mids: Sequence[str], chunk_size: int
) -> List[DocumentChunk]:
    assert chunk_size > 0, chunk_size
    chunks: List[DocumentChunk] = []
    for chunk_start in range(0, len(node_mids), chunk_size):
        chunk_mids = node_mids[chunk_start : chunk_start + chunk_size]
        chunks.append(
            DocumentChunk(
                index=len(chunks),
                first_node_mid=chunk_mids[0],
                size=len(chunk_mids),
            )
        )
    return chunks
