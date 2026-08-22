"""
Chunk slicing for lazily-loaded document content.
"""

from dataclasses import dataclass
from typing import List, Sequence, Tuple

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
    node order at render time. node_mids is the complete client-side lookup
    metadata for this frame. It must include nodes omitted from TOC (for
    example untitled TEXT nodes), because operation targets are identified by
    MID rather than by TOC membership.

    anchors mirrors node_mids position-for-position, giving each node's
    rendered URL fragment (see LinkRenderer.render_local_anchor()) instead of
    its MID. The lazy placeholder template stamps this list onto the frame
    (see document_chunk_lazy_placeholder.jinja.html) so
    toc_chunk_navigation.js can resolve which unloaded chunk owns a deep-link
    target even for a node with no TOC entry (a node without a TITLE is
    omitted from the TOC - see SDocDocumentIterator.table_of_contents() -
    but still gets a real anchor here, independent of its title).
    """

    index: int
    first_node_mid: str
    size: int
    node_mids: Sequence[str]
    anchors: Sequence[str]


def slice_chunks(
    node_entries: Sequence[Tuple[str, str]], chunk_size: int
) -> List[DocumentChunk]:
    """
    node_entries holds (node_mid, anchor) pairs in document order.
    """
    assert chunk_size > 0, chunk_size
    chunks: List[DocumentChunk] = []
    for chunk_start in range(0, len(node_entries), chunk_size):
        chunk_entries = node_entries[chunk_start : chunk_start + chunk_size]
        chunks.append(
            DocumentChunk(
                index=len(chunks),
                first_node_mid=chunk_entries[0][0],
                size=len(chunk_entries),
                node_mids=[entry[0] for entry in chunk_entries],
                anchors=[entry[1] for entry in chunk_entries],
            )
        )
    return chunks
