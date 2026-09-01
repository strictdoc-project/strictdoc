# HTML/CSS tree map

## WHAT

StrictDoc shall provide the `tree_map_html` feature. The feature shall be
activated through the project configuration and generate
`tree_map_html.html`.

The screen shall provide these tree maps:

- the complete document tree;
- requirements coverage by source files;
- requirements coverage by test files.

Each tree map shall show the document hierarchy as nested HTML elements styled
with CSS. A node's area shall represent its weight. Its color shall represent
the value calculated for the selected tree map.

The browser shall use the available rectangle's actual aspect ratio when it
calculates the layout. It shall recalculate the layout when the viewport size
changes.

Each node shall reserve a header row above its children. The renderer shall
exclude this row from the rectangle available to the children. Renderer options
shall control the header height and label visibility. A leaf node shall use a
leaf-specific style without a child area.

Each node shall reserve configurable padding around its header and child area.
The renderer shall exclude this padding from the child layout. Visual borders
shall not change the calculated geometry.

The renderer shall support configurable visual gaps between adjacent nodes.
These gaps shall not change node weights or rectangle layout.

Each node shall use a transparent outer element for absolute positioning. A
separate inner surface shall provide the node background and contain its header
and future node information. The surface shall be inset by half of the visual
gap. Adjacent outer elements shall touch without CSS margins.

The child container shall remain transparent. Its inset shall include half of
the visual gap and the node padding. Gaps between children shall reveal their
parent's surface instead of a fixed page color.

The renderer shall distinguish the immediate children of the focused root from
deeper contextual nodes. Current-level nodes shall use a stronger surface
outline.

Python shall prepare the hierarchy and the StrictDoc-specific data shown in the
tree maps. The browser renderer shall receive this data as JSON. It shall
calculate the layout and render the supplied data without containing the
StrictDoc-specific rules that define it.

The Python design shall allow the addition of user-defined functions that
control what a tree map shows.

The screen shall support projects with large numbers of documents and
requirements. Their tree maps shall remain usable for visualization and
navigation.

The renderer shall limit visible depth and DOM node count. It shall expand the
hierarchy by level so that one deep branch cannot hide its peers. A branch
shall show either all immediate display children or none.

The renderer shall enforce a configurable minimum node height. When a vertical
stack contains a shorter node and taller siblings have sufficient height, the
layout shall transfer only the deficit from those siblings without changing
the stack's outer rectangle. If squarify cannot satisfy the limit locally but
the complete sibling list fits as horizontal rows, the renderer shall use that
fallback and distribute height above the minimum by weight. The parent shall
remain collapsed only when the fallback also cannot fit every child.

When a node has too many direct children, the renderer shall replace them with
synthetic groups. A synthetic group shall preserve the combined weight of its
children. It shall remain collapsed in its parent's view and reveal its source
children after the user enters the group.

The focused node shall remain visible inside the canvas as the non-interactive
outer node around its children. It shall not have a pointer hover state or
activate itself. Its immediate children shall remain the active current level.

Above the canvas, the renderer shall show one navigation row for each actual
ancestor of the focused node. These rows shall represent the source hierarchy,
not the history of clicks. Each row shall navigate directly to that ancestor.
The focused node shall stay in the canvas and shall not be duplicated in the
ancestor rows.

The renderer shall keep click history independently from the source hierarchy.
The Back action shall return to the previously visited node. This behavior for
horizontal transitions between synthetic groups remains subject to UX review.

When the focused node is a synthetic group, the renderer shall provide direct
navigation to the preceding and following synthetic groups created for the
same source parent. This horizontal navigation shall not apply to ordinary
source nodes.

## WHY

StrictDoc needs a tree map rendered with project-owned HTML and CSS.

Tree map contents depend on StrictDoc's document models and traceability data.
Keeping these calculations in Python allows projects to define what a tree map
shows without changing the browser renderer.

## HOW

Implement the feature in `strictdoc/features/tree_map_html`.

The Python part shall build the tree map data and serialize it as JSON. The
browser part shall calculate the rectangle layout, create the HTML elements,
and style them with CSS.

The browser shall use a squarified tree map layout calculated from the real
pixel dimensions of each child area. It shall convert the resulting geometry
to CSS percentages after the calculation.

The generated node markup shall separate the transparent positioning element,
the styled surface, the header, and the child container. Additional node
content, such as document links, shall belong to the surface rather than the
positioning element.

The browser renderer shall keep layout and level-of-detail settings in one
options object. The initial settings shall cover header height, depth and DOM
limits, node padding, visual gaps, grouping limits, and visibility thresholds.
It shall publish CSS-facing settings as custom properties.
