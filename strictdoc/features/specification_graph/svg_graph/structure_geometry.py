"""
Stages 5 and 6 of the graph generator for the structure mode.

Stage 5 computes the sizes from the inside out: a container gets its size
from its columns. Stage 6 computes the coordinates from the outside in.
spec.md, section "Геометрия контейнера", defines the rules.

The routing of the structure mode is not implemented yet. All channels have
the minimum size.
"""

import math
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Mapping, Optional, Tuple

from strictdoc.features.specification_graph.svg_graph.levels_geometry import (
    GeometryConfig,
    Rect,
)
from strictdoc.features.specification_graph.svg_graph.normalization import (
    NormalizedGraph,
)
from strictdoc.features.specification_graph.svg_graph.structure_layout import (
    ContainerColumn,
    StructureLayout,
)


class ChannelKind(Enum):
    TOP_CORRIDOR = "top_corridor"
    BOTTOM_CORRIDOR = "bottom_corridor"
    VERTICAL = "vertical"
    COLUMN = "column"
    # Between the block of the unconnected root children and the row.
    BLOCK_SEPARATOR = "block_separator"


@dataclass(frozen=True)
class StructureChannel:
    kind: ChannelKind
    # The composite node that holds the channel. None for the root.
    container_id: Optional[str]
    rect: Rect


@dataclass(frozen=True)
class StructureGeometry:
    config: GeometryConfig
    width: float
    height: float
    # Frames of the composite nodes and boxes of the simple nodes.
    node_rects: Mapping[str, Rect]
    # Header strips of the composite nodes. The bottom edge of a header is
    # the header line.
    header_rects: Mapping[str, Rect]
    channels: Tuple[StructureChannel, ...]


def compute_structure_geometry(
    normalized_graph: NormalizedGraph,
    layout: StructureLayout,
    config: Optional[GeometryConfig] = None,
) -> StructureGeometry:
    if config is None:
        config = GeometryConfig()
    return _GeometryBuilder(normalized_graph, layout, config).build()


class _GeometryBuilder:
    def __init__(
        self,
        normalized_graph: NormalizedGraph,
        layout: StructureLayout,
        config: GeometryConfig,
    ) -> None:
        self.layout: StructureLayout = layout
        self.config: GeometryConfig = config
        self.is_composite: Dict[str, bool] = {
            node_.node_id: len(node_.children) > 0
            for node_ in normalized_graph.nodes
        }
        self.sizes: Dict[str, Tuple[float, float]] = {}
        self.node_rects: Dict[str, Rect] = {}
        self.header_rects: Dict[str, Rect] = {}
        self.channels: List[StructureChannel] = []

    def build(self) -> StructureGeometry:
        config = self.config
        channel = config.min_channel_size
        row_columns = self.layout.columns[None]
        row_width, row_height = self._area_size(row_columns)
        block_ids = self.layout.root_block_ids
        block_sizes = [self._size(node_id_) for node_id_ in block_ids]
        block_width = (
            row_width
            if len(row_columns) > 0
            else _block_width(block_sizes, channel)
        )

        top = config.margin
        width = row_width
        if len(block_ids) > 0:
            block_height, block_used_width = self._place_block(
                block_ids, block_sizes, block_width, config.margin, top
            )
            width = max(width, block_used_width)
            top += block_height
            if len(row_columns) > 0:
                self.channels.append(
                    StructureChannel(
                        kind=ChannelKind.BLOCK_SEPARATOR,
                        container_id=None,
                        rect=Rect(config.margin, top, width, channel),
                    )
                )
                top += channel
        if len(row_columns) > 0:
            self._place_area(None, row_columns, config.margin, top)
            top += row_height
        return StructureGeometry(
            config=config,
            width=config.margin * 2 + width,
            height=top + config.margin,
            node_rects=self.node_rects,
            header_rects=self.header_rects,
            channels=tuple(self.channels),
        )

    def _size(self, node_id: str) -> Tuple[float, float]:
        """
        Return the size of a node. Stage 5: from the inside out.
        """

        if node_id in self.sizes:
            return self.sizes[node_id]
        if not self.is_composite[node_id]:
            size = (self.config.node_width, self.config.node_height)
        else:
            area_width, area_height = self._area_size(
                self.layout.columns[node_id]
            )
            size = (
                area_width,
                self.config.container_header_height + area_height,
            )
        self.sizes[node_id] = size
        return size

    def _column_size(self, column: ContainerColumn) -> Tuple[float, float]:
        if column.is_composite:
            return self._size(column.node_ids[0])
        count = len(column.node_ids)
        return (
            self.config.node_width,
            count * self.config.node_height
            + (count - 1) * self.config.min_channel_size,
        )

    def _area_size(
        self, columns: Tuple[ContainerColumn, ...]
    ) -> Tuple[float, float]:
        """
        Return the size of the children area of a container.

        The area has the top corridor, the columns with the vertical channels
        between them, and the bottom corridor.
        """

        if len(columns) == 0:
            return 0, 0
        channel = self.config.min_channel_size
        column_sizes = [self._column_size(column_) for column_ in columns]
        width = channel + sum(
            column_width_ + channel for column_width_, _ in column_sizes
        )
        height = (
            channel
            + max(column_height_ for _, column_height_ in column_sizes)
            + channel
        )
        return width, height

    def _place_area(
        self,
        container_id: Optional[str],
        columns: Tuple[ContainerColumn, ...],
        left: float,
        top: float,
    ) -> None:
        """
        Place the children area of a container. Stage 6: from the outside in.
        """

        channel = self.config.min_channel_size
        width, height = self._area_size(columns)
        self.channels.append(
            StructureChannel(
                ChannelKind.TOP_CORRIDOR,
                container_id,
                Rect(left, top, width, channel),
            )
        )
        self.channels.append(
            StructureChannel(
                ChannelKind.BOTTOM_CORRIDOR,
                container_id,
                Rect(left, top + height - channel, width, channel),
            )
        )
        columns_top = top + channel
        columns_height = height - 2 * channel
        x = left
        for column_ in columns:
            self.channels.append(
                StructureChannel(
                    ChannelKind.VERTICAL,
                    container_id,
                    Rect(x, columns_top, channel, columns_height),
                )
            )
            x += channel
            column_width_, _ = self._column_size(column_)
            self._place_column(container_id, column_, x, columns_top)
            x += column_width_
        self.channels.append(
            StructureChannel(
                ChannelKind.VERTICAL,
                container_id,
                Rect(x, columns_top, channel, columns_height),
            )
        )

    def _place_column(
        self,
        container_id: Optional[str],
        column: ContainerColumn,
        left: float,
        top: float,
    ) -> None:
        if column.is_composite:
            self._place_node(column.node_ids[0], left, top)
            return
        y = top
        for index_, node_id_ in enumerate(column.node_ids):
            if index_ > 0:
                self.channels.append(
                    StructureChannel(
                        ChannelKind.COLUMN,
                        container_id,
                        Rect(
                            left,
                            y,
                            self.config.node_width,
                            self.config.min_channel_size,
                        ),
                    )
                )
                y += self.config.min_channel_size
            self._place_node(node_id_, left, y)
            y += self.config.node_height

    def _place_node(self, node_id: str, left: float, top: float) -> None:
        width, height = self._size(node_id)
        self.node_rects[node_id] = Rect(left, top, width, height)
        if not self.is_composite[node_id]:
            return
        header_height = self.config.container_header_height
        self.header_rects[node_id] = Rect(left, top, width, header_height)
        self._place_area(
            node_id,
            self.layout.columns[node_id],
            left,
            top + header_height,
        )

    def _place_block(
        self,
        block_ids: Tuple[str, ...],
        block_sizes: List[Tuple[float, float]],
        block_width: float,
        left: float,
        top: float,
    ) -> Tuple[float, float]:
        """
        Place the unconnected root children on shelves, in input order.

        Return the height and the used width of the block.
        """

        positions, used_width, height = _shelf_positions(
            block_sizes, block_width, self.config.min_channel_size
        )
        for node_id_, (x_, y_) in zip(block_ids, positions):
            self._place_node(node_id_, left + x_, top + y_)
        return height, used_width


def _shelf_positions(
    sizes: List[Tuple[float, float]], shelf_width: float, channel: float
) -> Tuple[List[Tuple[float, float]], float, float]:
    """
    Put boxes on shelves from left to right, in input order.

    A shelf wraps when the next box does not fit into the shelf width. A
    channel separates the boxes and the shelves. Return the box positions,
    the used width, and the height.
    """

    positions: List[Tuple[float, float]] = []
    x = channel
    y = channel
    shelf_height = 0.0
    used_width = 0.0
    for width_, height_ in sizes:
        if x > channel and x + width_ + channel > shelf_width:
            x = channel
            y += shelf_height + channel
            shelf_height = 0.0
        positions.append((x, y))
        x += width_ + channel
        used_width = max(used_width, x)
        shelf_height = max(shelf_height, height_)
    return positions, used_width, y + shelf_height


def _block_width(
    block_sizes: List[Tuple[float, float]], channel: float
) -> float:
    """
    Return the shelf width of the block when the root has no connected row.

    This function is the only place of this rule. spec.md, section
    "Раскладка корня": the block is close to a square, but not narrower than
    its widest child.

    The function tries each shelf width that fits the first 1, 2, ... n
    boxes on the first shelf. It picks the width with the width to height
    ratio closest to 1. On a tie, the narrower width wins.
    """

    best_width = 0.0
    best_score = math.inf
    first_shelf_width = channel
    for width_, _ in block_sizes:
        first_shelf_width += width_ + channel
        _, used_width_, height_ = _shelf_positions(
            block_sizes, first_shelf_width, channel
        )
        score_ = abs(math.log(used_width_ / height_))
        if score_ < best_score:
            best_score = score_
            best_width = first_shelf_width
    return best_width
