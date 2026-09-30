import xml.etree.ElementTree as ET
from itertools import combinations
from typing import Dict, List

import pytest

from developer.examples.specification_graph.gallery_cases import (
    GALLERY_CASES,
    GalleryCase,
)
from strictdoc.features.specification_graph.svg_graph.levels_geometry import (
    GeometryConfig,
    Rect,
)
from strictdoc.features.specification_graph.svg_graph.model import LayoutMode
from strictdoc.features.specification_graph.svg_graph.normalization import (
    NormalizedGraph,
    normalize_graph,
)
from strictdoc.features.specification_graph.svg_graph.structure_geometry import (
    ChannelKind,
    StructureGeometry,
    compute_structure_geometry,
)
from strictdoc.features.specification_graph.svg_graph.structure_layout import (
    compute_structure_layout,
)
from strictdoc.features.specification_graph.svg_graph.svg_serializer import (
    serialize_structure_svg,
)

SVG_NAMESPACE = "{http://www.w3.org/2000/svg}"

STRUCTURE_CASES = [
    case_ for case_ in GALLERY_CASES if case_.graph.mode is LayoutMode.STRUCTURE
]


def _case(title: str) -> GalleryCase:
    return next(case_ for case_ in GALLERY_CASES if case_.title == title)


def _geometry(case: GalleryCase) -> StructureGeometry:
    normalized_graph = normalize_graph(case.graph)
    return compute_structure_geometry(
        normalized_graph, compute_structure_layout(normalized_graph)
    )


def _inside(inner: Rect, outer: Rect) -> bool:
    return (
        outer.x <= inner.x
        and outer.y <= inner.y
        and inner.x + inner.width <= outer.x + outer.width
        and inner.y + inner.height <= outer.y + outer.height
    )


def _overlap(first: Rect, second: Rect) -> bool:
    return (
        first.x < second.x + second.width
        and second.x < first.x + first.width
        and first.y < second.y + second.height
        and second.y < first.y + first.height
    )


def test_container_size_comes_from_its_columns() -> None:
    """
    A container size is the sum of its header, corridors, and columns.

    Code: structure_geometry._GeometryBuilder._size,
    structure_geometry._GeometryBuilder._area_size.
    Fails if:
    - the container height does not include the header.
    """

    config = GeometryConfig()
    geometry = _geometry(_case("Long container titles"))

    channel = config.min_channel_size
    section = geometry.node_rects["Sec"]
    assert section.width == channel + config.node_width + channel
    assert section.height == (
        config.container_header_height
        + channel
        + (2 * config.node_height + channel)
        + channel
    )


def test_columns_align_at_the_top_and_corridor_lies_below_the_tallest() -> None:
    """
    Columns align at the top. The bottom corridor lies below the tallest.

    Code: structure_geometry._GeometryBuilder._place_area.
    Fails if:
    - the bottom corridor lies below a shorter column than the tallest.
    """

    geometry = _geometry(_case("Columns of different height"))

    tops = {geometry.node_rects[id_].y for id_ in ("Short", "Tall", "Medium")}
    assert len(tops) == 1
    bottom_corridor = next(
        channel_
        for channel_ in geometry.channels
        if channel_.kind is ChannelKind.BOTTOM_CORRIDOR
        and channel_.container_id == "Document"
    )
    tall = geometry.node_rects["Tall"]
    assert bottom_corridor.rect.y == tall.y + tall.height


def test_block_stands_above_the_row_and_is_not_wider() -> None:
    """
    The block of unconnected root children stands above the row.

    Code: structure_geometry._GeometryBuilder.build,
    structure_geometry._skyline_positions.
    Fails if:
    - the block uses the square rule while a connected row exists.
    """

    geometry = _geometry(_case("Root with connected and unconnected documents"))

    row = [geometry.node_rects[id_] for id_ in ("A", "B", "C")]
    block = [geometry.node_rects[id_] for id_ in ("D", "E", "F", "G")]
    row_right = max(rect_.x + rect_.width for rect_ in row)
    assert max(rect_.y + rect_.height for rect_ in block) < min(
        rect_.y for rect_ in row
    )
    assert max(rect_.x + rect_.width for rect_ in block) <= row_right
    # The block takes the width of the row: D, E, and F fit side by side.
    # G takes the highest free place: below D, the shortest of the three.
    top = geometry.node_rects["D"].y
    assert [geometry.node_rects[id_].y for id_ in ("E", "F")] == [top, top]
    assert geometry.node_rects["G"].x == geometry.node_rects["D"].x
    assert geometry.node_rects["G"].y > top


def test_block_without_row_is_close_to_a_square() -> None:
    """
    Without a connected row, the block is the closest to a square.

    Code: structure_geometry._block_width.
    Fails if:
    - the block picks a shelf width that is not the closest to a square.
    """

    geometry = _geometry(_case("Root without relations"))

    lefts = {geometry.node_rects[f"Doc {index_}"].x for index_ in range(1, 7)}
    # Two columns: 520 x 670 px. Three columns give 752 x 486 px, farther
    # from a square.
    assert len(lefts) == 2
    assert (geometry.width, geometry.height) == (520, 670)


def test_serializer_draws_containers_before_their_children() -> None:
    """
    A container is a frame with a header line, drawn before its children.

    Code: svg_serializer.serialize_structure_svg,
    svg_serializer._render_nodes.
    Fails if:
    - a container is drawn as a simple node without the header line.
    """

    case = _case("Deep nesting")
    normalized_graph = normalize_graph(case.graph)
    svg = serialize_structure_svg(normalized_graph, _geometry(case))

    root = ET.fromstring(svg)
    groups = [
        group_
        for group_ in root.iter(f"{SVG_NAMESPACE}g")
        if "specification-graph-node" in group_.get("class", "").split(" ")
    ]
    order = [group_.get("data-node-id") for group_ in groups]
    assert order.index("Level 1") < order.index("Level 2")
    assert order.index("Level 2") < order.index("Deep 1")
    composite_ids = [
        group_.get("data-node-id")
        for group_ in groups
        if "specification-graph-node--composite"
        in group_.get("class", "").split(" ")
    ]
    assert composite_ids == ["Document", "Level 1", "Level 2", "Level 3"]
    for group_ in groups:
        header_lines_ = group_.findall(f"{SVG_NAMESPACE}line")
        is_composite_ = group_.get("data-node-id") in composite_ids
        assert len(header_lines_) == (1 if is_composite_ else 0)


@pytest.mark.parametrize(
    "case", STRUCTURE_CASES, ids=[case_.title for case_ in STRUCTURE_CASES]
)
def test_structure_geometry_invariants(case: GalleryCase) -> None:
    """
    Layout invariants of the structure mode on every structure case.

    Code: structure_geometry.compute_structure_geometry.
    Fails if:
    - a child lies outside its container or over the container header.
    - two siblings overlap.
    - a node lies outside the SVG.
    """

    normalized_graph = normalize_graph(case.graph)
    geometry = _geometry(case)

    _assert_children_inside_containers(normalized_graph, geometry)
    _assert_siblings_do_not_overlap(normalized_graph, geometry)
    svg_rect = Rect(0, 0, geometry.width, geometry.height)
    for rect_ in geometry.node_rects.values():
        assert _inside(rect_, svg_rect)
    assert _geometry(case) == geometry


def _assert_children_inside_containers(
    normalized_graph: NormalizedGraph, geometry: StructureGeometry
) -> None:
    for node_ in normalized_graph.nodes:
        parent_id_ = normalized_graph.parent_ids[node_.node_id]
        if parent_id_ is None:
            continue
        rect_ = geometry.node_rects[node_.node_id]
        assert _inside(rect_, geometry.node_rects[parent_id_])
        header_ = geometry.header_rects[parent_id_]
        assert rect_.y >= header_.y + header_.height


def _assert_siblings_do_not_overlap(
    normalized_graph: NormalizedGraph, geometry: StructureGeometry
) -> None:
    siblings: Dict[object, List[Rect]] = {}
    for node_ in normalized_graph.nodes:
        siblings.setdefault(
            normalized_graph.parent_ids[node_.node_id], []
        ).append(geometry.node_rects[node_.node_id])
    for rects_ in siblings.values():
        for first_, second_ in combinations(rects_, 2):
            assert not _overlap(first_, second_)
