from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from markupsafe import Markup

from strictdoc import __version__
from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.core.project_config import ProjectConfig
from strictdoc.export.html.html_templates import JinjaEnvironment
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.features.git_workspace.three_way_merge_analyzer import (
    PLACEMENT_START,
    NodeClassification,
    NodeMergeResult,
    ThreeWayMergeResult,
    order_children_by_parent_key,
)
from strictdoc.helpers.diff import get_colored_html_diff_string

# Fields compared/shown for a true-conflict node's side-by-side display.
_DISPLAYED_FIELDS = ("TITLE", "STATEMENT", "RATIONALE")

# Max length of a TEXT node's (no TITLE) STATEMENT preview shown in the
# always-visible <summary> line.
_SUMMARY_PREVIEW_LENGTH = 80


@dataclass
class ConflictNodeView:
    result: NodeMergeResult
    depth: int
    has_conflicting_descendant: bool = False
    has_modified_descendant: bool = False
    is_first_child: bool = False

    @property
    def key(self) -> str:
        return self.result.key

    @property
    def classification(self) -> str:
        return self.result.classification.value

    @property
    def is_conflict(self) -> bool:
        return self.result.is_conflict()

    @property
    def is_expanded_by_default(self) -> bool:
        # SDOC-SRS-221: a node is shown open by default whenever it (or
        # anything nested under it) actually changed -- an unchanged
        # section wrapping a modified node must still stay open, or the
        # very change the screen exists to surface would be hidden inside
        # a collapsed <details>.
        return (
            self.classification != NodeClassification.UNCHANGED.value
            or self.has_modified_descendant
        )

    @property
    def is_delete_modify(self) -> bool:
        return (
            self.result.classification
            == NodeClassification.DELETE_MODIFY_CONFLICT
        )

    @property
    def is_new_addition(self) -> bool:
        # A genuinely new node (no base_node) that auto-merged in without
        # conflict -- the only kind of node a drag-and-drop placement
        # applies to (see SyncMergeService.place_after).
        return (
            self.result.base_node is None
            and self.classification == NodeClassification.AUTO_MERGED.value
        )

    @property
    def is_draggable_from_incoming(self) -> bool:
        # Only meaningful to drag from the incoming (left) column when this
        # node actually has incoming-side content to show there -- a
        # target-only addition is also "new" but has nothing on the left.
        return self.is_new_addition and self.result.incoming_node is not None

    @property
    def node_type(self) -> str:
        node = (
            self.result.target_node
            or self.result.base_node
            or self.result.incoming_node
        )
        return node.node_type if node is not None else "REQUIREMENT"

    @property
    def is_section(self) -> bool:
        return self.node_type == "SECTION"

    def _display_text(self, node: Optional[SDocNode]) -> str:
        if node is None:
            return "(deleted)"
        title = node.reserved_title
        statement = node.reserved_statement
        if title:
            return title if not statement else f"{title}: {statement}"
        return statement or "(untitled)"

    @property
    def resolved_display(self) -> str:
        return self._display_text(self.result.resolved_node)

    @property
    def target_display(self) -> str:
        return self._display_text(self.result.target_node)

    @property
    def incoming_display(self) -> str:
        return self._display_text(self.result.incoming_node)

    def _summary_text(self, node: Optional[SDocNode]) -> str:
        # A short, single-line label for the always-visible <summary> --
        # unlike _display_text (used for the collapsible body below),
        # this must stay short even for a TEXT node with a long, multi-
        # paragraph STATEMENT and no TITLE, or collapsing the node (per
        # SDOC-SRS-221) would have no visible effect: the whole point of
        # collapsing is to hide exactly this content, not repeat it in the
        # one part of the node that's shown regardless of open/closed.
        if node is None:
            return "(deleted)"
        title = node.reserved_title
        if title:
            return title
        statement = node.reserved_statement or "(untitled)"
        if len(statement) > _SUMMARY_PREVIEW_LENGTH:
            return statement[:_SUMMARY_PREVIEW_LENGTH].rstrip() + "…"
        return statement

    @property
    def resolved_summary(self) -> str:
        return self._summary_text(self.result.resolved_node)

    @property
    def target_summary(self) -> str:
        return self._summary_text(self.result.target_node)

    @property
    def incoming_summary(self) -> str:
        return self._summary_text(self.result.incoming_node)

    @property
    def target_field_diffs(self) -> List[Tuple[str, Markup]]:
        return self._field_diffs("left")

    @property
    def incoming_field_diffs(self) -> List[Tuple[str, Markup]]:
        return self._field_diffs("right")

    @property
    def target_fields(self) -> List[Tuple[str, str]]:
        return self._plain_fields(self.result.target_node)

    @property
    def incoming_fields(self) -> List[Tuple[str, str]]:
        return self._plain_fields(self.result.incoming_node)

    def _plain_fields(self, node: Optional[SDocNode]) -> List[Tuple[str, str]]:
        # The un-colored counterpart of _field_diffs, used for the body of
        # unchanged/auto-merged nodes -- there is nothing to diff (either
        # nothing changed, or the classifier already auto-decided the
        # result without needing the user to compare two sides), but the
        # full field content still needs to live somewhere other than the
        # always-visible <summary> so that collapsing the node actually
        # hides it.
        fields: List[Tuple[str, str]] = []
        for field_name in _DISPLAYED_FIELDS:
            value = _get_field_value(node, field_name)
            if value is None:
                continue
            fields.append((field_name, value))
        return fields

    def _field_diffs(self, side: str) -> List[Tuple[str, Markup]]:
        target_node = self.result.target_node
        incoming_node = self.result.incoming_node
        diffs: List[Tuple[str, Markup]] = []
        for field_name in _DISPLAYED_FIELDS:
            target_value = _get_field_value(target_node, field_name)
            incoming_value = _get_field_value(incoming_node, field_name)
            if target_value is None and incoming_value is None:
                continue
            colored = get_colored_html_diff_string(
                target_value or "", incoming_value or "", side
            )
            diffs.append((field_name, colored))
        return diffs


def _get_field_value(
    node: Optional[SDocNode], field_name: str
) -> Optional[str]:
    if node is None:
        return None
    fields = node.ordered_fields_lookup.get(field_name)
    if not fields:
        return None
    value: str = fields[0].get_text_value()
    return value


@dataclass
class ConflictedDocumentView:
    rel_path: str
    nodes: List[ConflictNodeView] = field(default_factory=list)

    @property
    def has_conflicts(self) -> bool:
        return any(node.is_conflict for node in self.nodes)


def _flatten_document(
    merge_result: ThreeWayMergeResult,
    rel_path: str,
    placements: Dict[str, str],
) -> List[ConflictNodeView]:
    document_result = next(
        (doc for doc in merge_result.documents if doc.rel_path == rel_path),
        None,
    )
    if document_result is None:
        return []

    # Ordered (and depth-annotated) the same way splice_document will
    # actually materialize the tree -- including any drag-and-drop
    # placements -- so the review screen shows a moved node exactly where
    # it will end up once committed, not the pre-placement default order.
    _parent_key_of, children_by_parent_key = order_children_by_parent_key(
        document_result, placements
    )
    ordered: List[tuple[NodeMergeResult, int, bool]] = []

    def _walk(parent_key: Optional[str], depth: int) -> None:
        for index, result in enumerate(
            children_by_parent_key.get(parent_key, [])
        ):
            ordered.append((result, depth, index == 0))
            _walk(result.key, depth + 1)

    _walk(None, 0)

    views = [
        ConflictNodeView(result=result, depth=depth, is_first_child=is_first)
        for result, depth, is_first in ordered
    ]

    # A section's "resolve entire section" bulk action should be offered
    # whenever any of its descendants (in flattened pre-order) conflict,
    # regardless of whether the section's own fields changed. Likewise
    # (SDOC-SRS-221), a section must stay expanded by default whenever any
    # descendant changed at all, not just conflicting ones.
    for index, view in enumerate(views):
        if not view.is_section:
            continue
        for other in views[index + 1 :]:
            if other.depth <= view.depth:
                break
            if other.is_conflict:
                view.has_conflicting_descendant = True
            if other.classification != NodeClassification.UNCHANGED.value:
                view.has_modified_descendant = True
            if view.has_conflicting_descendant and view.has_modified_descendant:
                break

    return views


class GitConflictsViewObject:
    # Exposed for the drop-zone-before-the-first-child template markup.
    PLACEMENT_START: str = PLACEMENT_START

    def __init__(
        self,
        *,
        project_config: ProjectConfig,
        merge_result: Optional[ThreeWayMergeResult],
        allocations: Dict[str, str],
        target_branch: str,
        placements: Optional[Dict[str, str]] = None,
        non_document_changed_paths: Optional[List[str]] = None,
        message: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> None:
        self.project_config: ProjectConfig = project_config
        self.merge_result: Optional[ThreeWayMergeResult] = merge_result
        self.allocations: Dict[str, str] = allocations
        self.placements: Dict[str, str] = placements or {}
        self.non_document_changed_paths: List[str] = (
            non_document_changed_paths or []
        )
        self.target_branch: str = target_branch
        self.message: Optional[str] = message
        self.error_message: Optional[str] = error_message

        self.is_active: bool = merge_result is not None
        self.conflicted_documents: List[ConflictedDocumentView] = []
        if merge_result is not None:
            for document_result in merge_result.documents:
                nodes = _flatten_document(
                    merge_result, document_result.rel_path, self.placements
                )
                # Show any document with *something* to review -- not just
                # true conflicts. At zero true conflicts (fast-forward-
                # eligible syncs), every node is auto_merged/unchanged, and
                # this is the only screen the user ever sees before
                # Commit, so filtering down to "has a conflict" would
                # leave it blank exactly when there's the most auto-merged
                # content to actually review. A whole document added or
                # removed on one side (e.g. a new document with no
                # requirements in it yet) has no node-level classification
                # at all to check, so it's included unconditionally too.
                document_added_or_removed = (
                    document_result.target_document is None
                    or document_result.incoming_document is None
                )
                if document_added_or_removed or any(
                    node.classification != NodeClassification.UNCHANGED.value
                    for node in nodes
                ):
                    self.conflicted_documents.append(
                        ConflictedDocumentView(
                            rel_path=document_result.rel_path, nodes=nodes
                        )
                    )

        link_renderer = LinkRenderer(
            root_path="", static_path=project_config.dir_for_sdoc_assets
        )
        self.link_renderer: LinkRenderer = link_renderer
        self.is_running_on_server: bool = project_config.is_running_on_server
        self.strictdoc_version = __version__

    @property
    def remaining_true_conflicts(self) -> int:
        if self.merge_result is None:
            return 0
        return sum(
            1
            for document in self.merge_result.documents
            for result in document.iter_all()
            if result.is_conflict() and result.key not in self.allocations
        )

    @property
    def all_resolved(self) -> bool:
        return self.remaining_true_conflicts == 0

    @property
    def has_non_document_changes(self) -> bool:
        return len(self.non_document_changed_paths) > 0

    def get_document_level(self) -> int:
        return 0

    def render_screen(self, jinja_environment: JinjaEnvironment) -> Markup:
        return jinja_environment.render_template_as_markup(
            "features/git_workspace/conflicts_index.jinja", view_object=self
        )

    def render_url(self, url: str) -> Markup:
        return Markup(self.link_renderer.render_url(url))

    def render_static_url(self, url: str) -> Markup:
        return Markup(self.link_renderer.render_static_url(url))

    def render_static_url_with_prefix(self, url: str) -> str:
        return self.link_renderer.render_static_url_with_prefix(url)
