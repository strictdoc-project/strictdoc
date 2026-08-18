import json
import os
from copy import deepcopy
from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional

from strictdoc.backend.sdoc.writer import SDWriter
from strictdoc.core.file_system.document_finder import get_document_extensions
from strictdoc.core.project_config import ProjectConfig
from strictdoc.features.diff_and_changelog.git_client import GitClient
from strictdoc.features.diff_and_changelog.project_diff_analyzer import (
    ProjectTreeDiffStats,
)
from strictdoc.features.git_workspace.three_way_merge_analyzer import (
    PLACEMENT_START,
    ThreeWayMergeResult,
    build_index_and_stats,
    classify_documents_from_stats,
    compute_parent_key_map,
    splice_document,
)


@dataclass
class SyncMergeMeta:
    branch: str
    live_branch_sha_at_start: str
    target_branch: str
    base_revision: str
    target_revision: str
    incoming_revision: str
    allocations: Dict[str, str] = field(default_factory=dict)
    # A moved node's key -> the sibling key it should be inserted
    # immediately after, or PLACEMENT_START for "before all siblings".
    # Only applies to genuinely-new additions (no base_node); see
    # SyncMergeService.place_after.
    placements: Dict[str, str] = field(default_factory=dict)
    # Per SDOC-SRS-224: paths (relative to the repo root) that changed on
    # either side (base->target or base->incoming) and are not in a
    # readable StrictDoc format -- synchronization only merges document
    # content through the 3-way classifier, so any such path would
    # otherwise be silently taken from target alone or dropped entirely.
    non_document_changed_paths: List[str] = field(default_factory=list)


@dataclass
class SyncPublishResult:
    success: bool
    error_message: Optional[str] = None


def _project_config_for_worktree(
    project_config: ProjectConfig, git_client: GitClient
) -> ProjectConfig:
    assert project_config.input_paths is not None
    project_config_copy: ProjectConfig = deepcopy(project_config)
    export_input_rel_path = os.path.relpath(
        project_config.input_paths[0], os.getcwd()
    )
    project_config_copy.input_paths = [
        os.path.join(git_client.path_to_git_root, export_input_rel_path)
    ]
    return project_config_copy


def _build_stats_for_revision(
    project_config: ProjectConfig, revision: str
) -> ProjectTreeDiffStats:
    """
    One revision's worktree checkout + parse (SDOC-LLR-210: sparse,
    doc-paths-only checkout; SDOC-LLR-211: reused across calls, keyed by
    revision, rather than a fresh checkout torn down every time -- this is
    what lets PickleCache's document cache actually hit on repeated
    synchronizations against the same revision).

    Deliberately sequential, not parallelized across the three revisions:
    an earlier attempt at running this concurrently (one thread per
    revision) kept uncovering more shared mutable state one fix at a time
    -- the git worktree registry, .git/config, and finally the on-disk
    dependency cache used by TraceabilityIndexBuilder (keyed by the live
    project's cache dir, which every worktree-scoped ProjectConfig copy
    still points at, since only input_paths gets redirected per worktree,
    not the cache dir). Given that pattern, the sparse checkout on its own
    already removes the dominant cost (materializing the full working
    tree); parallelizing on top of it was reverted rather than chasing
    further races.
    """
    with GitClient.create_cached_repo_from_local_copy(
        revision, project_config, sparse_doc_paths_only=True
    ) as git_client:
        worktree_project_config = _project_config_for_worktree(
            project_config, git_client
        )
        _, stats = build_index_and_stats(worktree_project_config)
        return stats


def _find_non_document_changes(
    live_client: GitClient,
    project_config: ProjectConfig,
    base_revision: str,
    target_revision: str,
    incoming_revision: str,
) -> List[str]:
    """
    SDOC-SRS-224: any path changed on either side relative to base that
    does not end with a readable StrictDoc format extension -- the same
    canonical extension list DocumentFinder itself scans with
    (`get_document_extensions`), so this never drifts out of sync with
    what StrictDoc actually reads as a document.
    """
    readable_extensions = tuple(get_document_extensions(project_config))
    changed_paths = set(
        live_client.get_changed_paths(base_revision, target_revision)
    )
    changed_paths.update(
        live_client.get_changed_paths(base_revision, incoming_revision)
    )
    return sorted(
        path for path in changed_paths if not path.endswith(readable_extensions)
    )


class SyncMergeService:
    """
    Drives Synchronize as a single custom 3-way structural merge (base =
    merge_base(target, incoming), target = target branch tip, incoming =
    the live branch's tip), never git's own rebase/merge conflict machinery
    -- see three_way_merge_analyzer.py for why and the classification
    semantics. Node/section resolution decisions are the only thing
    persisted (`SyncMergeMeta.allocations`); the classification itself is
    always recomputed fresh from the pinned revisions (cheap, and avoids
    ever having to serialize parsed SDocNode object graphs to disk).
    """

    # Per SDOC-SRS-223: a single-slot cache of the most recently computed
    # classification, keyed by the exact (base, target, incoming) revision
    # triple it came from. Revisions are immutable git SHAs, so a cache hit
    # is always correct -- there is nothing to invalidate. One Git
    # conflicts action commonly spans several requests against the same
    # triple (e.g. resolve a node, then the redirect that re-renders the
    # screen); without this, each of those requests would redo the same
    # three checkouts+parses from scratch. A *different* triple (a new
    # Synchronize) naturally evicts the old entry -- the single-active-sync
    # design (one worktree, one meta file) means only one triple is ever
    # relevant at a time.
    _classification_cache: Optional[
        "tuple[tuple[str, str, str], ThreeWayMergeResult]"
    ] = None

    @staticmethod
    def get_worktree_path(project_config: ProjectConfig) -> str:
        return os.path.join(
            project_config.get_path_to_cache_dir(), "git", "sync_worktree"
        )

    @staticmethod
    def get_meta_path(project_config: ProjectConfig) -> str:
        return os.path.join(
            project_config.get_path_to_cache_dir(),
            "git",
            "sync_merge.meta.json",
        )

    @staticmethod
    def _classify(
        project_config: ProjectConfig,
        base_revision: str,
        target_revision: str,
        incoming_revision: str,
    ) -> ThreeWayMergeResult:
        cache_key = (base_revision, target_revision, incoming_revision)
        cached = SyncMergeService._classification_cache
        if cached is not None and cached[0] == cache_key:
            return cached[1]

        base_stats = _build_stats_for_revision(project_config, base_revision)
        target_stats = _build_stats_for_revision(
            project_config, target_revision
        )
        incoming_stats = _build_stats_for_revision(
            project_config, incoming_revision
        )

        result = classify_documents_from_stats(
            base_stats=base_stats,
            target_stats=target_stats,
            incoming_stats=incoming_stats,
            base_revision=base_revision,
            target_revision=target_revision,
            incoming_revision=incoming_revision,
        )

        SyncMergeService._classification_cache = (cache_key, result)
        return result

    @staticmethod
    def compute_merge(
        project_config: ProjectConfig,
        live_client: GitClient,
        target_branch: str,
    ) -> "tuple[SyncMergeMeta, ThreeWayMergeResult]":
        branch = live_client.get_current_branch()
        incoming_revision = live_client.check_revision(branch)
        target_revision = live_client.check_revision(target_branch)
        base_revision = live_client.merge_base(
            target_revision, incoming_revision
        )

        merge_result = SyncMergeService._classify(
            project_config, base_revision, target_revision, incoming_revision
        )

        non_document_changed_paths = _find_non_document_changes(
            live_client,
            project_config,
            base_revision,
            target_revision,
            incoming_revision,
        )

        meta = SyncMergeMeta(
            branch=branch,
            live_branch_sha_at_start=incoming_revision,
            target_branch=target_branch,
            base_revision=base_revision,
            target_revision=target_revision,
            incoming_revision=incoming_revision,
            non_document_changed_paths=non_document_changed_paths,
        )
        return meta, merge_result

    @staticmethod
    def persist(project_config: ProjectConfig, meta: SyncMergeMeta) -> None:
        path_to_meta = SyncMergeService.get_meta_path(project_config)
        os.makedirs(os.path.dirname(path_to_meta), exist_ok=True)
        with open(path_to_meta, "w", encoding="utf8") as meta_file:
            json.dump(asdict(meta), meta_file)

    @staticmethod
    def get_active(project_config: ProjectConfig) -> Optional[SyncMergeMeta]:
        path_to_meta = SyncMergeService.get_meta_path(project_config)
        if not os.path.isfile(path_to_meta):
            return None
        try:
            with open(path_to_meta, encoding="utf8") as meta_file:
                meta_dict = json.load(meta_file)
            return SyncMergeMeta(**meta_dict)
        except (OSError, ValueError, TypeError):
            SyncMergeService.cleanup(project_config)
            return None

    @staticmethod
    def recompute_merge_result(
        project_config: ProjectConfig, meta: SyncMergeMeta
    ) -> ThreeWayMergeResult:
        return SyncMergeService._classify(
            project_config,
            meta.base_revision,
            meta.target_revision,
            meta.incoming_revision,
        )

    @staticmethod
    def allocate(
        project_config: ProjectConfig,
        meta: SyncMergeMeta,
        merge_result: ThreeWayMergeResult,
        key: str,
        decision: str,
    ) -> SyncMergeMeta:
        node_result = merge_result.find_node_result(key)
        assert node_result is not None, f"Unknown node key: {key}"
        assert node_result.is_conflict(), f"Node {key} is not a conflict."
        assert decision in ("target", "incoming"), decision
        meta.allocations[key] = decision
        SyncMergeService.persist(project_config, meta)
        return meta

    @staticmethod
    def allocate_section(
        project_config: ProjectConfig,
        meta: SyncMergeMeta,
        merge_result: ThreeWayMergeResult,
        section_key: str,
        decision: str,
    ) -> SyncMergeMeta:
        assert decision in ("target", "incoming"), decision
        section_result = merge_result.find_node_result(section_key)
        assert section_result is not None, f"Unknown node key: {section_key}"
        document_result = merge_result.find_document_result(section_key)
        assert document_result is not None

        section_anchor = (
            section_result.target_node
            or section_result.base_node
            or section_result.incoming_node
        )
        for result in document_result.iter_all():
            if not result.is_conflict():
                continue
            anchor = (
                result.target_node or result.base_node or result.incoming_node
            )
            if anchor is None:
                continue
            if _is_descendant_of(anchor, section_anchor):
                meta.allocations[result.key] = decision
        SyncMergeService.persist(project_config, meta)
        return meta

    @staticmethod
    def place_after(
        project_config: ProjectConfig,
        meta: SyncMergeMeta,
        merge_result: ThreeWayMergeResult,
        node_key: str,
        after_key: str,
    ) -> SyncMergeMeta:
        """
        Records that `node_key` (a genuinely-new, non-conflicting addition)
        should be inserted right after `after_key` among its siblings, or
        at the very start if `after_key` is PLACEMENT_START -- an optional,
        non-blocking override of the default insertion order two
        independent additions would otherwise get (see splice_document).
        """
        node_result = merge_result.find_node_result(node_key)
        assert node_result is not None, f"Unknown node key: {node_key}"
        assert node_result.base_node is None, (
            f"Node {node_key} is not a new addition (it existed in base)."
        )
        assert not node_result.is_conflict(), (
            f"Node {node_key} is a conflict; resolve it, don't place it."
        )

        document_result = merge_result.find_document_result(node_key)
        assert document_result is not None
        parent_key_of = compute_parent_key_map(document_result)

        if after_key != PLACEMENT_START:
            after_result = merge_result.find_node_result(after_key)
            assert after_result is not None, f"Unknown node key: {after_key}"
            assert parent_key_of.get(node_key) == parent_key_of.get(
                after_key
            ), f"{after_key} is not a sibling of {node_key}."

        meta.placements[node_key] = after_key
        SyncMergeService.persist(project_config, meta)
        return meta

    @staticmethod
    def is_fully_resolved(
        merge_result: ThreeWayMergeResult, meta: SyncMergeMeta
    ) -> bool:
        for document in merge_result.documents:
            for result in document.iter_all():
                if result.is_conflict() and result.key not in meta.allocations:
                    return False
        return True

    @staticmethod
    def materialize_and_publish(
        project_config: ProjectConfig,
        live_client: GitClient,
        meta: SyncMergeMeta,
        merge_result: ThreeWayMergeResult,
    ) -> SyncPublishResult:
        if live_client.get_current_branch() != meta.branch:
            return SyncPublishResult(
                success=False,
                error_message=(
                    f"Cannot finish synchronization: the workspace is no "
                    f"longer on branch '{meta.branch}'. Switch back to "
                    f"'{meta.branch}' and try again, or abort."
                ),
            )
        if (
            live_client.check_revision(meta.branch)
            != meta.live_branch_sha_at_start
        ):
            return SyncPublishResult(
                success=False,
                error_message=(
                    f"Cannot finish synchronization: branch '{meta.branch}' "
                    f"changed since synchronization started. Abort and "
                    f"retry."
                ),
            )
        if not live_client.is_clean_branch():
            return SyncPublishResult(
                success=False,
                error_message=(
                    "Cannot finish synchronization: the workspace has "
                    "uncommitted changes. Commit or discard them first."
                ),
            )

        overrides: Dict[str, Optional[bytes]] = {}
        for document in merge_result.documents:
            composite_document = splice_document(
                document, meta.allocations, meta.placements
            )
            if composite_document is None:
                continue
            if (
                len(composite_document.section_contents) == 0
                and len(document.node_results) > 0
            ):
                # Every node in this document resolved to "deleted" (e.g.
                # the whole document was removed on one side and never
                # touched on the other, or a delete/modify conflict was
                # resolved as "confirm deletion") -- remove the file
                # entirely rather than publishing an empty document shell.
                # Only meaningful when target still has the file at all;
                # if it never did, there's nothing to remove.
                if document.target_document is not None:
                    overrides[document.rel_path] = None
                continue
            written = SDWriter(project_config).write(composite_document)
            overrides[document.rel_path] = written.encode("utf-8")

        path_to_worktree = SyncMergeService.get_worktree_path(project_config)
        worktree_client = GitClient.create_sync_worktree(
            path_to_worktree, meta.target_revision, project_config
        )
        try:
            new_sha = worktree_client.commit_tree_with_overrides(
                base_revision=meta.target_revision,
                overrides=overrides,
                parent_revision=meta.target_revision,
                message=(
                    f"Synchronize '{meta.branch}' onto '{meta.target_branch}'"
                ),
            )
        finally:
            GitClient.remove_sync_worktree(path_to_worktree)

        live_client.hard_reset(new_sha)
        SyncMergeService.cleanup(project_config)
        return SyncPublishResult(success=True)

    @staticmethod
    def cleanup(project_config: ProjectConfig) -> None:
        path_to_worktree = SyncMergeService.get_worktree_path(project_config)
        GitClient.remove_sync_worktree(path_to_worktree)

        path_to_meta = SyncMergeService.get_meta_path(project_config)
        if os.path.isfile(path_to_meta):
            os.remove(path_to_meta)

        SyncMergeService._classification_cache = None


def _is_descendant_of(node: object, ancestor: object) -> bool:
    if node is ancestor:
        return True
    current = getattr(node, "parent", None)
    while current is not None:
        if current is ancestor:
            return True
        current = getattr(current, "parent", None)
    return False
