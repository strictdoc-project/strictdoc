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

Python shall prepare the hierarchy and the StrictDoc-specific data shown in the
tree maps. The browser renderer shall receive this data as JSON. It shall
calculate the layout and render the supplied data without containing the
StrictDoc-specific rules that define it.

The Python design shall allow the addition of user-defined functions that
control what a tree map shows.

The screen shall support projects with large numbers of documents and
requirements. Their tree maps shall remain usable for visualization and
navigation.

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
