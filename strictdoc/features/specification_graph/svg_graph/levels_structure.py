"""
Stage 2 of the graph generator for the levels mode: structure.

The stage places each node in a logical grid cell: a row and a column. The
stage uses no pixel geometry. spec.md, section "Режим «уровни»", defines the
rules.
"""

from dataclasses import dataclass
from math import isqrt
from typing import Dict, FrozenSet, List, Mapping, Optional, Set, Tuple

from strictdoc.features.specification_graph.svg_graph.model import LayoutMode
from strictdoc.features.specification_graph.svg_graph.normalization import (
    NormalizedGraph,
)


@dataclass(frozen=True)
class GridPosition:
    row: int
    column: int


@dataclass(frozen=True)
class LevelsStructure:
    positions: Mapping[str, GridPosition]
    row_count: int
    column_count: int
    # Rows of the standalone node block. Connected rows follow them.
    standalone_row_count: int
    standalone_node_ids: Tuple[str, ...]
    corrected_root_ids: FrozenSet[str]
    # Edges that connect nodes on non-adjacent rows. The edges are dashed.
    skip_edge_ids: FrozenSet[str]


def compute_levels_structure(
    normalized_graph: NormalizedGraph,
) -> LevelsStructure:
    if normalized_graph.mode is not LayoutMode.LEVELS:
        raise ValueError(
            f"Levels structure does not support the mode: "
            f"{normalized_graph.mode.value}."
        )

    node_ids = [node_.node_id for node_ in normalized_graph.nodes]
    input_index: Dict[str, int] = {
        node_id_: index_ for index_, node_id_ in enumerate(node_ids)
    }
    parents_of: Dict[str, List[str]] = {node_id_: [] for node_id_ in node_ids}
    children_of: Dict[str, List[str]] = {node_id_: [] for node_id_ in node_ids}
    for edge_ in normalized_graph.edges:
        if edge_.is_level_edge:
            parents_of[edge_.source_id].append(edge_.target_id)
            children_of[edge_.target_id].append(edge_.source_id)

    standalone_node_ids = [
        node_id_
        for node_id_ in node_ids
        if len(parents_of[node_id_]) == 0 and len(children_of[node_id_]) == 0
    ]
    islands = _islands(node_ids, parents_of, children_of)

    positions: Dict[str, GridPosition] = {}
    corrected_root_ids: Set[str] = set()
    next_column = 0
    connected_row_count = 0
    for island_ in islands:
        island_layout_ = _IslandLayout(
            island_, parents_of, children_of, input_index
        )
        for node_id_, (row_, column_) in island_layout_.positions.items():
            positions[node_id_] = GridPosition(
                row=row_, column=column_ + next_column
            )
        corrected_root_ids.update(island_layout_.corrected_roots)
        next_column += island_layout_.column_count
        connected_row_count = max(connected_row_count, island_layout_.row_count)

    standalone_row_count = 0
    standalone_column_count = 0
    if len(standalone_node_ids) > 0:
        standalone_column_count = (
            next_column
            if next_column > 0
            else _square_grid_width(len(standalone_node_ids))
        )
        standalone_row_count = (
            len(standalone_node_ids) + standalone_column_count - 1
        ) // standalone_column_count
        for node_id_, position_ in list(positions.items()):
            positions[node_id_] = GridPosition(
                row=position_.row + standalone_row_count,
                column=position_.column,
            )
        for index_, node_id_ in enumerate(standalone_node_ids):
            positions[node_id_] = GridPosition(
                row=index_ // standalone_column_count,
                column=index_ % standalone_column_count,
            )

    skip_edge_ids = frozenset(
        edge_.edge_id
        for edge_ in normalized_graph.edges
        if positions[edge_.source_id].row - positions[edge_.target_id].row != 1
    )

    return LevelsStructure(
        positions={
            node_id_: positions[node_id_]
            for node_id_ in sorted(positions, key=input_index.__getitem__)
        },
        row_count=standalone_row_count + connected_row_count,
        column_count=max(next_column, standalone_column_count),
        standalone_row_count=standalone_row_count,
        standalone_node_ids=tuple(standalone_node_ids),
        corrected_root_ids=frozenset(corrected_root_ids),
        skip_edge_ids=skip_edge_ids,
    )


class _IslandLayout:
    """
    Levels and columns of one island.

    An island is a connected component of the level edges. Rows and columns
    are local to the island.
    """

    def __init__(
        self,
        node_ids: List[str],
        parents_of: Dict[str, List[str]],
        children_of: Dict[str, List[str]],
        input_index: Dict[str, int],
    ) -> None:
        self.node_ids: List[str] = node_ids
        self.parents_of: Dict[str, List[str]] = parents_of
        self.children_of: Dict[str, List[str]] = children_of
        self.input_index: Dict[str, int] = input_index

        self.level_of: Dict[str, int] = self._compute_levels()
        self.nodes_by_level: Dict[int, List[str]] = {}
        for node_id_ in node_ids:
            self.nodes_by_level.setdefault(self.level_of[node_id_], []).append(
                node_id_
            )

        self.column_of: Dict[str, int] = {}
        self._assign_columns()
        self._branch_root_memo: Dict[str, str] = {}
        self.nodes_by_branch_root: Dict[str, List[str]] = {}
        for node_id_ in node_ids:
            self.nodes_by_branch_root.setdefault(
                self._branch_root(node_id_), []
            ).append(node_id_)
        self._place_corrected_roots()
        self._resolve_overlaps()

        self.positions: Dict[str, Tuple[int, int]] = {
            node_id_: (self.level_of[node_id_], self.column_of[node_id_])
            for node_id_ in node_ids
        }
        self.row_count: int = max(self.level_of.values()) + 1
        self.column_count: int = max(self.column_of.values()) + 1

    def _compute_levels(self) -> Dict[str, int]:
        topological_order = self._topological_order()
        roots = [
            node_id_
            for node_id_ in self.node_ids
            if len(self.parents_of[node_id_]) == 0
            and len(self.children_of[node_id_]) > 0
        ]
        descendants_of: Dict[str, Set[str]] = {
            root_id_: self._descendants(root_id_) for root_id_ in roots
        }
        root_level: Dict[str, int] = dict.fromkeys(roots, 0)
        level_of = self._propagate_levels(topological_order, root_level)

        self.corrected_roots: Set[str] = set()
        for _ in range(len(self.node_ids) + 1):
            changed = False
            for root_id_ in roots:
                reference_level_: Optional[int] = None
                for child_id_ in self.children_of[root_id_]:
                    anchor_parents_ = [
                        parent_id_
                        for parent_id_ in self.parents_of[child_id_]
                        if parent_id_ != root_id_
                        and parent_id_ not in descendants_of[root_id_]
                    ]
                    if len(anchor_parents_) == 0:
                        continue
                    candidate_ = max(
                        level_of[parent_id_] for parent_id_ in anchor_parents_
                    )
                    if (
                        reference_level_ is None
                        or candidate_ < reference_level_
                    ):
                        reference_level_ = candidate_
                if (
                    reference_level_ is not None
                    and reference_level_ > root_level[root_id_]
                ):
                    root_level[root_id_] = reference_level_
                    self.corrected_roots.add(root_id_)
                    changed = True
            if not changed:
                break
            level_of = self._propagate_levels(topological_order, root_level)

        used_levels = sorted(set(level_of.values()))
        level_remap = {
            level_: index_ for index_, level_ in enumerate(used_levels)
        }
        return {
            node_id_: level_remap[level_]
            for node_id_, level_ in level_of.items()
        }

    def _topological_order(self) -> List[str]:
        """
        Order the nodes so that each parent comes before its children.
        """

        remaining_parent_count: Dict[str, int] = {
            node_id_: len(self.parents_of[node_id_])
            for node_id_ in self.node_ids
        }
        ready = [
            node_id_
            for node_id_ in reversed(self.node_ids)
            if remaining_parent_count[node_id_] == 0
        ]
        order: List[str] = []
        while len(ready) > 0:
            node_id = ready.pop()
            order.append(node_id)
            for child_id_ in self.children_of[node_id]:
                remaining_parent_count[child_id_] -= 1
                if remaining_parent_count[child_id_] == 0:
                    ready.append(child_id_)
        assert len(order) == len(self.node_ids), "Level edges have a cycle."
        return order

    def _propagate_levels(
        self, topological_order: List[str], root_level: Dict[str, int]
    ) -> Dict[str, int]:
        level_of: Dict[str, int] = {}
        for node_id_ in topological_order:
            if node_id_ in root_level:
                level_of[node_id_] = root_level[node_id_]
            elif len(self.parents_of[node_id_]) == 0:
                level_of[node_id_] = 0
            else:
                level_of[node_id_] = 1 + max(
                    level_of[parent_id_]
                    for parent_id_ in self.parents_of[node_id_]
                )
        return level_of

    def _descendants(self, node_id: str) -> Set[str]:
        result: Set[str] = set()
        pending = list(self.children_of[node_id])
        while len(pending) > 0:
            child_id = pending.pop()
            if child_id in result:
                continue
            result.add(child_id)
            pending.extend(self.children_of[child_id])
        return result

    def _preferred_parent(self, node_id: str) -> Optional[str]:
        parent_ids = self.parents_of[node_id]
        direct_parent_ids = [
            parent_id_
            for parent_id_ in parent_ids
            if self.level_of[parent_id_] == self.level_of[node_id] - 1
        ]
        if len(direct_parent_ids) == 1:
            return direct_parent_ids[0]
        if len(parent_ids) == 1:
            return parent_ids[0]
        uncorrected_parent_ids = [
            parent_id_
            for parent_id_ in parent_ids
            if parent_id_ not in self.corrected_roots
        ]
        if len(uncorrected_parent_ids) == 1:
            return uncorrected_parent_ids[0]
        return None

    def _assign_columns(self) -> None:
        for level_ in sorted(self.nodes_by_level):
            self._assign_level_columns(level_, self.nodes_by_level[level_])

    def _assign_level_columns(self, level: int, level_nodes: List[str]) -> None:
        preferred_column: Dict[str, int] = {}
        for node_id_ in level_nodes:
            parent_id_ = self._preferred_parent(node_id_)
            if parent_id_ is not None and parent_id_ in self.column_of:
                preferred_column[node_id_] = self.column_of[parent_id_]

        claimed: Dict[int, str] = {}
        for node_id_ in level_nodes:
            column_ = preferred_column.get(node_id_)
            if column_ is not None and column_ not in claimed:
                claimed[column_] = node_id_

        for node_id_ in level_nodes:
            if node_id_ in preferred_column:
                continue
            for parent_id_ in sorted(
                self.parents_of[node_id_], key=self.input_index.__getitem__
            ):
                if (
                    self.level_of[parent_id_] != level - 1
                    or parent_id_ not in self.column_of
                ):
                    continue
                column_ = self.column_of[parent_id_]
                if column_ not in claimed:
                    preferred_column[node_id_] = column_
                    claimed[column_] = node_id_
                    break

        reserved_columns = set(claimed)
        occupied_columns: Set[int] = set()
        for node_id_ in level_nodes:
            column_ = preferred_column.get(node_id_)
            if column_ is not None and claimed[column_] == node_id_:
                selected_ = column_
            elif column_ is not None:
                existing_max_column_ = max(self.column_of.values(), default=-1)
                candidates_ = sorted(
                    (
                        candidate_
                        for candidate_ in (column_ - 1, column_ + 1)
                        if candidate_ >= 0
                        and candidate_ not in occupied_columns
                        and candidate_ not in reserved_columns
                    ),
                    key=lambda candidate_: (
                        candidate_ > existing_max_column_,
                        abs(candidate_ - column_),
                        candidate_,
                    ),
                )
                if len(candidates_) > 0:
                    selected_ = candidates_[0]
                else:
                    selected_ = column_ + 1
                    self._insert_column(selected_)
                    occupied_columns = _shift_columns(
                        occupied_columns, selected_
                    )
                    reserved_columns = _shift_columns(
                        reserved_columns, selected_
                    )
                    for pending_id_, pending_column_ in list(
                        preferred_column.items()
                    ):
                        if pending_column_ >= selected_:
                            preferred_column[pending_id_] = pending_column_ + 1
                    claimed = {
                        (
                            claimed_column_ + 1
                            if claimed_column_ >= selected_
                            else claimed_column_
                        ): claimant_id_
                        for claimed_column_, claimant_id_ in claimed.items()
                    }
            else:
                selected_ = 0
                while (
                    selected_ in occupied_columns
                    or selected_ in reserved_columns
                ):
                    selected_ += 1
            self.column_of[node_id_] = selected_
            occupied_columns.add(selected_)

    def _insert_column(self, column: int) -> None:
        for node_id_, column_ in self.column_of.items():
            if column_ >= column:
                self.column_of[node_id_] = column_ + 1

    def _branch_root(self, node_id: str) -> str:
        """
        Follow the preferred parents up to the node that starts the branch.
        """

        path: List[str] = []
        current_id = node_id
        while current_id not in self._branch_root_memo:
            path.append(current_id)
            parent_id = self._preferred_parent(current_id)
            if parent_id is None:
                self._branch_root_memo[current_id] = current_id
                break
            current_id = parent_id
        root_id = self._branch_root_memo[current_id]
        for path_node_id_ in path:
            self._branch_root_memo[path_node_id_] = root_id
        return root_id

    def _shift_branch(self, node_id: str, delta: int) -> None:
        for member_id_ in self.nodes_by_branch_root[
            self._branch_root_memo[node_id]
        ]:
            self.column_of[member_id_] += delta

    def _place_corrected_roots(self) -> None:
        for root_id_ in sorted(
            self.corrected_roots, key=self.input_index.__getitem__
        ):
            root_level_ = self.level_of[root_id_]
            child_columns_ = sorted(
                self.column_of[child_id_]
                for child_id_ in self.children_of[root_id_]
                if self.level_of[child_id_] - root_level_ == 1
            )
            if len(child_columns_) == 0:
                continue
            target_column_ = child_columns_[(len(child_columns_) - 1) // 2] + 1
            if target_column_ == self.column_of[root_id_]:
                continue
            for other_id_ in self.nodes_by_level[root_level_]:
                if (
                    other_id_ != root_id_
                    and self.column_of[other_id_] >= target_column_
                ):
                    self._shift_branch(other_id_, 1)
            self.column_of[root_id_] = target_column_

    def _resolve_overlaps(self) -> None:
        while True:
            nodes_by_position: Dict[Tuple[int, int], List[str]] = {}
            for node_id_, column_ in self.column_of.items():
                nodes_by_position.setdefault(
                    (self.level_of[node_id_], column_), []
                ).append(node_id_)
            overlap = next(
                (
                    node_ids_
                    for node_ids_ in nodes_by_position.values()
                    if len(node_ids_) > 1
                ),
                None,
            )
            if overlap is None:
                return

            displaced_id = max(overlap, key=self.input_index.__getitem__)
            branch_member_ids = self.nodes_by_branch_root[
                self._branch_root_memo[displaced_id]
            ]
            branch_member_set = set(branch_member_ids)
            outside_positions = {
                (self.level_of[node_id_], column_)
                for node_id_, column_ in self.column_of.items()
                if node_id_ not in branch_member_set
            }
            current_max_column = max(self.column_of.values())
            candidate_deltas = sorted(
                range(-current_max_column, len(self.node_ids) + 1),
                key=lambda delta_: (
                    max(
                        self.column_of[member_id_] + delta_
                        for member_id_ in branch_member_ids
                    )
                    > current_max_column,
                    abs(delta_),
                    delta_ > 0,
                ),
            )
            delta = next(
                delta_
                for delta_ in candidate_deltas
                if delta_ != 0
                and all(
                    self.column_of[member_id_] + delta_ >= 0
                    and (
                        self.level_of[member_id_],
                        self.column_of[member_id_] + delta_,
                    )
                    not in outside_positions
                    for member_id_ in branch_member_ids
                )
            )
            self._shift_branch(displaced_id, delta)


def _islands(
    node_ids: List[str],
    parents_of: Dict[str, List[str]],
    children_of: Dict[str, List[str]],
) -> List[List[str]]:
    """
    Find the connected components of the level edges.

    Standalone nodes are not part of an island. The islands follow the input
    order of their first node. The nodes of an island keep the input order.
    """

    island_index_of: Dict[str, int] = {}
    islands: List[List[str]] = []
    for start_id_ in node_ids:
        if start_id_ in island_index_of:
            continue
        if len(parents_of[start_id_]) == 0 and len(children_of[start_id_]) == 0:
            continue
        island_index_ = len(islands)
        islands.append([])
        pending_ = [start_id_]
        while len(pending_) > 0:
            node_id_ = pending_.pop()
            if node_id_ in island_index_of:
                continue
            island_index_of[node_id_] = island_index_
            pending_.extend(parents_of[node_id_])
            pending_.extend(children_of[node_id_])
    for node_id_ in node_ids:
        node_island_index_ = island_index_of.get(node_id_)
        if node_island_index_ is not None:
            islands[node_island_index_].append(node_id_)
    return islands


def _shift_columns(columns: Set[int], inserted_column: int) -> Set[int]:
    return {
        column_ + 1 if column_ >= inserted_column else column_
        for column_ in columns
    }


def _square_grid_width(node_count: int) -> int:
    width = isqrt(node_count)
    return width if width * width == node_count else width + 1
