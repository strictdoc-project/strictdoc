"""
Assign each document a (row, column) position for the Specification graph
diagram, from the cross-document relation edges produced by
`relations.get_document_relation_edges()`.

This is a pure, presentation-independent step: it does not know about SVG.
See developer/tasks/20260809_feat_specification_graph/task.md for the full
"highway" layout rule this implements.
"""

from typing import Dict, List, Sequence, Set, Tuple

from strictdoc.backend.sdoc.models.model import SDocDocumentIF
from strictdoc.features.specification_graph.relations import (
    DocumentRelationEdge,
)

# (row, column), both zero-based. Row 0 is the topmost row.
DocumentPosition = Tuple[int, int]


def compute_document_layout(
    documents: Sequence[SDocDocumentIF],
    edges: List[DocumentRelationEdge],
) -> Dict[SDocDocumentIF, DocumentPosition]:
    """
    documents: every document to place, in project tree order. Must
    include every document referenced by `edges` (both as a child and as
    a parent), since edges alone don't carry isolated documents.

    Row: row 0 is reserved for documents with no relations at all (neither
    outgoing nor incoming). A document with no outgoing edges (no
    parent-relation to another document) but at least one incoming edge
    (it is itself someone else's parent) is the top of a hierarchy and
    sits at row 1. Otherwise a document's row is
    1 + max(row(parent) for parent in its parent documents) — the
    "highway" rule: when a document has parent edges reaching different
    rows, the deepest chain wins.

    Column: left-to-right position within a row, following the order
    documents are given in (project tree order).
    """
    parents_of: Dict[SDocDocumentIF, List[SDocDocumentIF]] = {
        document_: [] for document_ in documents
    }
    documents_with_incoming_edges: Set[SDocDocumentIF] = set()
    for child_document_, parent_document_ in edges:
        parents_of[child_document_].append(parent_document_)
        documents_with_incoming_edges.add(parent_document_)

    row_of: Dict[SDocDocumentIF, int] = {}

    def compute_row(document_: SDocDocumentIF) -> int:
        if document_ in row_of:
            return row_of[document_]
        parent_documents = parents_of.get(document_, [])
        if len(parent_documents) == 0:
            row = 1 if document_ in documents_with_incoming_edges else 0
        else:
            row = 1 + max(compute_row(parent_) for parent_ in parent_documents)
        row_of[document_] = row
        return row

    for document_ in documents:
        compute_row(document_)

    documents_by_row: Dict[int, List[SDocDocumentIF]] = {}
    for document_ in documents:
        documents_by_row.setdefault(row_of[document_], []).append(document_)

    layout: Dict[SDocDocumentIF, DocumentPosition] = {}
    for row_, documents_in_row_ in documents_by_row.items():
        for column_, document_ in enumerate(documents_in_row_):
            layout[document_] = (row_, column_)

    return layout


def get_skip_edges(
    edges: List[DocumentRelationEdge],
    layout: Dict[SDocDocumentIF, DocumentPosition],
) -> List[DocumentRelationEdge]:
    """
    Return the edges that are not part of any document's winning "highway"
    chain: edges whose child and parent end up more than one row apart.
    These must remain visually distinguishable in the diagram (see
    task.md), since they indicate a document modeling inconsistency.
    """
    skip_edges: List[DocumentRelationEdge] = []
    for edge_ in edges:
        child_document_, parent_document_ = edge_
        child_row, _ = layout[child_document_]
        parent_row, _ = layout[parent_document_]
        if child_row - parent_row != 1:
            skip_edges.append(edge_)
    return skip_edges
