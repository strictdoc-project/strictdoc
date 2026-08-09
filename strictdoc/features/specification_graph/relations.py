"""
Extract cross-document relation edges from a TraceabilityIndex.

This is a pure, presentation-independent step: it only answers "does
document A have a node-level Parent/Child relation into document B", not
how that fact should be laid out or rendered. See
developer/tasks/20260809_feat_specification_graph/task.md for the full
feature spec.
"""

from typing import List, Set, Tuple

from strictdoc.backend.sdoc.models.model import SDocDocumentIF
from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.core.traceability_index import TraceabilityIndex

DocumentRelationEdge = Tuple[SDocDocumentIF, SDocDocumentIF]


def get_document_relation_edges(
    traceability_index: TraceabilityIndex,
) -> List[DocumentRelationEdge]:
    """
    Return the unique (child_document, parent_document) edges of the
    project's document graph.

    An edge exists whenever any node in child_document has a relation
    (any role) to a node in parent_document, regardless of how many such
    node-level relations exist between the two documents. Relations where
    both endpoints are in the same document are not edges. The result
    order is deterministic (project tree order, then per-document node
    order), but is not itself the diagram row/column layout order — that
    is a separate, later step.
    """
    edges: List[DocumentRelationEdge] = []
    seen_edges: Set[DocumentRelationEdge] = set()

    for document_ in traceability_index.document_tree.document_list:
        if document_.document_is_included():
            continue

        document_iterator = traceability_index.get_document_iterator(
            document_
        )
        for node_, _ in document_iterator.all_content(print_fragments=False):
            if not isinstance(node_, SDocNode):
                continue

            child_document = node_.get_document()
            if child_document is None:
                continue

            for parent_node_ in traceability_index.get_parent_requirements(
                node_
            ):
                parent_document = parent_node_.get_document()
                if parent_document is None:
                    continue
                if parent_document is child_document:
                    continue

                edge = (child_document, parent_document)
                if edge in seen_edges:
                    continue
                seen_edges.add(edge)
                edges.append(edge)

    return edges
