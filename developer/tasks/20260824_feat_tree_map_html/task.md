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

The serialized weight shall be the actual size calculated for the document or
node. The data generator shall not clamp small weights to a minimum value.
Rendering constraints shall use the renderer's minimum node dimensions and
visibility thresholds without changing the weight.

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
the stack's outer rectangle. If squarify cannot satisfy the limit locally, the
fallback shall search for balanced rows that can contain multiple nodes while
respecting minimum node height and label width. Space above these minimums
shall remain weight-based. The parent shall remain collapsed only when the
fallback cannot fit every child.

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
The Back action shall return to the previously visited node. A horizontal
transition to an ordinary sibling or synthetic group shall replace the current
history entry instead of adding another one. After browsing any number of
siblings, Back shall return to the node from which the user entered that
level.
The toolbar shall show the visited nodes before the current node as a text
breadcrumb with `•` separators. It shall not repeat the current node and shall
remain separate from the structural ancestor controls.
The breadcrumb shall precede a directly interactive Back SVG without button
markup or button styling. When the breadcrumb is empty, the icon shall be
hidden while the toolbar retains its minimum height.

When the focused node has siblings, the renderer shall provide direct
navigation to the preceding and following nodes in its parent's `children`
array. This array shall preserve source document traversal order. Rectangle
layout may place the nodes in a different visual order because layout remains
weight-based. Synthetic groups shall use the order of the groups created for
the same source parent.

The focused node's header inside the canvas shall contain three columns: the
previous button, the current label, and the next button. The previous button
shall contain the preceding sibling's label followed by a left-pointing
symbol. The next button shall contain a right-pointing symbol followed by the
following sibling's label. The side columns shall have equal widths, and the
center column shall be twice as wide. The buttons shall fill their columns.

The current label shall use bold text. Every label shall stay on one line, use
an ellipsis when it does not fit, and expose its complete text in a `title`
attribute. A button without a sibling in its direction shall be disabled.

When the focused node is the project root, its header shall omit both sibling
labels and both navigation buttons. The project label shall use the complete
header width and remain centered without the three-column grid. This exception
shall not apply to other nodes that happen to have no siblings.

Ordinary nodes and synthetic groups shall use the same header markup. A
focused synthetic group shall show its item range and total, such as
`1–96 of 666`; adjacent group labels shall show their own item ranges.

While the pointer is over the tree map's complete section, including its
toolbar, ancestor navigation, and canvas, the left and right arrow keys shall
use the same sibling navigation. The up arrow shall navigate to the focused
node's actual parent. Outside the section, these keys shall retain their native
behavior.

While the pointer is over the section, Backspace shall invoke the history-based
Back action. The renderer shall not intercept Backspace from an input,
textarea, or editable element.

Each tile shall show at most one primary action. A document tile shall navigate
to its Document view without an anchor. An SDoc node shall open the full-node
preview modal. In static output, where the modal endpoint is unavailable, the
same tile shall instead show its anchored Document view action. The SDoc node's
anchored Document view URL shall remain in serialized server data for secondary
interaction even though the server screen does not show a separate action for
it. The project root and synthetic groups shall not provide an action.

The actions shall reuse the DEEP-TRACE destinations and icons:
`ico16_go_to_doc.svg` for Document view and `ico16_maximize.svg` for the modal.
Each control shall appear as a directly interactive SVG element without the
DEEP-TRACE button wrapper. It shall be visible only while the pointer is over
its node. A branch shall place it at the upper-right edge of its header, where
it limits the space available to the title. A leaf shall place it at its
lower-right edge.

While Shift is held over a real node, the node shall show a compact information
panel with its title, MID, and UID.

Shift+Click shall invoke the tile's primary action, and Shift+Alt+Click shall
invoke its secondary action. The primary action shall open the modal for an
SDoc node and the Document view for a document tile. In static output, it shall
use the SDoc node's fallback Document view action. The secondary action shall
always navigate to the item's Document view URL. This URL includes the node
anchor for an SDoc node and has no anchor for a document tile.

The tree map screen shall suppress Shift+Click and Shift+Alt+Click outside tree
map tiles. This includes controls rendered in the shared modal outlet. The
screen reserves both combinations for tile actions, so a modifier left pressed
after using the map shall not trigger link navigation or a button action
elsewhere on the screen. Clicks without Shift shall keep their normal behavior.

End-to-end tests shall locate stable controls and observable results through
`data-testid` attributes where standard Selenium interaction is sufficient.
CSS classes and internal DOM nesting shall not form the behavioral test
contract. The existing tree map test shall migrate to this convention after
the screen behavior and controls settle.

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

Shape scoring shall use a configurable target node aspect ratio instead of
assuming that square nodes are ideal. The initial target shall be `1.6`, so the
layout prefers moderately wide text-bearing nodes without forcing one strip
orientation. A value of `1` shall restore classic square-oriented squarify
behavior, including the original width-versus-height orientation threshold.
The constrained fallback shall use the same target.

The generated node markup shall separate the transparent positioning element,
the styled surface, the header, and the child container. Additional node
content, such as document links, shall belong to the surface rather than the
positioning element.

The serialized real-node data shall include the title, MID, UID, and Document
view URL required by the node actions and information panel. SDoc nodes shall
also receive a preview URL when the screen runs on the server. The project root
and browser-created synthetic groups shall not receive node-action URLs. The
preview action shall use the same full-node server endpoint and modal flow as
DEEP-TRACE.

The browser renderer shall keep layout and level-of-detail settings in one
options object. The initial settings shall cover header height, depth and DOM
limits, node padding, visual gaps, grouping limits, and visibility thresholds.
It shall publish CSS-facing settings as custom properties.
