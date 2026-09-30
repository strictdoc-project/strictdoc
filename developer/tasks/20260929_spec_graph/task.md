# Specification graph

## WHAT

StrictDoc provides a "Specification graph" screen. The screen shows the
project structure as an SVG diagram of nodes, nested containers, and the
relations between them.

The work has five parts:

1. Graph generator with a public API.
2. Interactivity of the generated diagram.
3. StrictDoc adapter.
4. StrictDoc feature integration.
5. SVG file export.

### 1. Graph generator

- The generator converts an abstract graph model into SVG.
- The generator does not import or depend on the StrictDoc document model.
- The input model has nodes, composite nodes (nodes that contain other
  nodes), and typed relations.
- `spec.md` in this folder defines the model, the layout and routing rules,
  and the result invariants.
- The same input produces the same output.
- A developer gallery page renders a set of example graphs for visual
  control. Each gallery case is also a test input.

### 2. Interactivity

- Pan and zoom, with zoom controls and fit-to-view.
- Hover and focus highlight a relation and the nodes it connects.
- Shift + hover shows the node data. Shift + click opens the node link in
  a new tab. A plain click does not open the link.
- The legend and the controls stay fixed while the diagram moves.
- Interactivity works on the server-generated inline SVG. The feature does
  not add a client-side graph library.

### 3. StrictDoc adapter

The adapter converts the traceability index into the generator model. The
adapter supports two views:

- Documents: a flat graph. Each document is one node. A relation between
  two documents exists if any node in one document relates to a node in the
  other document.
- Nodes: a nested graph. Documents and sections are composite nodes.
  Requirements are nodes. The view keeps the document structure and the
  order of nodes in each document.

### 4. StrictDoc feature integration

- A `ProjectFeature` flag enables the screen. The flag is not in the default
  feature set.
- The screen is available in static export and in server mode.
- The navigation shows the screen when the feature is enabled.
- The screen has a help modal, a legend, and a toolbox with the view
  switch and the zoom controls.
- Feature settings in the project configuration: to be defined.
- The screen catches `GraphModelError` from the generator. The screen shows
  the error text instead of the diagram and logs the error. The rest of the
  export continues.

### 5. SVG file export

- In server mode, the screen offers to save the diagram as an SVG file.
- Static export writes the SVG file into the export folder. The screen
  links to the file.
- The SVG file contains the legend.
- The SVG file has no interactivity.

## WHY

A StrictDoc project can have many documents connected through relations of
different types. StrictDoc has no single view that shows how documents and
their nodes relate to each other. Such a view also shows modeling problems,
for example a node with parents on different levels of the specification
hierarchy, or cycles between documents.

## HOW

The generator comes first and is developed against abstract example graphs.
The StrictDoc adapter and the feature screen come after the generator
passes the gallery cases.

Order of work:

1. Specification of the generator (`spec.md`).
2. Generator stages and their unit tests, one stage at a time.
3. Developer gallery page.
4. Interactivity.
5. StrictDoc adapter for the documents view and the nodes view.
6. Feature registration, export screen, server route, navigation entry,
   help, legend, toolbox.
7. SVG file export.

### Code location

- Feature: `strictdoc/features/specification_graph/`, with `generator.py`,
  `view_object.py`, and templates under
  `strictdoc/features/specification_graph/templates/`.
- Generator: `strictdoc/features/specification_graph/svg_graph/`, a
  subpackage of the feature without StrictDoc imports.
- Gallery: `developer/examples/specification_graph/`.

### Tests

- Unit tests for each generator stage, against the stage contract in
  `spec.md`.
- Each unit test docstring names the code under test ("Code:") and the
  breakages that fail the test ("Fails if:").
- `developer/examples/specification_graph/mutations.py` applies each
  breakage to the code, runs the unit tests, and reports a breakage that
  fails no test or a test that no breakage fails.
- Integration tests (`tests/integration/`) for export of the screen.
- End-to-end tests for the screen and the interactivity, run with
  `--headless`.
