# 3D project graph screen

Add a new StrictDoc screen, that renders the project's document tree
as an interactive 3D force-directed graph.

## WHAT

Add a new StrictDoc screen, "Project graph", that renders the project's document
tree as an interactive 3D force-directed graph, using
[3d-force-graph](https://github.com/vasturiano/3d-force-graph).

### V1 scope (this task)

- Graph nodes: documents, sections, and requirement-like nodes
  (`SDocNode` with a reserved title/UID), across all documents in the project
  tree. Plain `TEXT` nodes are excluded.
- Graph edges: structural containment only — document → section → node,
  following the same parent/child hierarchy used by `tree_map`
  (`SDocDocumentIterator`). This is the first-level DAG.
- Each node is labeled with its title (and UID, when present).
- The graph is navigable with the controls 3d-force-graph provides out of the
  box (orbit/rotate, zoom, pan). No custom interaction is required yet.
- Rendered as its own screen (`project_graph.html`), gated by a new
  `ProjectFeature` flag, reachable from the project tree nav — mirroring how
  `tree_map` is wired (see HOW).
- Works in both static HTML export and server mode.
- The 3d-force-graph library (and its Three.js dependency) is vendored under
  the feature's `assets/` directory, not loaded from a CDN, so static export
  stays fully offline — consistent with `mermaid`, `mathjax`, `nestor`.

### Explicitly out of scope for V1

- Rendering a single document's tree in isolation (project-wide graph only,
  for now).
- Turning `RELATIONS` (Parent/Child/Refines/etc.) into additional graph
  edges — this is the planned next increment (see "Next increments" below).
- Click-to-preview a node's content.
- Click-to-open a node in the document editor/viewer.
- Filtering or grouping nodes (by document, by requirement type, by coverage,
  etc.).
- Any persistence of camera position/layout between sessions.

### Success criteria

- With the new feature flag enabled, exporting a project produces
  `project_graph.html` that renders all documents/sections/requirement nodes
  of the project as a 3D graph with containment edges, matching the counts
  produced by `SDocDocumentIterator` (same traversal `tree_map` uses).
- The screen works identically when StrictDoc runs as a server.
- The screen degrades sensibly (does not crash) on an empty project or a
  project with a single document.
- At least one integration/end-to-end test exercises export of the new screen
  (per SDG: every new feature needs at least one new integration or
  end-to-end test).

## WHY

StrictDoc currently offers 2D visualizations of the document tree
(`tree_map`, table/traceability screens) but no way to explore the
project's structure and its cross-references spatially. A 3D force-directed
graph gives a different, exploratory view of how documents, sections, and
requirements relate to each other — useful for getting an overview of a
large or unfamiliar project, and, in later increments, for visually
inspecting traceability relations that are otherwise only visible per-document
or in the traceability matrix.

This task establishes the new screen end-to-end (data export, vendored
library, screen wiring, feature flag) with the simplest possible graph
(structural containment) so the plumbing is validated before layering
richer edge types and interactivity on top.

## HOW

### Summary

Mirror the `tree_map` feature's architecture (`strictdoc/features/tree_map/`)
for a new `strictdoc/features/project_graph/` feature:

- A generator (`generator.py`) that walks `traceability_index.document_tree`
  the same way `TreeMapGenerator` does (via `SDocDocumentIterator`), and
  builds a graph-data JSON structure (`{nodes: [...], links: [...]}`, per
  3d-force-graph's input format) instead of a Plotly dataframe.
- A `view_object.py` (`ProjectGraphViewObject`) analogous to
  `TreeMapViewObject`, exposing the serialized graph JSON and the vendored JS
  to the Jinja template.
- A Jinja template (`templates/features/project_graph/index.jinja`) extending
  `base.jinja.html`, following `tree_map/index.jinja`'s structure: a
  `<script>` block that inlines the vendored 3d-force-graph JS, and a
  `<div id="graph-container">` where a small inline script instantiates
  `ForceGraph3D()` with the exported JSON.
- Vendored assets under `strictdoc/features/project_graph/assets/` (JS
  bundle(s) for `3d-force-graph` + `three`), loaded the same way
  `mermaid`/`nestor`/`mathjax` vendor and inline their JS.
- A new `ProjectFeature.PROJECT_GRAPH_SCREEN` flag (experimental features
  section of the enum in `strictdoc/core/project_config.py`), with an
  `is_activated_project_graph()` accessor.
- Wiring:
  - `strictdoc/export/html/html_generator.py`: `export_project_graph_screen()`
    method + call site guarded by `is_activated_project_graph()`, following
    `export_tree_map_screen()`.
  - `strictdoc/server/routers/main_router.py`: route for
    `project_graph.html` in server mode, following the `tree_map.html`
    branch.
  - `strictdoc/export/html/templates/_shared/nav.jinja.html`: new nav entry
    guarded by `is_activated_project_graph()`, following the `tree_map` nav
    entry.
- The new flag is added to the experimental features list, not
  `ProjectConfigDefault.DEFAULT_FEATURES`, so it is opt-in like `tree_map`
  and other experimental screens.

### Data shape (for 3d-force-graph)

```json
{
  "nodes": [
    {"id": "<MID>", "name": "<title or 'title (UID)'>", "type": "document|section|requirement"}
  ],
  "links": [
    {"source": "<parent MID>", "target": "<child MID>"}
  ]
}
```

`MID` is reused as the graph node id, matching how `tree_map` already keys
rows by `reserved_mid`.

### Next increments (not part of this task, tracked here for continuity)

1. Add `RELATIONS`-derived edges (Parent/Child/Refines/etc.) as a second,
   visually distinct edge type layered on top of the containment DAG —
   per the user's clarification, "parent/child relations become
   [additional] nodes/edges" on top of the base structural graph, and
   `RELATIONS` fields are further, separate links to add after that.
2. Click-to-preview a node's content (e.g., a hover/click side panel).
3. Click-to-open a node in the document editor/viewer (reusing
   `LinkRenderer.render_node_link`, as `tree_map` already does for its
   "Open in document" links).
4. Filters/grouping (by document, node type, coverage, free text).
5. Single-document graph view (in addition to the project-wide graph).

## Open questions / to research before or during implementation

- **3d-force-graph packaging**: the library ships as an npm package built on
  Three.js (WebGL). Need to determine the smallest viable vendored bundle
  (UMD/IIFE build vs. ES module) that can be inlined the way `mermaid.min.js`
  etc. are, without introducing a Node/npm build step into StrictDoc's
  Python-only build pipeline. Check whether a prebuilt UMD bundle is
  published (e.g., via a CDN dist file we can vendor a copy of) or whether we
  need `esbuild`/similar once, offline, to produce one.
- **Bundle size / license**: 3d-force-graph + three.js is significantly
  larger than mermaid/plotly-lite assets already vendored. Confirm license
  compatibility (MIT, should be fine) and check the impact on
  `output_html_root` size and export time for large projects.
- **Performance ceiling**: unclear how many nodes/edges 3d-force-graph can
  render smoothly (WebGL, but still). Need to test against StrictDoc's own
  docs (SDG) and a large sample project to see if V1 needs any node-count
  safeguard (e.g., a warning, or excluding the graph screen above N nodes)
  before this becomes a real concern.
- **SDG requirement**: per SDG conventions (see `SDOC-SRS-157` for
  `tree_map`), a new feature normally gets a corresponding SRS requirement
  documenting expected behavior. Confirm whether/when to add this to
  `docs/strictdoc_21_l2_high_level_requirements.sdoc`.
- **Static vs. server node count parity**: confirm the JSON payload is
  generated once and reused identically between static export and server
  mode (same as `tree_map`'s `TreeMapGenerator.export` being called from both
  `html_generator.py` and `main_router.py`).
