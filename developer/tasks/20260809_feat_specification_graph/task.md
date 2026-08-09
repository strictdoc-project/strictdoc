# FEATURE: Specification graph (document-level relation diagram)

## WHAT

StrictDoc SHALL provide a new export screen, "Specification graph", showing
an SVG block diagram of the project's documents and the relations between
them.

### Diagram content

- Each document is rendered as a rectangle containing (at minimum) the
  document title.
- An arrow is drawn between two documents whenever any node in one document
  has a relation to a node in a different document, regardless of relation
  type. Relations between nodes within the same document are not shown.
- The arrow points from the child (source) document to the parent (target)
  document, i.e. upward, mirroring the direction of a Parent/Child relation.
- Multiple relations between the same pair of documents are drawn as a
  single arrow between those two documents (the diagram is document-level,
  not node-level). The only styling distinction in the diagram is the
  "skip" arrow case below, which is about layout, not relation type.

### Layout ("highway" layered layout)

- Documents are arranged in horizontal rows ("floors"). Row 0 (topmost) is
  reserved for every document that has no outgoing parent-relation to any
  other document.
- A document with at least one outgoing parent-relation is placed one row
  below the row of its parent document.
- Within a row, documents are ordered left to right in the same order they
  appear in the project tree (`strictdoc.toml` / directory tree order).
- **Highway rule.** A document can have parent-relations reaching documents
  on more than one row (e.g. a direct relation to a row-0 document, and
  also, via a different relation, an ancestor chain that bottoms out at
  row 2). This is flagged as a project modeling issue (see below), and the
  document's row is resolved deterministically:
  - Compute, for each parent-relation, the depth (row number) of the full
    ancestor chain reached through that relation.
  - The document is placed one row below the **deepest** such chain (the
    chain with the most rows/levels between the document and a row-0
    document wins).
  - Relations that point to a shallower ancestor than the winning chain
    become "skip" arrows that visually cross more than one row boundary.
    These SHALL remain visually distinguishable (e.g. dashed or colored) so
    the modeling issue is visible in the diagram itself, not just in a log.
- Document-level cycles are not a case this feature needs to handle:
  StrictDoc's existing `TreeCycleDetector` already rejects cyclic relations
  at project load time, so a cyclic document graph cannot occur in practice.
- A document with no relations at all (isolated) is placed in row 0, with
  no arrows.

### Delivery

- Rendered as a new export screen (e.g. `specification_graph.html`),
  generated as part of `strictdoc export`, following the existing
  `tree_map` / `project_statistics` screen pattern:
  - `strictdoc/features/specification_graph/generator.py`,
    `view_object.py`, `templates/features/specification_graph/index.jinja`.
  - Gated by a new `ProjectFeature.SPECIFICATION_GRAPH_SCREEN` flag in
    `strictdoc/core/project_config.py` (experimental, not in
    `DEFAULT_FEATURES`, mirroring how `TREE_MAP_SCREEN` is introduced).
  - Export method + call site in `strictdoc/export/html/html_generator.py`.
  - Server-mode route in `strictdoc/server/routers/main_router.py`.
  - Nav entry in `strictdoc/export/html/templates/_shared/nav.jinja.html`,
    gated by the new feature flag.
- The SVG is generated server-side in Python (custom layered-layout
  algorithm, see HOW), not via a client-side JS layout library. No new
  vendored JS dependency is introduced by this feature.
- SVG markup is written by hand (plain strings/f-strings or a small
  Jinja template), no new Python SVG library dependency (`pyproject.toml`
  currently has none). Only reconsider adding one (e.g. `svgwrite`) if
  hand-written SVG generation turns out to be unwieldy in practice.

### Out of scope for V1

- Interactive dragging/repositioning of document boxes.
- 3D or force-directed rendering (this is unrelated to the existing,
  separately-branched `project_graph` 3D feature — see HOW).
- Automatic edge-crossing minimization within a row (row order follows
  project tree order, not a crossing-minimizing heuristic).

## WHY

Large StrictDoc projects can span many documents connected through
Parent/Child and other relation types (e.g. a top-level requirements
document refined and verified by several downstream documents). There is
currently no single diagram that shows, at a glance, how documents relate to
each other and whether the intended document hierarchy is actually
consistent (e.g. a document that unexpectedly has parents on two different
conceptual levels of the specification). A layered block diagram, analogous
to a classic top-down specification/architecture diagram, makes this
structure and its inconsistencies visible without requiring the reader to
open each document's traceability data individually.

## HOW

### Summary

Add a new StrictDoc export screen, `specification_graph`, that:

1. Walks the already-built `TraceabilityIndex` / graph database to collect,
   for every pair of documents, whether any node-to-node relation crosses
   from one document to the other, and in which direction (child → parent).
2. Runs a custom Python layered-layout algorithm over this document-level
   DAG: assigns each document a row number using the "highway" rule
   described in WHAT, and an in-row column position from project tree
   order.
3. Renders the result as inline SVG (rectangles for documents, arrows for
   cross-document relations, distinct styling only for off-highway "skip"
   arrows) via a Python-side generator — no client-side JS graph-layout
   library.
4. Wires the new screen into export following the existing `tree_map`
   screen pattern (generator/view_object/template, `ProjectFeature` flag,
   `html_generator.py`, `main_router.py`, nav entry).

### Data source

- Cross-document relations are derived from the existing graph database
  (`GraphLinkType.NODE_TO_PARENT_NODES` / `NODE_TO_CHILD_NODES`, see
  `strictdoc/core/traceability_index.py`), using each node's `get_document()`
  to detect when a relation's two endpoints belong to different documents.
  Only the fact and direction of a cross-document relation is needed.
- Row ordering within a "floor" uses
  `traceability_index.document_tree.document_list`, which is already the
  project-tree-order list of documents (confirmed via
  `strictdoc/core/document_tree.py` and its use in
  `strictdoc/core/traceability_index.py:108`).
- No new index/graph-database structures are required; this feature reads
  from the existing traceability index built for every `strictdoc export`
  run.

### Research findings (confirmed before implementation)

- `GraphLinkType.NODE_TO_PARENT_NODES` / `NODE_TO_CHILD_NODES` exist on the
  graph database and are usable per-node; each node's document is obtained
  via `node.get_document()`.
- `traceability_index.document_tree.document_list: List[SDocDocument]` is
  the canonical project-tree-order document list.
- No SVG-generation library is currently a dependency (checked
  `pyproject.toml`); per the decision above, SVG is hand-written for V1.
- No existing fixture project exercises the layout edge cases this feature
  needs (multi-document cross-document relations, a deliberate multi-floor
  conflict, an isolated document). These fixtures do not exist and must be
  authored as part of this feature's own tests — see Implementation order
  below.

### Relationship to the existing 3D `project_graph` feature

A separate, not-yet-merged branch (`mettta/ui_3d_graph`) implements an
unrelated screen also called "project graph": a 3D WebGL force-directed
graph of the full document → section → requirement containment tree plus
all `RELATIONS` edges, rendered client-side with a vendored
`3d-force-graph` (three.js) bundle. This feature is intentionally
independent of that work:

- Different scope: this feature shows documents only (not sections/
  requirements), and only cross-document relations.
- Different rendering: static server-rendered 2D SVG, not a client-side
  WebGL force graph.
- Different name/code path: `specification_graph`, not `project_graph`, to
  avoid confusion between the two screens once both exist.

No code sharing is assumed between the two features. If useful overlap
turns out to exist once both are implemented (e.g. a shared "cross-document
relations" data extraction helper), that is a follow-up refactor, not a V1
requirement here.

### Implementation order

The feature is built bottom-up in self-contained commits/PRs, each passing
`invoke check`, in this order:

1. **Feature skeleton, trivial content.** Wire up the new screen end to
   end with hardcoded/trivial output: `ProjectFeature.SPECIFICATION_GRAPH_SCREEN`
   flag, `generator.py`/`view_object.py`/`index.jinja` producing a fixed
   placeholder SVG (e.g. two hardcoded boxes and an arrow, or just a
   "Specification graph" heading), export call site, server route, nav
   entry. A basic end-to-end test asserts the screen is reachable and
   renders without JS/console errors, mirroring
   `tests/end2end/screens/tree_map`. This proves the plumbing (nav → export
   → screen) before any real algorithm exists.
2. **Cross-document relation extraction.** Implement the graph-database
   walk that, given a `TraceabilityIndex`, returns the set of
   (child document, parent document) edges. Unit-test this in isolation
   against small in-memory/fixture document sets, independent of SVG
   rendering.
3. **Layered layout algorithm.** Implement the row/column assignment
   (including the highway deepest-chain rule) as a pure function from the
   edge set to `{document: (row, column)}`. Unit-test this directly,
   including the edge cases: isolated document, simple chain, multi-floor
   conflict (highway rule), documents sharing a row and their tree order.
   This is the part of the task with real design risk, so it should be
   tested without SVG rendering in the loop.
4. **Real SVG rendering + fixtures.** Wire steps 2–3 into the generator to
   replace the placeholder from step 1, and author the fixture project(s)
   needed to exercise the interesting cases end-to-end (multi-document
   project with cross-document relations, a deliberate multi-floor
   conflict, an isolated document). Add integration and/or end-to-end
   tests against these fixtures per the SDG testing requirement.

### Open questions for implementation phase

- Exact SVG geometry (box sizing/wrapping for long document titles, spacing
  between rows/columns, arrow routing when two documents are far apart
  horizontally) is not decided yet and should be worked out during
  implementation step 4, informed by the fixtures authored at that step.
- Exact visual encoding for "skip" arrows (color vs. dash pattern vs. both)
  is not decided yet.
