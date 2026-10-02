"""
Stages 5 and 6 of the graph generator for the structure mode.

Stage 5 computes the sizes from the inside out: a container gets its size
from its columns and channels. Stage 6 computes the coordinates from the
outside in. spec.md, section "Геометрия контейнера", defines the rules.

The size of each channel follows from its lane count. A channel without
lanes has the minimum size. The segments under the columns (the bottom
corridor and the pockets) take their base heights one by one.
"""

import math
from dataclasses import dataclass
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from strictdoc.features.specification_graph.svg_graph.levels_geometry import (
    GeometryConfig,
    Rect,
    horizontal_channel_size,
    vertical_channel_size,
)
from strictdoc.features.specification_graph.svg_graph.normalization import (
    NormalizedGraph,
)
from strictdoc.features.specification_graph.svg_graph.structure_layout import (
    ChannelKind,
    ContainerColumn,
    CorridorSegment,
    LaneEnd,
    SegmentEnd,
    StructureChannelId,
    StructureLayout,
)

# Left, right, and bottom of a column.
ColumnSpan = Tuple[float, float, float]


@dataclass(frozen=True)
class StructureChannel:
    channel_id: StructureChannelId
    rect: Rect

    @property
    def kind(self) -> ChannelKind:
        return self.channel_id.kind

    @property
    def container_id(self) -> Optional[str]:
        return self.channel_id.container_id


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
    # Pockets: the spaces under the columns shorter than the tallest column
    # of their container.
    bottom_pockets: Tuple[StructureChannel, ...]
    # Lane count of each channel with lanes at fixed positions.
    lane_counts: Mapping[StructureChannelId, int]
    # Left x, right x, and y of each segment in a bottom corridor, by the
    # segment key.
    bottom_segment_lines: Mapping[Tuple[str, int], Tuple[float, float, float]]

    def channel_rect(self, channel_id: StructureChannelId) -> Rect:
        return next(
            channel_.rect
            for channel_ in self.channels
            if channel_.channel_id == channel_id
        )


def compute_structure_geometry(
    normalized_graph: NormalizedGraph,
    layout: StructureLayout,
    config: Optional[GeometryConfig] = None,
    lane_counts: Optional[Mapping[StructureChannelId, int]] = None,
    bottom_segments: Sequence[CorridorSegment] = (),
) -> StructureGeometry:
    if config is None:
        config = GeometryConfig()
    return _GeometryBuilder(
        normalized_graph,
        layout,
        config,
        {} if lane_counts is None else lane_counts,
        bottom_segments,
    ).build()


def corridor_contour(
    column_spans: Sequence[ColumnSpan], low: float, high: float
) -> float:
    """
    Return the bottom of the lowest column that a segment passes over.

    The segment spans from low to high. Without such a column, return the
    bottom of the tallest column.
    """

    return max(
        (
            bottom_
            for left_, right_, bottom_ in column_spans
            if low < right_ and high > left_
        ),
        default=max(bottom_ for _, _, bottom_ in column_spans),
    )


def corridor_segment_y(
    column_spans: Sequence[ColumnSpan],
    low: float,
    high: float,
    through_heights: Iterable[float],
    config: GeometryConfig,
) -> Tuple[float, Optional[float]]:
    """
    Return the heights of a segment under the columns.

    This function is the only place of this rule. spec.md, section
    "Геометрия контейнера". The segment spans from low to high. Return the
    lowest height it may take, the clearance below the lowest column it
    passes over, and the first through height that is not higher, or None.
    A through height is the height of a column channel lane that the
    segment continues straight.
    """

    lowest = corridor_contour(column_spans, low, high) + config.lane_clearance
    return lowest, next(
        (height_ for height_ in through_heights if height_ >= lowest), None
    )


def centered_lane_offset(
    size: float, lane_count: int, lane: int, config: GeometryConfig
) -> float:
    """
    Return the offset of a lane from the start of a channel.

    The lanes of a channel are centered in the channel.
    """

    return (size - (lane_count - 1) * config.lane_pitch) / 2 + (
        lane * config.lane_pitch
    )


def port_offset(
    slot: int, list_size: int, node_width: float, config: GeometryConfig
) -> float:
    """
    Return the offset of a port from the center of its node face.
    """

    if slot == 0:
        return 0
    available_half_width = node_width / 2 - config.port_margin
    return slot * min(config.port_pitch, available_half_width / list_size)


class _GeometryBuilder:
    def __init__(
        self,
        normalized_graph: NormalizedGraph,
        layout: StructureLayout,
        config: GeometryConfig,
        lane_counts: Mapping[StructureChannelId, int],
        bottom_segments: Sequence[CorridorSegment],
    ) -> None:
        self.layout: StructureLayout = layout
        self.config: GeometryConfig = config
        self.lane_counts: Mapping[StructureChannelId, int] = lane_counts
        self.bottom_segments: Dict[Optional[str], List[CorridorSegment]] = {}
        for segment_ in bottom_segments:
            self.bottom_segments.setdefault(segment_.container_id, []).append(
                segment_
            )
        self.is_composite: Dict[str, bool] = {
            node_.node_id: len(node_.children) > 0
            for node_ in normalized_graph.nodes
        }
        self.sizes: Dict[str, Tuple[float, float]] = {}
        self.node_rects: Dict[str, Rect] = {}
        self.header_rects: Dict[str, Rect] = {}
        self.channels: List[StructureChannel] = []
        self.bottom_pockets: List[StructureChannel] = []
        self.corridors: Dict[Optional[str], _BottomCorridor] = {}
        self.bottom_segment_lines: Dict[
            Tuple[str, int], Tuple[float, float, float]
        ] = {}

    def build(self) -> StructureGeometry:
        config = self.config
        channel = config.min_channel_size
        row_columns = self.layout.columns[None]
        row_width, row_height = self._area_size(None, row_columns)
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
                        StructureChannelId(ChannelKind.BLOCK_SEPARATOR, None),
                        Rect(config.margin, top, width, channel),
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
            bottom_pockets=tuple(self.bottom_pockets),
            lane_counts=dict(self.lane_counts),
            bottom_segment_lines=self.bottom_segment_lines,
        )

    def _channel_size(self, channel_id: StructureChannelId) -> float:
        lane_count = self.lane_counts.get(channel_id, 0)
        if channel_id.is_horizontal:
            return horizontal_channel_size(lane_count, self.config)
        return vertical_channel_size(lane_count, self.config)

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
                node_id, self.layout.columns[node_id]
            )
            size = (
                area_width,
                self.config.container_header_height + area_height,
            )
        self.sizes[node_id] = size
        return size

    def _column_size(
        self,
        container_id: Optional[str],
        column_index: int,
        column: ContainerColumn,
    ) -> Tuple[float, float]:
        if column.is_composite:
            return self._size(column.node_ids[0])
        return (
            self.config.node_width,
            len(column.node_ids) * self.config.node_height
            + sum(
                self._channel_size(
                    StructureChannelId(
                        ChannelKind.COLUMN, container_id, column_index, gap_
                    )
                )
                for gap_ in range(len(column.node_ids) - 1)
            ),
        )

    def _area_size(
        self,
        container_id: Optional[str],
        columns: Tuple[ContainerColumn, ...],
    ) -> Tuple[float, float]:
        """
        Return the size of the children area of a container.

        The area has the top corridor, the columns with the vertical channels
        between them, and the bottom corridor.
        """

        if len(columns) == 0:
            return 0, 0
        column_sizes = [
            self._column_size(container_id, index_, column_)
            for index_, column_ in enumerate(columns)
        ]
        width = sum(
            self._channel_size(
                StructureChannelId(ChannelKind.VERTICAL, container_id, index_)
            )
            for index_ in range(len(columns) + 1)
        ) + sum(column_width_ for column_width_, _ in column_sizes)
        height = (
            self._channel_size(
                StructureChannelId(ChannelKind.TOP_CORRIDOR, container_id)
            )
            + max(column_height_ for _, column_height_ in column_sizes)
            + self._bottom_corridor(container_id, columns).size
        )
        return width, height

    def _bottom_corridor(
        self,
        container_id: Optional[str],
        columns: Tuple[ContainerColumn, ...],
    ) -> "_BottomCorridor":
        """
        Place the segments of the bottom corridor of a container.

        The coordinates are local: x from the left of the children area, y
        from the top of the columns.

        A segment continues a column channel lane straight if the height of
        that lane fits under the columns the segment passes over. Such a
        segment keeps the height of the lane: it belongs to the row of that
        lane. The other segments form the corridor: in lane order, each lies
        the clearance below the lowest column it passes over, and at least
        one lane pitch below each overlapping corridor segment with a
        smaller lane. Right-hand traffic, which gives the lane order, thus
        applies within one row or within the corridor, never across them. A
        segment that meets an overlapping segment closer than one lane pitch
        moves down. The corridor size below the tallest column fits the
        lowest segment.
        """

        if container_id in self.corridors:
            return self.corridors[container_id]
        config = self.config
        column_spans: List[ColumnSpan] = []
        verticals: Dict[StructureChannelId, float] = {}
        x = 0.0
        for index_ in range(len(columns) + 1):
            vertical_ = StructureChannelId(
                ChannelKind.VERTICAL, container_id, index_
            )
            verticals[vertical_] = x
            x += self._channel_size(vertical_)
            if index_ == len(columns):
                break
            column_width_, column_height_ = self._column_size(
                container_id, index_, columns[index_]
            )
            column_spans.append((x, x + column_width_, column_height_))
            x += column_width_

        def end_x(end: SegmentEnd) -> float:
            if isinstance(end, LaneEnd):
                return verticals[end.channel] + centered_lane_offset(
                    self._channel_size(end.channel),
                    self.lane_counts[end.channel],
                    end.lane,
                    config,
                )
            node_width_, _ = self._size(end.node_id)
            left_, _, _ = column_spans[self.layout.places[end.node_id].column]
            return (
                left_
                + node_width_ / 2
                + port_offset(end.slot, end.list_size, node_width_, config)
            )

        through_lines: List[Tuple[CorridorSegment, float, float, float]] = []
        corridor_lines: List[Tuple[CorridorSegment, float, float, float]] = []
        for segment_ in self.bottom_segments.get(container_id, []):
            first_x_, second_x_ = (end_x(end_) for end_ in segment_.ends)
            low_, high_ = min(first_x_, second_x_), max(first_x_, second_x_)
            lowest_y_, through_y_ = corridor_segment_y(
                column_spans,
                low_,
                high_,
                (
                    self._column_lane_y(
                        columns, through_.channel, through_.lane
                    )
                    for through_ in segment_.through_lanes
                ),
                config,
            )
            if through_y_ is not None:
                through_lines.append((segment_, low_, high_, through_y_))
            else:
                corridor_lines.append((segment_, low_, high_, lowest_y_))

        lines: Dict[Tuple[str, int], Tuple[float, float, float]] = {}
        placed: List[Tuple[float, float, float]] = []
        for segment_, low_, high_, base_y_ in sorted(
            through_lines,
            key=lambda line_: (line_[3], line_[0].lane, line_[0].key),
        ):
            y_ = _free_y(base_y_, low_, high_, placed, config.lane_pitch)
            placed.append((low_, high_, y_))
            lines[segment_.key] = (low_, high_, y_)
        corridor_placed: List[Tuple[float, float, float]] = []
        for segment_, low_, high_, base_y_ in sorted(
            corridor_lines,
            key=lambda line_: (line_[0].lane, line_[0].key),
        ):
            y_ = base_y_
            for placed_low_, placed_high_, placed_y_ in corridor_placed:
                if not (high_ < placed_low_ or placed_high_ < low_):
                    y_ = max(y_, placed_y_ + config.lane_pitch)
            y_ = _free_y(y_, low_, high_, placed, config.lane_pitch)
            corridor_placed.append((low_, high_, y_))
            placed.append((low_, high_, y_))
            lines[segment_.key] = (low_, high_, y_)
        tallest = max((bottom_ for _, _, bottom_ in column_spans), default=0)
        size = max(
            (y_ + config.lane_clearance - tallest for _, _, y_ in placed),
            default=0,
        )
        corridor = _BottomCorridor(
            size=max(config.min_channel_size, size),
            column_spans=column_spans,
            lines=lines,
        )
        self.corridors[container_id] = corridor
        return corridor

    def _column_lane_y(
        self,
        columns: Tuple[ContainerColumn, ...],
        channel: StructureChannelId,
        lane: int,
    ) -> float:
        """
        Return the y of a column channel lane from the top of the columns.
        """

        config = self.config
        above = sum(
            self._channel_size(
                StructureChannelId(
                    ChannelKind.COLUMN,
                    channel.container_id,
                    channel.index,
                    gap_,
                )
            )
            for gap_ in range(channel.gap)
        )
        assert not columns[channel.index].is_composite
        return (
            (channel.gap + 1) * config.node_height
            + above
            + centered_lane_offset(
                self._channel_size(channel),
                self.lane_counts[channel],
                lane,
                config,
            )
        )

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

        width, height = self._area_size(container_id, columns)
        top_corridor = StructureChannelId(
            ChannelKind.TOP_CORRIDOR, container_id
        )
        bottom_corridor = StructureChannelId(
            ChannelKind.BOTTOM_CORRIDOR, container_id
        )
        corridor = self._bottom_corridor(container_id, columns)
        top_size = self._channel_size(top_corridor)
        bottom_size = corridor.size
        self.channels.append(
            StructureChannel(top_corridor, Rect(left, top, width, top_size))
        )
        self.channels.append(
            StructureChannel(
                bottom_corridor,
                Rect(left, top + height - bottom_size, width, bottom_size),
            )
        )
        columns_top = top + top_size
        columns_height = height - top_size - bottom_size
        for column_index_, (
            column_left_,
            column_right_,
            column_bottom_,
        ) in enumerate(corridor.column_spans):
            if column_bottom_ < columns_height:
                self.bottom_pockets.append(
                    StructureChannel(
                        StructureChannelId(
                            ChannelKind.POCKET, container_id, column_index_
                        ),
                        Rect(
                            left + column_left_,
                            columns_top + column_bottom_,
                            column_right_ - column_left_,
                            columns_height - column_bottom_,
                        ),
                    )
                )
        for key_, (low_, high_, y_) in corridor.lines.items():
            self.bottom_segment_lines[key_] = (
                left + low_,
                left + high_,
                columns_top + y_,
            )
        x = left
        for index_ in range(len(columns) + 1):
            vertical_ = StructureChannelId(
                ChannelKind.VERTICAL, container_id, index_
            )
            vertical_size_ = self._channel_size(vertical_)
            self.channels.append(
                StructureChannel(
                    vertical_,
                    Rect(x, columns_top, vertical_size_, columns_height),
                )
            )
            x += vertical_size_
            if index_ == len(columns):
                break
            column_width_, _ = self._column_size(
                container_id, index_, columns[index_]
            )
            self._place_column(
                container_id, index_, columns[index_], x, columns_top
            )
            x += column_width_

    def _place_column(
        self,
        container_id: Optional[str],
        column_index: int,
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
                gap_channel_ = StructureChannelId(
                    ChannelKind.COLUMN, container_id, column_index, index_ - 1
                )
                gap_size_ = self._channel_size(gap_channel_)
                self.channels.append(
                    StructureChannel(
                        gap_channel_,
                        Rect(left, y, self.config.node_width, gap_size_),
                    )
                )
                y += gap_size_
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
        Place the unconnected root children by the skyline, in input order.

        Return the height and the used width of the block.
        """

        positions, used_width, height = _skyline_positions(
            block_sizes, block_width, self.config.min_channel_size
        )
        for node_id_, (x_, y_) in zip(block_ids, positions):
            self._place_node(node_id_, left + x_, top + y_)
        return height, used_width


def _free_y(
    y: float,
    low: float,
    high: float,
    placed: List[Tuple[float, float, float]],
    lane_pitch: float,
) -> float:
    """
    Return the first free height from y down.

    A free height keeps one lane pitch from the placed segments that overlap
    the segment from low to high.
    """

    moved = True
    while moved:
        moved = False
        for placed_low_, placed_high_, placed_y_ in placed:
            if (
                not (high < placed_low_ or placed_high_ < low)
                and abs(placed_y_ - y) < lane_pitch
            ):
                y = placed_y_ + lane_pitch
                moved = True
    return y


@dataclass(frozen=True)
class _BottomCorridor:
    size: float
    # Column spans in local coordinates of the children area.
    column_spans: List[ColumnSpan]
    # Left x, right x, and y of each segment in local coordinates.
    lines: Dict[Tuple[str, int], Tuple[float, float, float]]


def _skyline_positions(
    sizes: List[Tuple[float, float]], block_width: float, channel: float
) -> Tuple[List[Tuple[float, float]], float, float]:
    """
    Pack boxes by the skyline, in input order.

    This function is the only place of the block packing rule. spec.md,
    section "Раскладка корня". The skyline is the lower edge of the boxes
    placed so far. Each next box takes the highest place on the skyline where
    it fits into the block width. On a tie, the leftmost place wins. A
    channel separates the boxes. Return the box positions, the used width,
    and the height.
    """

    # Skyline segments: (left, right, top of the free space).
    skyline: List[Tuple[float, float, float]] = [
        (channel, max(block_width, channel), channel)
    ]
    positions: List[Tuple[float, float]] = []
    used_width = 0.0
    height = 0.0
    for width_, height_ in sizes:
        footprint_ = width_ + channel
        best_: Optional[Tuple[float, float]] = None
        for left_, _, _ in skyline:
            right_ = left_ + footprint_
            if right_ > block_width and left_ > channel:
                continue
            top_ = max(
                segment_top_
                for segment_left_, segment_right_, segment_top_ in skyline
                if segment_left_ < right_ and segment_right_ > left_
            )
            if best_ is None or (top_, left_) < (best_[1], best_[0]):
                best_ = (left_, top_)
        assert best_ is not None
        x_, y_ = best_
        positions.append((x_, y_))
        used_width = max(used_width, x_ + footprint_)
        height = max(height, y_ + height_)
        skyline = _raise_skyline(
            skyline, x_, x_ + footprint_, y_ + height_ + channel
        )
    return positions, used_width, height


def _raise_skyline(
    skyline: List[Tuple[float, float, float]],
    left: float,
    right: float,
    top: float,
) -> List[Tuple[float, float, float]]:
    """
    Set the skyline between left and right to the given top.
    """

    result: List[Tuple[float, float, float]] = []
    for segment_left_, segment_right_, segment_top_ in skyline:
        if segment_right_ <= left or segment_left_ >= right:
            result.append((segment_left_, segment_right_, segment_top_))
            continue
        if segment_left_ < left:
            result.append((segment_left_, left, segment_top_))
        if segment_right_ > right:
            result.append((right, segment_right_, segment_top_))
    result.append((left, right, top))
    return sorted(result)


def _block_width(
    block_sizes: List[Tuple[float, float]], channel: float
) -> float:
    """
    Return the width of the block when the root has no connected row.

    This function is the only place of this rule. spec.md, section
    "Раскладка корня": the block is close to a square, but not narrower than
    its widest child.

    The function tries each block width that fits the first 1, 2, ... n
    boxes side by side. It picks the width with the width to height ratio of
    the packed block closest to 1. On a tie, the narrower width wins.
    """

    best_width = 0.0
    best_score = math.inf
    candidate_width = channel
    for width_, _ in block_sizes:
        candidate_width += width_ + channel
        _, used_width_, height_ = _skyline_positions(
            block_sizes, candidate_width, channel
        )
        score_ = abs(math.log(used_width_ / height_))
        if score_ < best_score:
            best_score = score_
            best_width = candidate_width
    return best_width
