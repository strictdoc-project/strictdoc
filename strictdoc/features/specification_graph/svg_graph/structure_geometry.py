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

from strictdoc.features.specification_graph.svg_graph.gate_ports import Face
from strictdoc.features.specification_graph.svg_graph.levels_geometry import (
    GeometryConfig,
    Rect,
    grid_ceil,
    horizontal_channel_size,
    port_list_pitch,
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

# A gate of the structure mode: a horizontal channel and a column of its
# container. The faces of the gate are the node faces of the column that
# open into the channel.
StructureGate = Tuple[StructureChannelId, int]


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
    # The longest port list on the left and on the right side of each gate.
    gate_port_lists: Mapping[StructureGate, Tuple[int, int]]
    # The gate of each face of a simple node.
    face_gates: Mapping[Tuple[str, Face], StructureGate]

    def channel_rect(self, channel_id: StructureChannelId) -> Rect:
        return next(
            channel_.rect
            for channel_ in self.channels
            if channel_.channel_id == channel_id
        )

    def port_offset(
        self, node_id: str, face: Face, slot: int, list_size: int
    ) -> float:
        """
        Return the offset of a port from the center of its node face.

        The ports of a section stand from the left of its frame, at the
        header: slot 1 is the leftmost one. spec.md, section "Связи
        композитной ноды".
        """

        if node_id in self.header_rects:
            rect = self.node_rects[node_id]
            first_x = rect.x + self.config.port_margin
            if face is Face.HEADER:
                # The leftmost port on the header line is not closer to the
                # left face than the first lane of the left vertical channel.
                vertical = self.channel_rect(
                    StructureChannelId(ChannelKind.VERTICAL, node_id, 0)
                )
                first_x = max(
                    first_x,
                    vertical.x
                    + centered_lane_offset(
                        vertical.width,
                        max(
                            1,
                            self.lane_counts.get(
                                StructureChannelId(
                                    ChannelKind.VERTICAL, node_id, 0
                                ),
                                0,
                            ),
                        ),
                        0,
                        self.config,
                    ),
                )
            return (
                first_x
                - (rect.x + rect.width / 2)
                + (slot - 1) * self.config.port_pitch
            )
        gate = self.face_gates.get((node_id, face))
        return gate_port_offset(
            slot,
            list_size,
            self.node_rects[node_id].width,
            self.gate_port_lists.get(gate, (0, 0)) if gate else (0, 0),
            self.config,
        )

    def face_y(self, node_id: str, face: Face) -> float:
        return face_y(self.node_rects, self.header_rects, node_id, face)


def face_y(
    node_rects: Mapping[str, Rect],
    header_rects: Mapping[str, Rect],
    node_id: str,
    face: Face,
) -> float:
    """
    Return the height of a face: the top or the bottom of a node, or the
    bottom line of the header of a section.
    """

    if face is Face.HEADER:
        header = header_rects[node_id]
        return header.y + header.height
    rect = node_rects[node_id]
    return rect.y if face is Face.TOP else rect.y + rect.height


def compute_structure_geometry(
    normalized_graph: NormalizedGraph,
    layout: StructureLayout,
    config: Optional[GeometryConfig] = None,
    lane_counts: Optional[Mapping[StructureChannelId, int]] = None,
    bottom_segments: Sequence[CorridorSegment] = (),
    side_entries: Optional[Mapping[StructureChannelId, Sequence[str]]] = None,
    gate_port_lists: Optional[Mapping[StructureGate, Tuple[int, int]]] = None,
) -> StructureGeometry:
    """
    Return the geometry of the structure mode.

    side_entries maps a column channel to the child containers that a line
    from this channel enters through a side face, into the outer vertical
    channel of the child. gate_port_lists gives the longest port list on
    the left and on the right side of each gate whose ports are known.
    """

    if config is None:
        config = GeometryConfig()
    return _GeometryBuilder(
        normalized_graph,
        layout,
        config,
        {} if lane_counts is None else lane_counts,
        bottom_segments,
        {} if side_entries is None else side_entries,
        {} if gate_port_lists is None else gate_port_lists,
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


def gate_port_offset(
    slot: int,
    list_size: int,
    node_width: float,
    list_sizes: Tuple[int, int],
    config: GeometryConfig,
) -> float:
    """
    Return the offset of a port from the center of its node face.

    spec.md, section "Шаг портов и переполнение грани". list_sizes are the
    longest port lists on the left and on the right side of the gate. The
    center of the gate stays in the middle of the face while both sides fit
    at the minimum port pitch. If one side does not fit, the center moves
    toward the other side by the missing width. Both faces of a gate move
    it the same way, so a straight edge stays straight. The width of the
    column lets the other side still fit, see
    _GeometryBuilder._column_width.
    """

    half_width = node_width / 2 - config.port_margin
    left_needed = list_sizes[0] * config.min_port_pitch
    right_needed = list_sizes[1] * config.min_port_pitch
    center_offset = 0.0
    if left_needed > half_width:
        center_offset = left_needed - half_width
    elif right_needed > half_width:
        center_offset = half_width - right_needed
    if slot == 0:
        return center_offset
    side_width = (
        half_width + center_offset if slot < 0 else half_width - center_offset
    )
    return center_offset + slot * port_list_pitch(list_size, side_width, config)


class _GeometryBuilder:
    def __init__(
        self,
        normalized_graph: NormalizedGraph,
        layout: StructureLayout,
        config: GeometryConfig,
        lane_counts: Mapping[StructureChannelId, int],
        bottom_segments: Sequence[CorridorSegment],
        side_entries: Mapping[StructureChannelId, Sequence[str]],
        gate_port_lists: Mapping[StructureGate, Tuple[int, int]],
    ) -> None:
        self.layout: StructureLayout = layout
        self.config: GeometryConfig = config
        self.lane_counts: Mapping[StructureChannelId, int] = lane_counts
        self.side_entries: Mapping[StructureChannelId, Sequence[str]] = (
            side_entries
        )
        self.gate_port_lists: Mapping[StructureGate, Tuple[int, int]] = (
            gate_port_lists
        )
        self.face_gates: Dict[Tuple[str, Face], StructureGate] = {}
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
            gate_port_lists=self.gate_port_lists,
            face_gates=self.face_gates,
        )

    def _channel_size(self, channel_id: StructureChannelId) -> float:
        lane_count = self.lane_counts.get(channel_id, 0)
        if channel_id.kind is ChannelKind.COLUMN:
            return max(
                horizontal_channel_size(lane_count, self.config),
                self._side_entry_size(channel_id, lane_count),
            )
        if channel_id.is_horizontal:
            return horizontal_channel_size(lane_count, self.config)
        return vertical_channel_size(lane_count, self.config)

    def _side_entry_size(
        self, channel: StructureChannelId, lane_count: int
    ) -> float:
        """
        Return the size of a column channel that puts its lanes not above
        the outer vertical channels of the children its lines enter.

        spec.md, section "Проходные порты". A line from a column channel
        enters a child container through its side face only opposite the
        outer vertical channel of the child, below its header and its top
        corridor. The top corridor can get more lanes than the path search
        expected, so the channel grows until its top lane lies there and the
        nodes under it move down. The rule holds for all lanes of the
        channel: the lane of each line is not known when the parent is
        sized.
        Both heights count from the top of the columns.
        """

        children = self.side_entries.get(channel, ())
        if len(children) == 0:
            return 0
        lowest_top = max(
            self.config.container_header_height
            + self._channel_size(
                StructureChannelId(ChannelKind.TOP_CORRIDOR, child_id_)
            )
            for child_id_ in children
        )
        return (
            2 * (lowest_top - self._column_channel_top(channel))
            + (lane_count - 1) * self.config.lane_pitch
        )

    def _size(self, node_id: str) -> Tuple[float, float]:
        """
        Return the size of a node. Stage 5: from the inside out.
        """

        if node_id in self.sizes:
            return self.sizes[node_id]
        if not self.is_composite[node_id]:
            place = self.layout.places.get(node_id)
            size = (
                self.config.node_width
                if place is None
                else self._column_width(place.container_id, place.column),
                self.config.node_height,
            )
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
            self._column_width(container_id, column_index),
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

    def _column_width(
        self, container_id: Optional[str], column_index: int
    ) -> float:
        """
        Return the width of a column of simple nodes.

        spec.md, section "Шаг портов и переполнение грани". A gate needs room
        for the longest list on each side at the minimum port pitch. If the
        node width is not enough even with a moved gate center, all nodes of
        the column get wider.
        """

        width = self.config.node_width
        for (channel_, column_), (
            left_,
            right_,
        ) in self.gate_port_lists.items():
            if channel_.container_id != container_id or column_ != column_index:
                continue
            width = max(
                width,
                grid_ceil(
                    (left_ + right_) * self.config.min_port_pitch
                    + 2 * self.config.port_margin,
                    self.config,
                ),
            )
        return width

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
        segment takes the height of the lane: it belongs to the row of that
        lane. The other segments form the corridor: each lies the clearance
        below the lowest column it passes over, and at least one lane pitch
        below each overlapping corridor segment with a smaller lane.

        The segments take their places in lane order, which follows
        right-hand traffic. A segment that meets an overlapping placed
        segment closer than one lane pitch moves down. So the lane order
        decides where two segments meet, and segments of different rows
        keep their own heights. The corridor size below the tallest column
        fits the lowest segment.

        A corridor segment that leaves through a side face also keeps one
        lane pitch from the lanes of a column channel of the parent that
        enters through the same face, see _face_entry_lanes.
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

        area_width = x

        def end_x(end: SegmentEnd) -> float:
            if isinstance(end, LaneEnd) and end.channel not in verticals:
                child_column_ = self._child_column(
                    container_id, end.channel.container_id
                )
                if child_column_ is not None:
                    # The segment enters the outer vertical channel of a
                    # child container through its side face: the columns
                    # under the segment end at the face.
                    child_left_, child_right_, _ = column_spans[child_column_]
                    return (
                        child_left_ if end.channel.index == 0 else child_right_
                    )
                # The segment leaves the container through a side face: the
                # lane lies in the parent next to that face.
                own_column_ = self._own_column(container_id)
                return 0.0 if end.channel.index == own_column_ else area_width
            if isinstance(end, LaneEnd):
                return verticals[end.channel] + centered_lane_offset(
                    self._channel_size(end.channel),
                    self.lane_counts[end.channel],
                    end.lane,
                    config,
                )
            node_width_, _ = self._size(end.node_id)
            place_ = self.layout.places[end.node_id]
            left_, _, _ = column_spans[place_.column]
            gate_ = (self.layout.channel_below(end.node_id), place_.column)
            return (
                left_
                + node_width_ / 2
                + gate_port_offset(
                    end.slot,
                    end.list_size,
                    node_width_,
                    self.gate_port_lists.get(gate_, (0, 0)),
                    config,
                )
            )

        # (segment, low x, high x, base height, the segment is in a row).
        bases: List[Tuple[CorridorSegment, float, float, float, bool]] = []
        for segment_ in self.bottom_segments.get(container_id, []):
            first_x_, second_x_ = (end_x(end_) for end_ in segment_.ends)
            low_, high_ = min(first_x_, second_x_), max(first_x_, second_x_)
            lowest_y_, through_y_ = corridor_segment_y(
                column_spans,
                low_,
                high_,
                [
                    self._through_lane_y(
                        container_id, through_.channel, through_.lane
                    )
                    for through_ in segment_.through_lanes
                ]
                + [
                    self._child_segment_y(container_id, key_)
                    for key_ in segment_.through_segments
                ],
                config,
            )
            # A line that enters the outer vertical channel of a child
            # through its side face lies below the top corridor of the
            # child: it never meets a lane of that corridor.
            entry_floor_ = max(
                (
                    self._side_entry_floor(container_id, end_)
                    for end_ in segment_.ends
                ),
                default=lowest_y_,
            )
            if through_y_ is not None and through_y_ < entry_floor_:
                through_y_ = None
            lowest_y_ = max(lowest_y_, entry_floor_)
            is_row_ = through_y_ is not None
            bases.append(
                (
                    segment_,
                    low_,
                    high_,
                    through_y_ if through_y_ is not None else lowest_y_,
                    is_row_,
                )
            )

        face_lanes = self._face_entry_lanes(container_id, area_width)
        lines: Dict[Tuple[str, int], Tuple[float, float, float]] = {}
        placed: List[Tuple[float, float, float]] = []
        corridor_placed: List[Tuple[float, float, float]] = []
        for segment_, low_, high_, base_y_, is_row_ in sorted(
            bases, key=lambda base_: (base_[0].lane, base_[0].key)
        ):
            y_ = base_y_
            if not is_row_:
                for placed_low_, placed_high_, placed_y_ in corridor_placed:
                    if not (high_ < placed_low_ or placed_high_ < low_):
                        y_ = max(y_, placed_y_ + config.lane_pitch)
            y_ = _free_y(
                y_,
                low_,
                high_,
                placed if is_row_ else placed + face_lanes,
                config.lane_pitch,
            )
            if not is_row_:
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

    def _face_entry_lanes(
        self, container_id: Optional[str], area_width: float
    ) -> List[Tuple[float, float, float]]:
        """
        Return the lanes of the column channels of the parent that enter a
        container through its side faces, as points on the faces.

        spec.md, section "Проходные порты". A line from such a lane crosses
        the face at the height of the lane. A corridor segment of the
        container that leaves through the same face at that height would
        cross the face at the same point, and the two lines would lie on
        top of each other. All lanes of the channel count: the container is
        placed before its parent, so the lane of each line is not known
        yet. The coordinates are local, as in _bottom_corridor: x 0 or
        area_width at the left or the right face, y from the top of the
        columns of the container.
        """

        if container_id is None:
            return []
        own_column = None
        result: List[Tuple[float, float, float]] = []
        for channel_, children_ in self.side_entries.items():
            if container_id not in children_:
                continue
            if own_column is None:
                own_column = self._own_column(container_id)
            face_x_ = 0.0 if channel_.index < own_column else area_width
            columns_top_ = self.config.container_header_height + (
                self._channel_size(
                    StructureChannelId(ChannelKind.TOP_CORRIDOR, container_id)
                )
            )
            result.extend(
                (
                    face_x_,
                    face_x_,
                    self._column_lane_y(channel_, lane_) - columns_top_,
                )
                for lane_ in range(self.lane_counts.get(channel_, 0))
            )
        return result

    def _side_entry_floor(
        self, container_id: Optional[str], end: SegmentEnd
    ) -> float:
        """
        Return the lowest top of a line that enters a child at this end.

        For an end in the outer vertical channel of a child container, this
        is the top of that channel: the header and the top corridor of the
        child lie above it. The y counts from the top of the columns, where
        the child stands. Other ends set no floor.
        """

        if not isinstance(end, LaneEnd):
            return -math.inf
        child_id = end.channel.container_id
        if (
            child_id == container_id
            or self._child_column(container_id, child_id) is None
        ):
            return -math.inf
        return self.config.container_header_height + self._channel_size(
            StructureChannelId(ChannelKind.TOP_CORRIDOR, child_id)
        )

    def _child_column(
        self, container_id: Optional[str], child_id: Optional[str]
    ) -> Optional[int]:
        """
        Return the column of a child container, or None if it is no child.
        """

        for index_, column_ in enumerate(self.layout.columns[container_id]):
            if column_.is_composite and column_.node_ids[0] == child_id:
                return index_
        return None

    def _own_column(self, container_id: Optional[str]) -> int:
        """
        Return the column of a container in its parent.
        """

        for columns_ in self.layout.columns.values():
            for index_, column_ in enumerate(columns_):
                if column_.is_composite and column_.node_ids[0] == container_id:
                    return index_
        raise AssertionError(container_id)

    def _through_lane_y(
        self,
        container_id: Optional[str],
        channel: StructureChannelId,
        lane: int,
    ) -> float:
        """
        Return the y of a lane that a segment continues straight.

        The lane lies in a column channel of the container, or in a column
        channel or the top corridor of a child container. The y counts from
        the top of the columns of the container. A child container stands at
        the top of its column.
        """

        if channel.container_id == container_id:
            return self._column_lane_y(channel, lane)
        assert channel.container_id is not None
        child_top = self.config.container_header_height
        top_corridor = StructureChannelId(
            ChannelKind.TOP_CORRIDOR, channel.container_id
        )
        if channel == top_corridor:
            return child_top + centered_lane_offset(
                self._channel_size(top_corridor),
                self.lane_counts[top_corridor],
                lane,
                self.config,
            )
        return (
            child_top
            + self._channel_size(top_corridor)
            + self._column_lane_y(channel, lane)
        )

    def _child_segment_y(
        self, container_id: Optional[str], key: Tuple[str, int]
    ) -> float:
        """
        Return the y of a segment under the columns of a child container.

        The y counts from the top of the columns of the container. A child
        container stands at the top of its column, and the child is placed
        first.
        """

        for column_ in self.layout.columns[container_id]:
            if not column_.is_composite:
                continue
            child_id_ = column_.node_ids[0]
            corridor_ = self._bottom_corridor(
                child_id_, self.layout.columns[child_id_]
            )
            if key in corridor_.lines:
                top_corridor_ = StructureChannelId(
                    ChannelKind.TOP_CORRIDOR, child_id_
                )
                return (
                    self.config.container_header_height
                    + self._channel_size(top_corridor_)
                    + corridor_.lines[key][2]
                )
        raise AssertionError(f"{key} lies under no child of {container_id}")

    def _column_lane_y(self, channel: StructureChannelId, lane: int) -> float:
        """
        Return the y of a column channel lane from the top of the columns.
        """

        assert not self.layout.columns[channel.container_id][
            channel.index
        ].is_composite
        return self._column_channel_top(channel) + centered_lane_offset(
            self._channel_size(channel),
            self.lane_counts[channel],
            lane,
            self.config,
        )

    def _column_channel_top(self, channel: StructureChannelId) -> float:
        """
        Return the y of the top of a column channel from the top of the
        columns.
        """

        return (channel.gap + 1) * self.config.node_height + sum(
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
                        Rect(
                            left,
                            y,
                            self._column_width(container_id, column_index),
                            gap_size_,
                        ),
                    )
                )
                y += gap_size_
            self._place_node(node_id_, left, y)
            y += self.config.node_height

    def _place_node(self, node_id: str, left: float, top: float) -> None:
        width, height = self._size(node_id)
        self.node_rects[node_id] = Rect(left, top, width, height)
        if not self.is_composite[node_id]:
            place = self.layout.places.get(node_id)
            if place is not None:
                self.face_gates[(node_id, Face.TOP)] = (
                    self.layout.channel_above(node_id),
                    place.column,
                )
                self.face_gates[(node_id, Face.BOTTOM)] = (
                    self.layout.channel_below(node_id),
                    place.column,
                )
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
