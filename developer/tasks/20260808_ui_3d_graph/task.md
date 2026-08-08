# 3D project graph screen

Add a new StrictDoc screen, "Project graph", that renders the project's
document tree as an interactive 3D force-directed graph, using
[3d-force-graph](https://github.com/vasturiano/3d-force-graph).

## WHAT

### Scope

- Graph nodes: documents, sections, and requirement-like nodes
  (`SDocNode` with a reserved title/UID), across all documents in the project
  tree. Plain `TEXT` nodes are excluded.
- Graph edges: structural containment only — document → section → node,
  following the same parent/child hierarchy `tree_map` uses
  (`SDocDocumentIterator`). This is a single-root DAG per document.
- Each node is labeled with its title (and UID, when present).
- The graph is navigable with the controls 3d-force-graph provides out of the
  box (orbit/rotate, zoom, pan). No custom interaction (click-to-open,
  click-to-preview, filters) is implemented.
- Rendered as its own screen (`project_graph.html`), gated by the
  `PROJECT_GRAPH_SCREEN` project feature, reachable from the project tree nav.
- Works in both static HTML export and server mode.
- The 3d-force-graph library (a self-contained UMD bundle that already
  includes Three.js and its own dependencies) is vendored under the
  feature's `assets/` directory, not loaded from a CDN, so static export
  stays fully offline — consistent with `mermaid`, `mathjax`, `nestor`.

### Out of scope (not implemented)

- Rendering a single document's tree in isolation (project-wide graph only).
- Turning `RELATIONS` (Parent/Child/Refines/etc.) into additional graph
  edges.
- Click-to-preview a node's content.
- Click-to-open a node in the document editor/viewer.
- Filtering or grouping nodes (by document, by requirement type, by
  coverage, etc.).
- Any persistence of camera position/layout between sessions.

### Testing

No automated test coverage for this screen yet.

An end-to-end test (mirroring the `tree_map` screen's Selenium-based tests)
was written and then removed after investigation showed it cannot pass in
this project's e2e test environment: 3d-force-graph requires a WebGL
context (via Three.js), and the Chrome instance SeleniumBase launches for
`invoke test-end2end` has no WebGL context available — Chrome reports
`"disabled by enterprise policy or commandline switch"` and
`ForceGraph3D()` throws on init. This reproduces identically in both
`--headless` and `--headed` runs, so it is not a headless-specific
limitation — it is how SeleniumBase's Chrome is launched/configured in this
environment. Manually opening the exported `project_graph.html` in a
regular browser renders and behaves correctly.

Fixing this would mean passing software-WebGL Chrome flags (e.g.
`--use-gl=angle --use-angle=swiftshader`) into the shared e2e Chrome launch
config (`tasks.py`), which is shared e2e test infrastructure, not local to
this feature, and needs a deliberate decision before touching it. Until
that's resolved, this screen's correctness is verified manually
(`strictdoc export` producing the expected `project_graph.html`, checked in
a real browser) rather than by an automated test — a deliberate,
documented exception, not an oversight.

## WHY

StrictDoc already offers 2D visualizations of the document tree
(`tree_map`, table/traceability screens) but no way to explore the
project's structure spatially. A 3D force-directed graph gives a different,
exploratory view of how documents, sections, and requirements relate to
each other — useful for getting an overview of a large or unfamiliar
project, and, in future increments, for visually inspecting traceability
relations that are otherwise only visible per-document or in the
traceability matrix.

This first iteration establishes the new screen end-to-end (data export,
vendored library, screen wiring, feature flag) with the simplest possible
graph (structural containment) so the plumbing is validated before layering
richer edge types and interactivity on top.

## HOW

### Summary

The `strictdoc/features/project_graph/` feature mirrors the `tree_map`
feature's architecture (`strictdoc/features/tree_map/`):

- `generator.py` (`ProjectGraphGenerator`) walks
  `traceability_index.document_tree` the same way `TreeMapGenerator` does
  (via `SDocDocumentIterator`), and builds a graph-data structure
  (`{"nodes": [...], "links": [...]}`, per 3d-force-graph's input format).
- `view_object.py` (`ProjectGraphViewObject`), analogous to
  `TreeMapViewObject`: serializes the graph data to JSON (escaping `</` so
  it can't break out of its `<script>` tag) and exposes it, and the
  vendored-JS static URL, to the Jinja template.
- `templates/features/project_graph/index.jinja` extends `base.jinja.html`,
  following `tree_map/index.jinja`'s structure: a `<script src="...">` tag
  loading the vendored 3d-force-graph bundle, a
  `<script type="application/json">` tag holding the graph data, a
  `<div id="project_graph-container">`, and a small inline script that
  parses the JSON and calls `ForceGraph3D()` on the container, coloring
  nodes by type (document/section/requirement).
- Vendored asset:
  `strictdoc/features/project_graph/assets/project_graph/3d-force-graph.min.js`
  (+ `LICENSE-3D-FORCE-GRAPH`, MIT). This is 3d-force-graph's own prebuilt
  UMD bundle (currently v1.80.0, ~1.3MB minified / ~340KB gzipped) — it
  already inlines Three.js and all its other dependencies
  (`three-forcegraph`, `three-render-objects`, `kapsule`, `accessor-fn`),
  so no separate Three.js file and no Node/npm build step were needed.
  Loaded the same way `mermaid.min.js` is: a plain `<script src=...>` tag
  pointing at a `render_static_url()`-resolved path.
- `strictdoc.core.project_config.ProjectFeature.PROJECT_GRAPH_SCREEN`
  (experimental features section), with an `is_activated_project_graph()`
  accessor — not part of `ProjectConfigDefault.DEFAULT_FEATURES`, so it is
  opt-in like `tree_map` and the other experimental screens.
- Wiring:
  - `strictdoc/core/environment.py`: `project_graph/templates` and
    `project_graph/assets` added to `HTML_TEMPLATE_DIRS` /
    `HTML_STATIC_DIRS`.
  - `strictdoc/export/html/html_generator.py`: `export_project_graph_screen()`
    method + call site guarded by `is_activated_project_graph()`, following
    `export_tree_map_screen()`.
  - `strictdoc/server/routers/main_router.py`: route for
    `project_graph.html` in server mode, following the `tree_map.html`
    branch.
  - `strictdoc/export/html/templates/_shared/nav.jinja.html`: nav entry
    (icon: letter "G", same style as tree_map's "M") guarded by
    `is_activated_project_graph()`.
  - `strictdoc/commands/new_command.py`: `PROJECT_GRAPH_SCREEN` added
    (commented out) to the scaffolded project config's experimental
    features list, alongside `TREE_MAP_SCREEN`.

### Data shape (3d-force-graph input)

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

`MID` (`reserved_mid`) is reused as the graph node id, matching how
`tree_map` already keys its rows.

### Verification performed

- `strictdoc export` on a small hand-written project (one document, one
  section, one requirement) with `PROJECT_GRAPH_SCREEN` enabled produces a
  `project_graph.html` containing the expected node/link JSON
  (document → section → requirement, 2 links) and the vendored JS
  reference under `_static/project_graph/`.
- Same check in server mode (route returns the equivalent page).
- The exported page opened in a real (non-Selenium) browser: graph renders
  and is orbit/zoom/pan-navigable, matching the intended behavior.
- `invoke lint-ruff` and `invoke lint-mypy` pass on all changed/added
  Python files.

## Next increments (not implemented, for future tasks)

1. Resolve the WebGL/Selenium-Chrome environment issue (see Testing above)
   and add the automated end-to-end test coverage this feature currently
   lacks.
2. Add `RELATIONS`-derived edges (Parent/Child/Refines/etc.) as a second,
   visually distinct edge type layered on top of the containment DAG.
3. Click-to-preview a node's content (e.g., a hover/click side panel).
4. Click-to-open a node in the document editor/viewer (reusing
   `LinkRenderer.render_node_link`, as `tree_map` already does for its
   "Open in document" links).
5. Filters/grouping (by document, node type, coverage, free text).
6. Single-document graph view (in addition to the project-wide graph).
7. Consider an SRS requirement in
   `docs/strictdoc_21_l2_high_level_requirements.sdoc` for this screen,
   as exists for `tree_map` (`SDOC-SRS-157`).
8. Performance ceiling is untested against large projects — if the graph
   becomes sluggish on big document trees, revisit (e.g., a node-count
   warning).
