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

When a node has too many direct children, the renderer shall replace them with
synthetic groups. A synthetic group shall preserve the combined weight of its
children. It shall remain collapsed in its parent's view and reveal its source
children after the user enters the group.

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

The browser renderer shall keep layout and level-of-detail settings in one
options object. The initial settings shall cover header height, depth and DOM
limits, grouping limits, and visibility thresholds.
