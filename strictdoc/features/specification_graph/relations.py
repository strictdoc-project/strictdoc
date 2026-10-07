"""
StrictDoc adapter of the specification graph.

The adapter converts the traceability index into the input model of the
graph generator. A relation goes from the child node to the parent node.
The relation type is the relation role, or "Parent" for a relation without
a role.
"""

from typing import Dict, List, Optional, Set, Tuple, Union

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_from_file import DocumentFromFile
from strictdoc.backend.sdoc.models.model import SDocDocumentIF
from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.document_type import DocumentType
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.features.specification_graph.svg_graph.model import (
    Graph,
    GraphEdge,
    GraphNode,
    LayoutMode,
    RelationStyle,
)

PARENT_RELATION_TYPE = "Parent"

# Styles of the relation roles, assigned in the order of the sorted roles.
RELATION_ROLE_PALETTE = (
    RelationStyle(label="", color="#2563eb"),
    RelationStyle(label="", color="#9333ea", dash="6 3"),
    RelationStyle(label="", color="#c2410c", dash="2 3"),
    RelationStyle(label="", color="#15803d", dash="8 3 2 3"),
)


def build_documents_graph(
    traceability_index: TraceabilityIndex, link_renderer: LinkRenderer
) -> Graph:
    """
    Build the documents view: one node per document.

    A relation between two documents exists if a node of one document
    relates to a node of the other document. Relations with the same
    documents and the same type give one relation.
    """

    documents = _root_documents(traceability_index)
    nodes = tuple(
        GraphNode(
            node_id=_document_id(document_),
            title=document_.get_display_title(include_toc_number=False),
            link=_link(link_renderer, document_),
            details=_document_details(document_),
        )
        for document_ in documents
    )
    edge_keys: Dict[Tuple[str, str, str], None] = {}
    for document_ in documents:
        for node_ in _document_nodes(document_):
            child_document_ = node_.get_parent_or_including_document()
            for (
                parent_,
                role_,
            ) in traceability_index.get_parent_relations_with_roles(node_):
                parent_document_ = parent_.get_parent_or_including_document()
                if parent_document_ is child_document_:
                    continue
                edge_keys.setdefault(
                    (
                        _document_id(child_document_),
                        _document_id(parent_document_),
                        role_ or PARENT_RELATION_TYPE,
                    ),
                    None,
                )
    edges = tuple(
        GraphEdge(
            source_id=source_id_,
            target_id=target_id_,
            relation_type=relation_type_,
        )
        for source_id_, target_id_, relation_type_ in edge_keys
    )
    return Graph(
        mode=LayoutMode.LEVELS,
        root=nodes,
        edges=edges,
        relation_types=relation_styles(edges),
    )


def build_nodes_graph(
    traceability_index: TraceabilityIndex, link_renderer: LinkRenderer
) -> Graph:
    """
    Build the nodes view: documents and composite nodes (sections and
    composite requirements) are containers, the other nodes are leaves. The
    order of children follows the documents.
    """

    node_ids: Set[str] = set()
    root: List[GraphNode] = []
    for document_ in _root_documents(traceability_index):
        root.append(
            GraphNode(
                node_id=_document_id(document_),
                title=document_.get_display_title(include_toc_number=False),
                link=_link(link_renderer, document_),
                details=_document_details(document_),
                children=_children(
                    document_, document_, link_renderer, node_ids
                ),
            )
        )
    edges: List[GraphEdge] = []
    for document_ in _root_documents(traceability_index):
        for node_ in _document_nodes(document_):
            for (
                parent_,
                role_,
            ) in traceability_index.get_parent_relations_with_roles(node_):
                parent_id_ = _node_id(parent_)
                if parent_id_ not in node_ids:
                    continue
                edges.append(
                    GraphEdge(
                        source_id=_node_id(node_),
                        target_id=parent_id_,
                        relation_type=role_ or PARENT_RELATION_TYPE,
                    )
                )
    return Graph(
        mode=LayoutMode.STRUCTURE,
        root=tuple(root),
        edges=tuple(edges),
        relation_types=relation_styles(edges),
    )


def relation_styles(
    edges: Tuple[GraphEdge, ...] | List[GraphEdge],
) -> Dict[str, RelationStyle]:
    """
    Give each relation type a style. "Parent" is a black line, the roles
    take the palette in the order of their names.
    """

    styles: Dict[str, RelationStyle] = {}
    roles = sorted(
        {edge_.relation_type for edge_ in edges} - {PARENT_RELATION_TYPE}
    )
    if any(edge_.relation_type == PARENT_RELATION_TYPE for edge_ in edges):
        styles[PARENT_RELATION_TYPE] = RelationStyle(
            label=PARENT_RELATION_TYPE, color="#222222"
        )
    for index_, role_ in enumerate(roles):
        palette_style_ = RELATION_ROLE_PALETTE[
            index_ % len(RELATION_ROLE_PALETTE)
        ]
        styles[role_] = RelationStyle(
            label=role_, color=palette_style_.color, dash=palette_style_.dash
        )
    return styles


def _root_documents(
    traceability_index: TraceabilityIndex,
) -> List[SDocDocument]:
    """
    Return the documents in the project tree order. An included document
    (a fragment) is a part of the document that includes it.
    """

    assert traceability_index.document_tree is not None
    return [
        document_
        for document_ in traceability_index.document_tree.document_list
        if not document_.document_is_included()
    ]


def _document_nodes(document: SDocDocument) -> List[SDocNode]:
    """
    Return the nodes of a document in document order, with the nodes of the
    included documents. Text nodes are not a part of the graph.
    """

    result: List[SDocNode] = []
    stack: List[object] = list(reversed(_contents(document)))
    while len(stack) > 0:
        element_ = stack.pop()
        if isinstance(element_, SDocNode):
            if element_.is_text_node():
                continue
            result.append(element_)
        stack.extend(reversed(_contents(element_)))
    return result


def _contents(element: object) -> List[object]:
    if isinstance(element, DocumentFromFile):
        assert element.resolved_document is not None
        return list(element.resolved_document.section_contents)
    if isinstance(element, (SDocDocument, SDocNode)):
        return list(element.section_contents)
    return []


def _children(
    element: Union[SDocDocument, SDocNode, DocumentFromFile],
    document: SDocDocument,
    link_renderer: LinkRenderer,
    node_ids: Set[str],
) -> Tuple[GraphNode, ...]:
    children: List[GraphNode] = []
    for child_ in _contents(element):
        if isinstance(child_, DocumentFromFile):
            children.extend(
                _children(child_, document, link_renderer, node_ids)
            )
            continue
        if not isinstance(child_, SDocNode) or child_.is_text_node():
            continue
        node_id_ = _node_id(child_)
        node_ids.add(node_id_)
        children.append(
            GraphNode(
                node_id=node_id_,
                title=_node_title(child_),
                link=_link(link_renderer, child_),
                details=_node_details(child_, document),
                children=_children(child_, document, link_renderer, node_ids),
            )
        )
    return tuple(children)


def _document_id(document: SDocDocumentIF) -> str:
    return f"document-{document.reserved_mid}"


def _node_id(node: SDocNode) -> str:
    return f"node-{node.reserved_mid}"


def _node_title(node: SDocNode) -> str:
    title_ = node.get_display_title(include_toc_number=False)
    if title_ is not None and len(title_) > 0:
        return title_
    if node.reserved_uid is not None:
        return node.reserved_uid
    return node.node_type


def _link(
    link_renderer: LinkRenderer, element: Union[SDocDocument, SDocNode]
) -> Optional[str]:
    return link_renderer.render_node_link(element, None, DocumentType.DOCUMENT)


def _document_details(document: SDocDocument) -> Tuple[Tuple[str, str], ...]:
    details: List[Tuple[str, str]] = [("Kind", "Document")]
    if document.meta is not None:
        details.append(
            ("Path", document.meta.input_doc_rel_path.relative_path_posix)
        )
    return tuple(details)


def _node_details(
    node: SDocNode, document: SDocDocument
) -> Tuple[Tuple[str, str], ...]:
    details: List[Tuple[str, str]] = [("Kind", node.node_type)]
    if node.reserved_uid is not None:
        details.append(("UID", node.reserved_uid))
    details.append(
        ("Document", document.get_display_title(include_toc_number=False))
    )
    return tuple(details)
