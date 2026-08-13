from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Iterator, List, Optional, Set, Union

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.model import SDocElementIF
from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.core.traceability_index_builder import TraceabilityIndexBuilder
from strictdoc.features.diff_and_changelog.project_diff_analyzer import (
    ProjectDiffAnalyzer,
    ProjectTreeDiffStats,
)
from strictdoc.helpers.parallelizer import NullParallelizer


class NodeClassification(str, Enum):
    UNCHANGED = "unchanged"
    AUTO_MERGED = "auto_merged"
    TRUE_CONFLICT = "true_conflict"
    DELETE_MODIFY_CONFLICT = "delete_modify_conflict"


CONFLICT_CLASSIFICATIONS = (
    NodeClassification.TRUE_CONFLICT,
    NodeClassification.DELETE_MODIFY_CONFLICT,
)


@dataclass
class NodeMergeResult:
    key: str
    classification: NodeClassification
    base_node: Optional[SDocNode] = None
    target_node: Optional[SDocNode] = None
    incoming_node: Optional[SDocNode] = None
    # Only meaningful for UNCHANGED/AUTO_MERGED: the value already decided
    # without user input. None means "this node is absent from the result".
    resolved_node: Optional[SDocNode] = None
    # Only meaningful for DELETE_MODIFY_CONFLICT: which side deleted the node.
    deleted_side: Optional[str] = None
    children: List["NodeMergeResult"] = field(default_factory=list)

    def is_conflict(self) -> bool:
        return self.classification in CONFLICT_CLASSIFICATIONS

    def resolve(self, decision: str) -> Optional[SDocNode]:
        """
        Decision is "target" or "incoming". For a plain TRUE_CONFLICT this
        picks that side's node. For a DELETE_MODIFY_CONFLICT, "target" means
        "the merged tree has no node here" (target's side is the deletion)
        and "incoming" means "keep incoming's edited node" -- this reuses
        target_node/incoming_node directly, which are already None on the
        deleted side, so no extra branching is needed here.
        """
        assert decision in ("target", "incoming"), decision
        return self.target_node if decision == "target" else self.incoming_node


@dataclass
class DocumentMergeResult:
    rel_path: str
    base_document: Optional[SDocDocument]
    target_document: Optional[SDocDocument]
    incoming_document: Optional[SDocDocument]
    node_results: List[NodeMergeResult]

    def iter_all(self) -> Iterator[NodeMergeResult]:
        def _walk(items: List[NodeMergeResult]) -> Iterator[NodeMergeResult]:
            for item in items:
                yield item
                yield from _walk(item.children)

        yield from _walk(self.node_results)

    @property
    def total_true_conflicts(self) -> int:
        return sum(1 for r in self.iter_all() if r.is_conflict())


@dataclass
class ThreeWayMergeResult:
    base_revision: str
    target_revision: str
    incoming_revision: str
    documents: List[DocumentMergeResult]

    @property
    def total_true_conflicts(self) -> int:
        return sum(doc.total_true_conflicts for doc in self.documents)

    def find_node_result(self, key: str) -> Optional[NodeMergeResult]:
        for document in self.documents:
            for result in document.iter_all():
                if result.key == key:
                    return result
        return None

    def find_document_result(
        self, key_prefix: str
    ) -> Optional[DocumentMergeResult]:
        for document in self.documents:
            if key_prefix.startswith(f"{document.rel_path}#"):
                return document
        return None


def build_index_and_stats(
    project_config: ProjectConfig,
) -> "tuple[TraceabilityIndex, ProjectTreeDiffStats]":
    """
    Parses one revision's document tree into an index + diff stats. Public
    (not `classify_documents`-internal) so that per-revision work can be
    run independently -- e.g. one thread per revision (SDOC-LLR-209) --
    before the three results are combined by
    `classify_documents_from_stats`.
    """
    traceability_index = TraceabilityIndexBuilder.create(
        project_config=project_config,
        parallelizer=NullParallelizer(),
        skip_source_files=True,
    )
    stats = ProjectDiffAnalyzer.analyze_document_tree(traceability_index)
    return traceability_index, stats


_Container = Union[SDocDocument, SDocNode]


def _child_nodes(container: _Container) -> List[SDocNode]:
    return [
        node
        for node in container.section_contents
        if isinstance(node, SDocNode)
    ]


def _all_descendant_nodes(container: _Container) -> Iterator[SDocNode]:
    """
    Flat pre-order walk of every SDocNode anywhere under `container`
    (document or node), matching the flat sequence classification needs --
    unlike `_child_nodes`, which only looks at one level.
    """
    for node in _child_nodes(container):
        yield node
        yield from _all_descendant_nodes(node)


def _classify_paired_with_base(
    base_node: SDocNode,
    target_node: Optional[SDocNode],
    incoming_node: Optional[SDocNode],
    *,
    base_stats: ProjectTreeDiffStats,
    target_stats: ProjectTreeDiffStats,
    incoming_stats: ProjectTreeDiffStats,
) -> NodeMergeResult:
    base_md5 = base_stats.get_md5_by_node(base_node)
    target_md5 = (
        target_stats.get_md5_by_node(target_node)
        if target_node is not None
        else None
    )
    incoming_md5 = (
        incoming_stats.get_md5_by_node(incoming_node)
        if incoming_node is not None
        else None
    )

    if target_node is not None and incoming_node is not None:
        if base_md5 == target_md5 == incoming_md5:
            classification = NodeClassification.UNCHANGED
            resolved = target_node
        elif base_md5 == target_md5:
            classification = NodeClassification.AUTO_MERGED
            resolved = incoming_node
        elif base_md5 == incoming_md5:
            classification = NodeClassification.AUTO_MERGED
            resolved = target_node
        elif target_md5 == incoming_md5:
            classification = NodeClassification.AUTO_MERGED
            resolved = target_node
        else:
            classification = NodeClassification.TRUE_CONFLICT
            resolved = None
        return NodeMergeResult(
            key="",
            classification=classification,
            base_node=base_node,
            target_node=target_node,
            incoming_node=incoming_node,
            resolved_node=resolved,
        )

    if target_node is None and incoming_node is None:
        return NodeMergeResult(
            key="",
            classification=NodeClassification.AUTO_MERGED,
            base_node=base_node,
            resolved_node=None,
        )

    if target_node is None:
        # Target deleted it; incoming still has it.
        if base_md5 == incoming_md5:
            return NodeMergeResult(
                key="",
                classification=NodeClassification.AUTO_MERGED,
                base_node=base_node,
                incoming_node=incoming_node,
                resolved_node=None,
            )
        return NodeMergeResult(
            key="",
            classification=NodeClassification.DELETE_MODIFY_CONFLICT,
            base_node=base_node,
            incoming_node=incoming_node,
            deleted_side="target",
        )

    # incoming_node is None: incoming deleted it; target still has it.
    if base_md5 == target_md5:
        return NodeMergeResult(
            key="",
            classification=NodeClassification.AUTO_MERGED,
            base_node=base_node,
            target_node=target_node,
            resolved_node=None,
        )
    return NodeMergeResult(
        key="",
        classification=NodeClassification.DELETE_MODIFY_CONFLICT,
        base_node=base_node,
        target_node=target_node,
        deleted_side="incoming",
    )


def _classify_unpaired_addition(
    target_node: SDocNode,
    incoming_node: Optional[SDocNode],
    target_stats: ProjectTreeDiffStats,
    incoming_stats: ProjectTreeDiffStats,
) -> NodeMergeResult:
    if incoming_node is None:
        # Present in target only; base never had it, incoming never added
        # anything matching it. Nothing to do -- target already has it.
        return NodeMergeResult(
            key="",
            classification=NodeClassification.AUTO_MERGED,
            target_node=target_node,
            resolved_node=target_node,
        )
    target_md5 = target_stats.get_md5_by_node(target_node)
    incoming_md5 = incoming_stats.get_md5_by_node(incoming_node)
    if target_md5 == incoming_md5:
        classification = NodeClassification.AUTO_MERGED
        resolved: Optional[SDocNode] = target_node
    else:
        # Both sides independently added something the matcher considers
        # "the same logical node" (by title/content similarity), but with
        # different content -- known edge case (inherited from the Diff
        # feature's matcher, not introduced here): this can occasionally
        # mis-pair two genuinely unrelated new nodes. Treated as a true
        # conflict since the matcher believes they're the same thing.
        classification = NodeClassification.TRUE_CONFLICT
        resolved = None
    return NodeMergeResult(
        key="",
        classification=classification,
        target_node=target_node,
        incoming_node=incoming_node,
        resolved_node=resolved,
    )


def _classify_document(
    rel_path: str,
    base_document: Optional[SDocDocument],
    target_document: Optional[SDocDocument],
    incoming_document: Optional[SDocDocument],
    *,
    base_stats: ProjectTreeDiffStats,
    target_stats: ProjectTreeDiffStats,
    incoming_stats: ProjectTreeDiffStats,
) -> DocumentMergeResult:
    node_results: List[NodeMergeResult] = []
    visited_target: Set[SDocNode] = set()
    visited_incoming: Set[SDocNode] = set()

    if base_document is not None:
        for base_node in _all_descendant_nodes(base_document):
            target_node = (
                target_stats.find_requirement(base_node)
                if target_document is not None
                else None
            )
            incoming_node = (
                incoming_stats.find_requirement(base_node)
                if incoming_document is not None
                else None
            )
            if target_node is not None:
                visited_target.add(target_node)
            if incoming_node is not None:
                visited_incoming.add(incoming_node)
            node_results.append(
                _classify_paired_with_base(
                    base_node,
                    target_node,
                    incoming_node,
                    base_stats=base_stats,
                    target_stats=target_stats,
                    incoming_stats=incoming_stats,
                )
            )

    if target_document is not None:
        for target_node in _all_descendant_nodes(target_document):
            if target_node in visited_target:
                continue
            incoming_candidate: Optional[SDocNode] = None
            if incoming_document is not None:
                candidate = incoming_stats.find_requirement(target_node)
                if candidate is not None and candidate not in visited_incoming:
                    base_match = (
                        base_stats.find_requirement(candidate)
                        if base_document is not None
                        else None
                    )
                    if base_match is None:
                        incoming_candidate = candidate
            if incoming_candidate is not None:
                visited_incoming.add(incoming_candidate)
            node_results.append(
                _classify_unpaired_addition(
                    target_node,
                    incoming_candidate,
                    target_stats,
                    incoming_stats,
                )
            )

    if incoming_document is not None:
        for incoming_node in _all_descendant_nodes(incoming_document):
            if incoming_node in visited_incoming:
                continue
            node_results.append(
                NodeMergeResult(
                    key="",
                    classification=NodeClassification.AUTO_MERGED,
                    incoming_node=incoming_node,
                    resolved_node=incoming_node,
                )
            )

    for index, result in enumerate(node_results):
        result.key = f"{rel_path}#{index}"

    return DocumentMergeResult(
        rel_path=rel_path,
        base_document=base_document,
        target_document=target_document,
        incoming_document=incoming_document,
        node_results=node_results,
    )


def classify_documents(
    *,
    base_project_config: ProjectConfig,
    target_project_config: ProjectConfig,
    incoming_project_config: ProjectConfig,
    base_revision: str,
    target_revision: str,
    incoming_revision: str,
) -> ThreeWayMergeResult:
    _, base_stats = build_index_and_stats(base_project_config)
    target_index, target_stats = build_index_and_stats(target_project_config)
    incoming_index, incoming_stats = build_index_and_stats(
        incoming_project_config
    )

    assert target_index.document_tree is not None
    assert incoming_index.document_tree is not None

    return classify_documents_from_stats(
        base_stats=base_stats,
        target_stats=target_stats,
        incoming_stats=incoming_stats,
        base_revision=base_revision,
        target_revision=target_revision,
        incoming_revision=incoming_revision,
    )


def classify_documents_from_stats(
    *,
    base_stats: ProjectTreeDiffStats,
    target_stats: ProjectTreeDiffStats,
    incoming_stats: ProjectTreeDiffStats,
    base_revision: str,
    target_revision: str,
    incoming_revision: str,
) -> ThreeWayMergeResult:
    """
    The combination half of `classify_documents`, taking already-built
    per-revision stats instead of building them itself -- lets a caller
    (SDOC-LLR-209) build the three revisions' stats concurrently (each is
    fully independent) and combine them here once all three are ready.
    """
    all_rel_paths = (
        set(base_stats.map_rel_paths_to_docs.keys())
        | set(target_stats.map_rel_paths_to_docs.keys())
        | set(incoming_stats.map_rel_paths_to_docs.keys())
    )

    documents = [
        _classify_document(
            rel_path,
            base_stats.map_rel_paths_to_docs.get(rel_path),
            target_stats.map_rel_paths_to_docs.get(rel_path),
            incoming_stats.map_rel_paths_to_docs.get(rel_path),
            base_stats=base_stats,
            target_stats=target_stats,
            incoming_stats=incoming_stats,
        )
        for rel_path in sorted(all_rel_paths)
    ]

    return ThreeWayMergeResult(
        base_revision=base_revision,
        target_revision=target_revision,
        incoming_revision=incoming_revision,
        documents=documents,
    )


def compute_parent_key_map(
    document_merge_result: DocumentMergeResult,
) -> Dict[str, Optional[str]]:
    """
    Each result's immediate logical parent's key (None means top-level),
    resolved by walking whichever side's tree actually anchors that result
    -- target's, else base's, else incoming's -- rather than raw
    target-tree object identity: a node's ancestor chain may be entirely
    absent from target (e.g. a whole section deleted on target while one of
    its nodes was independently modified on incoming), and the object that
    represents "this node's parent" then lives in the base or incoming
    parse tree instead -- a different object graph than target's. Looking
    up `anchor_node.parent` in the *same* tree the anchor itself came from
    never crosses trees mid-hop, so this stays correct however many
    ancestors in a row are missing from target.

    Shared by `splice_document` (structural rebuild) and
    `SyncMergeService.place_after` (validating that a drag-and-drop
    placement's target is an actual sibling), so both agree on what
    "sibling" means.
    """
    node_results = document_merge_result.node_results
    target_document = document_merge_result.target_document
    incoming_document = document_merge_result.incoming_document
    base_document = document_merge_result.base_document

    def _anchor(result: NodeMergeResult) -> "tuple[Optional[SDocNode], str]":
        if result.target_node is not None:
            return result.target_node, "target"
        if result.base_node is not None:
            return result.base_node, "base"
        return result.incoming_node, "incoming"

    source_document_by_tree: Dict[str, Optional[SDocDocument]] = {
        "target": target_document,
        "base": base_document,
        "incoming": incoming_document,
    }
    result_by_node_id_by_tree: Dict[str, Dict[int, NodeMergeResult]] = {
        "target": {},
        "base": {},
        "incoming": {},
    }
    for result in node_results:
        if result.target_node is not None:
            result_by_node_id_by_tree["target"][id(result.target_node)] = result
        if result.base_node is not None:
            result_by_node_id_by_tree["base"][id(result.base_node)] = result
        if result.incoming_node is not None:
            result_by_node_id_by_tree["incoming"][id(result.incoming_node)] = (
                result
            )

    parent_key_of: Dict[str, Optional[str]] = {}
    for result in node_results:
        anchor_node, tree = _anchor(result)
        if anchor_node is None:
            parent_key_of[result.key] = None
            continue
        parent_node = anchor_node.parent
        if parent_node is source_document_by_tree[tree]:
            parent_key_of[result.key] = None
            continue
        parent_result = result_by_node_id_by_tree[tree].get(id(parent_node))
        parent_key_of[result.key] = (
            parent_result.key if parent_result is not None else None
        )

    return parent_key_of


PLACEMENT_START = "__start__"


def order_children_by_parent_key(
    document_merge_result: DocumentMergeResult,
    placements: Optional[Dict[str, str]] = None,
) -> "tuple[Dict[str, Optional[str]], Dict[Optional[str], List[NodeMergeResult]]]":
    """
    Default sibling order (see `compute_parent_key_map`), with any
    `placements` (result key -> sibling key to insert immediately after,
    or PLACEMENT_START) applied on top. Shared by `splice_document`
    (building the actual composite tree) and the conflicts screen's own
    node listing (`GitConflictsViewObject`), so a drag-and-drop placement
    shows up in the review screen exactly where it will actually end up
    once committed.
    """
    parent_key_of = compute_parent_key_map(document_merge_result)

    children_by_parent_key: Dict[Optional[str], List[NodeMergeResult]] = {}
    for result in document_merge_result.node_results:
        children_by_parent_key.setdefault(parent_key_of[result.key], []).append(
            result
        )

    if placements:
        result_by_key = {
            result.key: result for result in document_merge_result.node_results
        }
        for key, after_key in placements.items():
            siblings = children_by_parent_key.get(parent_key_of.get(key))
            moved = result_by_key.get(key)
            if siblings is None or moved is None or moved not in siblings:
                continue
            siblings.remove(moved)
            if after_key == PLACEMENT_START:
                siblings.insert(0, moved)
                continue
            after_index = next(
                (
                    index
                    for index, sibling in enumerate(siblings)
                    if sibling.key == after_key
                ),
                None,
            )
            siblings.insert(
                after_index + 1 if after_index is not None else len(siblings),
                moved,
            )

    return parent_key_of, children_by_parent_key


def splice_document(
    document_merge_result: DocumentMergeResult,
    allocations: Dict[str, str],
    placements: Optional[Dict[str, str]] = None,
) -> Optional[SDocDocument]:
    """
    Builds the resolved SDocDocument for a touched document.

    An ancestor whose own change auto-resolved to "removed" is forced back
    into existence (using incoming's, else target's, else base's copy of
    that ancestor) whenever any of its descendants survives the merge --
    otherwise a resolved child would have no container to nest in.

    `placements` (result key -> the sibling result key it should be
    inserted immediately after, or `PLACEMENT_START` for "before all
    siblings") lets a genuinely-new addition (no base_node) be repositioned
    among its default-ordered siblings -- e.g. two independent new
    top-level sections added by each side otherwise land in a fixed order
    (existing content, then target-only additions, then incoming-only
    additions) with no way for the user to choose where their own new
    content ends up relative to the other side's.

    Returns None if the document needs no changes from target's raw content
    (nothing to materialize -- the caller should keep target's blob as-is,
    or, if target never had this document at all and nothing survived from
    incoming either, no file needs to be added).
    """
    node_results = document_merge_result.node_results
    target_document = document_merge_result.target_document
    incoming_document = document_merge_result.incoming_document

    composite_base = (
        target_document if target_document is not None else incoming_document
    )
    if composite_base is None:
        return None

    def _final_node(result: NodeMergeResult) -> Optional[SDocNode]:
        if result.is_conflict():
            decision = allocations.get(result.key)
            assert decision is not None, (
                f"Node {result.key} was not resolved before materialization."
            )
            return result.resolve(decision)
        return result.resolved_node

    _parent_key_of, children_by_parent_key = order_children_by_parent_key(
        document_merge_result, placements
    )

    final_by_key: Dict[str, Optional[SDocNode]] = {}

    def _resolve_final(result: NodeMergeResult) -> Optional[SDocNode]:
        if result.key in final_by_key:
            return final_by_key[result.key]
        final_by_key[result.key] = None  # cycle guard; real cycles can't occur
        any_child_survives = any(
            _resolve_final(child) is not None
            for child in children_by_parent_key.get(result.key, [])
        )
        own_final = _final_node(result)
        if own_final is None and any_child_survives:
            own_final = (
                result.incoming_node or result.target_node or result.base_node
            )
        final_by_key[result.key] = own_final
        return own_final

    for result in node_results:
        _resolve_final(result)

    if not any(
        final_by_key[result.key] is not result.target_node
        for result in node_results
    ):
        return None

    composite_document = deepcopy(composite_base)

    def _build(result: NodeMergeResult) -> Optional[SDocNode]:
        final = final_by_key[result.key]
        if final is None:
            return None
        new_node = deepcopy(final)
        if new_node.ng_document_reference is not None:
            new_node.ng_document_reference.set_document(composite_document)
        children: List[SDocElementIF] = []
        for child_result in children_by_parent_key.get(result.key, []):
            built = _build(child_result)
            if built is None:
                continue
            built.parent = new_node
            children.append(built)
        new_node.section_contents = children
        return new_node

    top_level: List[SDocElementIF] = []
    for result in children_by_parent_key.get(None, []):
        built = _build(result)
        if built is None:
            continue
        built.parent = composite_document
        top_level.append(built)

    composite_document.section_contents = top_level
    return composite_document
