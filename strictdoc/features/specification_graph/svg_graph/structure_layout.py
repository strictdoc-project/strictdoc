"""
Stage 2 of the graph generator for the structure mode: structure.

The stage places the children of each container in columns. The stage uses
no pixel geometry. spec.md, section "Режим «структура»", defines the rules.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Mapping, Optional, Set, Tuple, Union

from strictdoc.features.specification_graph.svg_graph.model import (
    GraphNode,
    LayoutMode,
)
from strictdoc.features.specification_graph.svg_graph.normalization import (
    NormalizedGraph,
)


class ChannelKind(Enum):
    TOP_CORRIDOR = "top_corridor"
    BOTTOM_CORRIDOR = "bottom_corridor"
    VERTICAL = "vertical"
    COLUMN = "column"
    # Space under a short column, from its bottom down to the bottom
    # corridor. The index is the column. For the routes, the pockets and the
    # bottom corridor are one channel: BOTTOM_CORRIDOR.
    POCKET = "pocket"
    # Between the block of the unconnected root children and the row.
    BLOCK_SEPARATOR = "block_separator"


@dataclass(frozen=True)
class StructureChannelId:
    """
    A channel of a container. The container ID None is the root.

    VERTICAL: index is the channel number, 0 is left of the first column.
    COLUMN: index is the column number, gap is the gap number, 0 is below
    the first node of the column.
    """

    kind: ChannelKind
    container_id: Optional[str]
    index: int = 0
    gap: int = 0

    @property
    def is_horizontal(self) -> bool:
        return self.kind is not ChannelKind.VERTICAL


@dataclass(frozen=True)
class PortEnd:
    """
    An end of a segment at a port of a node.
    """

    node_id: str
    slot: int
    list_size: int


@dataclass(frozen=True)
class LaneEnd:
    """
    An end of a segment at a lane of a vertical channel.
    """

    channel: StructureChannelId
    lane: int


SegmentEnd = Union[PortEnd, LaneEnd]


@dataclass(frozen=True)
class CorridorSegment:
    """
    A horizontal segment of a route in the bottom corridor.

    The geometry places the segment at its base height if it is free,
    otherwise lower. spec.md, section "Геометрия контейнера".
    """

    # The edge ID and the position of the channel in the route.
    key: Tuple[str, int]
    container_id: Optional[str]
    lane: int
    ends: Tuple[SegmentEnd, SegmentEnd]
    # The lane of a column channel that the segment continues straight
    # through a through pass. Its height is the base height. Without it, the
    # base height lies the clearance below the columns the segment passes
    # over.
    level_from: Optional[LaneEnd] = None


@dataclass(frozen=True)
class NodePlace:
    """
    The place of a node in the columns of its container.
    """

    container_id: Optional[str]
    column: int
    # Position in a column of simple nodes, 0 is the top node.
    row: int
    row_count: int


@dataclass(frozen=True)
class ContainerColumn:
    # Simple nodes from top to bottom, or one composite node.
    node_ids: Tuple[str, ...]
    is_composite: bool


@dataclass(frozen=True)
class StructureLayout:
    # Columns of each composite node, by node ID. The key None is the row of
    # the connected root children.
    columns: Mapping[Optional[str], Tuple[ContainerColumn, ...]]
    # Root children in the block above the row, in input order.
    root_block_ids: Tuple[str, ...]
    # Places of the nodes in the columns. The root block has no places.
    places: Mapping[str, NodePlace]

    def channel_above(self, node_id: str) -> StructureChannelId:
        """
        Return the horizontal channel above a node in a column.
        """

        place = self.places[node_id]
        if place.row == 0:
            return StructureChannelId(
                ChannelKind.TOP_CORRIDOR, place.container_id
            )
        return StructureChannelId(
            ChannelKind.COLUMN, place.container_id, place.column, place.row - 1
        )

    def channel_below(self, node_id: str) -> StructureChannelId:
        """
        Return the horizontal channel below a node in a column.
        """

        place = self.places[node_id]
        if place.row == place.row_count - 1:
            return StructureChannelId(
                ChannelKind.BOTTOM_CORRIDOR, place.container_id
            )
        return StructureChannelId(
            ChannelKind.COLUMN, place.container_id, place.column, place.row
        )

    def neighbor_channels(
        self, channel: StructureChannelId
    ) -> List[StructureChannelId]:
        """
        Return the channels that touch a channel in the same container.

        The corridors touch every vertical channel. A column channel touches
        the two vertical channels beside its column. A vertical channel
        touches the corridors and the column channels of the columns beside
        it.
        """

        columns = self.columns[channel.container_id]
        container_id = channel.container_id
        if channel.kind in (
            ChannelKind.TOP_CORRIDOR,
            ChannelKind.BOTTOM_CORRIDOR,
        ):
            return [
                StructureChannelId(ChannelKind.VERTICAL, container_id, index_)
                for index_ in range(len(columns) + 1)
            ]
        if channel.kind is ChannelKind.COLUMN:
            return [
                StructureChannelId(
                    ChannelKind.VERTICAL, container_id, channel.index
                ),
                StructureChannelId(
                    ChannelKind.VERTICAL, container_id, channel.index + 1
                ),
            ]
        if channel.kind is ChannelKind.VERTICAL:
            result = [
                StructureChannelId(ChannelKind.TOP_CORRIDOR, container_id),
                StructureChannelId(ChannelKind.BOTTOM_CORRIDOR, container_id),
            ]
            for column_index_ in (channel.index - 1, channel.index):
                if not 0 <= column_index_ < len(columns):
                    continue
                column_ = columns[column_index_]
                if column_.is_composite:
                    continue
                result.extend(
                    StructureChannelId(
                        ChannelKind.COLUMN, container_id, column_index_, gap_
                    )
                    for gap_ in range(len(column_.node_ids) - 1)
                )
            return result
        return []


def compute_structure_layout(
    normalized_graph: NormalizedGraph,
) -> StructureLayout:
    if normalized_graph.mode is not LayoutMode.STRUCTURE:
        raise ValueError(
            f"Structure layout does not support the mode: "
            f"{normalized_graph.mode.value}."
        )

    root_nodes = [
        node_
        for node_ in normalized_graph.nodes
        if normalized_graph.parent_ids[node_.node_id] is None
    ]
    row_nodes, block_nodes = split_root_children(normalized_graph, root_nodes)

    columns: Dict[Optional[str], Tuple[ContainerColumn, ...]] = {
        None: _columns(row_nodes)
    }
    for node_ in normalized_graph.nodes:
        if len(node_.children) > 0:
            columns[node_.node_id] = _columns(list(node_.children))
    places: Dict[str, NodePlace] = {}
    for container_id_, container_columns_ in columns.items():
        for column_index_, column_ in enumerate(container_columns_):
            for row_, node_id_ in enumerate(column_.node_ids):
                places[node_id_] = NodePlace(
                    container_id=container_id_,
                    column=column_index_,
                    row=row_,
                    row_count=len(column_.node_ids),
                )
    return StructureLayout(
        columns=columns,
        root_block_ids=tuple(node_.node_id for node_ in block_nodes),
        places=places,
    )


def split_root_children(
    normalized_graph: NormalizedGraph, root_nodes: List[GraphNode]
) -> Tuple[List[GraphNode], List[GraphNode]]:
    """
    Split the root children into the row and the block.

    This function is the only place of the root rule. spec.md, section "Раскладка корня": a root child is connected if the
    child or any of its descendants has a relation to a node outside the
    child. Connected children form the row. The other children form the
    block above the row. Inner containers do not use this rule.
    """

    root_of: Dict[str, str] = {}
    for node_ in normalized_graph.nodes:
        parent_id_ = normalized_graph.parent_ids[node_.node_id]
        root_of[node_.node_id] = (
            node_.node_id if parent_id_ is None else root_of[parent_id_]
        )
    connected_root_ids: Set[str] = set()
    for edge_ in normalized_graph.edges:
        source_root_ = root_of[edge_.source_id]
        target_root_ = root_of[edge_.target_id]
        if source_root_ != target_root_:
            connected_root_ids.add(source_root_)
            connected_root_ids.add(target_root_)
    row_nodes = [
        node_ for node_ in root_nodes if node_.node_id in connected_root_ids
    ]
    block_nodes = [
        node_ for node_ in root_nodes if node_.node_id not in connected_root_ids
    ]
    return row_nodes, block_nodes


def _columns(children: List[GraphNode]) -> Tuple[ContainerColumn, ...]:
    """
    Apply the column rule to the children of one container.

    Consecutive simple nodes form one column from top to bottom. A composite
    node takes a column of its own.
    """

    columns: List[ContainerColumn] = []
    simple_run: List[str] = []
    for child_ in children:
        if len(child_.children) == 0:
            simple_run.append(child_.node_id)
            continue
        if len(simple_run) > 0:
            columns.append(
                ContainerColumn(node_ids=tuple(simple_run), is_composite=False)
            )
            simple_run = []
        columns.append(
            ContainerColumn(node_ids=(child_.node_id,), is_composite=True)
        )
    if len(simple_run) > 0:
        columns.append(
            ContainerColumn(node_ids=tuple(simple_run), is_composite=False)
        )
    return tuple(columns)
