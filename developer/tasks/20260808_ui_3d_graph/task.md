# 3D project graph screen

Add a new StrictDoc screen, "Project graph", that renders the project's
document tree as an interactive 3D force-directed graph, using
[3d-force-graph](https://github.com/vasturiano/3d-force-graph).

## WHAT

### Scope

- Graph nodes: documents, sections, requirement-like nodes (`SDocNode` with
  a reserved title/UID), and source/test files that requirements have
  traceability links to. Plain `TEXT` nodes are excluded.
- Graph edges, three kinds, color- and width-coded (see legend on the
  screen):
  - `containment` — structural document → section → node hierarchy,
    following the same traversal `tree_map` uses (`SDocDocumentIterator`).
    Gray, width 1.
  - `relation` — one edge per resolved `RELATIONS: TYPE: Parent` link
    between requirements (`traceability_index.get_parent_requirements()`),
    i.e. the same parent/child requirement graph the traceability matrix
    is built from. Magenta, width 2.
  - `file` — one edge per requirement → linked source/test file, from
    `traceability_index.get_file_traceability_index()` (the same data
    `tree_map`/`source_coverage` read). Cyan, width 1.
- Each node is labeled with its title (and UID, when present); file nodes
  are labeled with their relative path and colored differently for test
  files (path containing `tests/`) vs. other source files.
- A view switcher (top-left dropdown) lets the user swap the layout live,
  without a page reload:
  - `force` — plain force-directed (no `dagMode`).
  - `td` / `lr` / `radialout` — 3d-force-graph's built-in `dagMode` tree
    layouts (top-down is the default view on load).
  - `byDocument` — a custom layout, not a `dagMode` preset: every node is
    tagged with a `docIndex` (`generator.py`) identifying which document
    it belongs to; each document and its nodes are pinned to their own
    horizontal plane via a fixed `z` (`docIndex * PLANE_SPACING`), planes
    stacked one above another so all document-center nodes share the same
    `x`/`y` and differ only in `z`. The document node itself is pulled to
    its plane's center (`x=0, y=0`); its other nodes keep `z` pinned to
    the same plane but are left free on `x`/`y`, so the normal charge/link
    forces settle them into a radial arrangement around the document
    center. A file node referenced from multiple documents is pinned to
    the plane of whichever document happened to reference it first — an
    approximation, not exact.
    - On this vendored 3d-force-graph build, `x` can be hard-pinned via
      `node.fx`, but `node.fy` is silently cleared back to `undefined`
      every tick — a residual effect of `dagMode`'s "td"/"bu" modes owning
      the y axis, which persists even after `dagMode(null)`. `y` is
      therefore pulled toward 0 via a custom `d3Force` that nudges
      velocity (`vy`) instead of fixing position.
    - Dragging a node pins its `fx`/`fy`/`fz` to the drop point and they
      stay there — which would otherwise let a dragged document ball end
      up permanently off-center, or a dragged child node end up on the
      wrong plane. An `onNodeDragEnd` handler snaps `z` back to the
      node's document plane for any node, and additionally snaps the
      document node itself back to `(0, 0)` — so document balls always
      return to the same fixed point after being dragged, and other
      nodes can move freely within their plane but never leave it.
- The graph is otherwise navigable with the controls 3d-force-graph
  provides out of the box (orbit/rotate, zoom, pan). No click interaction
  (click-to-open, click-to-preview, filters) is implemented.
- Rendered as its own screen (`project_graph.html`), gated by the
  `PROJECT_GRAPH_SCREEN` project feature, reachable from the project tree nav.
- Works in both static HTML export and server mode.
- The 3d-force-graph library (a self-contained UMD bundle that already
  includes Three.js and its own dependencies) is vendored under the
  feature's `assets/` directory, not loaded from a CDN, so static export
  stays fully offline — consistent with `mermaid`, `mathjax`, `nestor`.

### Out of scope (not implemented)

- Rendering a single document's tree in isolation (project-wide graph only).
- `RELATIONS` types other than `Parent` (e.g. role-qualified relations,
  `Refines`, etc.) — only the plain parent/child requirement graph is
  rendered.
- Click-to-preview a node's content.
- Click-to-open a node in the document editor/viewer.
- Filtering or grouping nodes (by document, by requirement type, by
  coverage, etc.).
- Any persistence of camera position/layout/selected view between sessions.

### Testing

No automated test coverage for this screen. This is a deliberate,
documented exception (see SDG's "one test per feature" rule): 3d-force-graph
requires a WebGL context (via Three.js), and this project's
SeleniumBase-driven Chrome (`invoke test-end2end`, both `--headless` and
`--headed`) has no WebGL context available — Chrome reports `"disabled by
enterprise policy or commandline switch"` and `ForceGraph3D()` throws on
init. This is not headless-specific; it is how SeleniumBase's Chrome is
launched/configured in this environment. The screen renders and behaves
correctly in a regular (non-Selenium) browser.

Resolving this requires passing software-WebGL Chrome flags (e.g.
`--use-gl=angle --use-angle=swiftshader`) into the shared e2e Chrome launch
config (`tasks.py`) — shared e2e test infrastructure, not local to this
feature, so it needs a deliberate decision before touching it (see Next
increments). Until then, this screen is verified manually: export a project
with `PROJECT_GRAPH_SCREEN` enabled and check `project_graph.html` in a
real browser.

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
  `<div id="project_graph-container">`, a view-switcher `<select>` plus a
  color legend, and a small inline script that parses the JSON and calls
  `ForceGraph3D()` on the container, coloring nodes by type
  (document/section/requirement/source_file/test_file), coloring/widening
  links by `kind` (containment/relation/file — via `.linkColor()` +
  `.linkWidth()`; `.linkLineDash()` is not available on this vendored
  3d-force-graph build), and applying either `.dagMode()` or the custom
  `byDocument` fixed-coordinate layout (see Scope) whenever the
  view-switcher selection changes, followed by `.d3ReheatSimulation()` so
  the new layout actually takes effect.
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
    {"id": "<MID or file path>", "name": "<title/UID or file path>", "type": "document|section|requirement|source_file|test_file", "docIndex": 0}
  ],
  "links": [
    {"source": "<MID>", "target": "<MID or file path>", "kind": "containment|relation|file"}
  ]
}
```

`MID` (`reserved_mid`) is reused as the graph node id for document/section/
requirement nodes, matching how `tree_map` already keys its rows. File
nodes are keyed by their relative path instead (there is no MID for a
source file), deduplicated across requirements via a `seen_file_paths` set
so a file referenced by multiple requirements is still a single node.
`relation` links are produced by walking
`traceability_index.get_parent_requirements(node)` for every node with a
`reserved_uid`, resolving `RELATIONS: TYPE: Parent` references to their
target node's MID — the same resolved graph the traceability matrix reads
from, not a re-parse of the `RELATIONS` field. `file` links come from
`traceability_index.get_file_traceability_index().get_requirement_file_links(node)`.
`docIndex` is the 0-based position of the node's document among the
project's non-included documents (assigned while iterating
`document_tree.document_list` in `generator.py`); it is only consumed by
the `byDocument` view.

### Manual verification checklist

In the absence of automated coverage (see Testing), changes to this screen
should be checked against:

- `strictdoc export` on a project with `PROJECT_GRAPH_SCREEN` enabled
  produces a `project_graph.html` whose embedded node/link JSON matches
  the project's actual document → section → requirement structure, plus
  the vendored JS reference under `_static/project_graph/`.
- The same holds in server mode (the route returns the equivalent page).
- The exported page, opened in a real (non-Selenium) browser: the graph
  renders and is orbit/zoom/pan-navigable; each view-switcher option
  (`force`/`td`/`lr`/`radialout`/`byDocument`) produces a distinct,
  sane layout.
- A project with a `RELATIONS: TYPE: Parent` link between two
  requirements produces the corresponding `"kind": "relation"` link in
  the exported JSON, alongside `"kind": "containment"` links.
- A project with a `@relation(REQ-1, scope=file)` marker in a source file
  (with `REQUIREMENT_TO_SOURCE_TRACEABILITY` enabled) produces a
  `source_file` node for that file and a `"kind": "file"` link from the
  requirement to it.
- `invoke lint-ruff` and `invoke lint-mypy` pass.

## Next increments (not implemented, for future tasks)

1. Resolve the WebGL/Selenium-Chrome environment issue (see Testing above)
   and add the automated end-to-end test coverage this feature currently
   lacks.
2. Broaden `relation` edges beyond plain `Parent` links (role-qualified
   relations, `Refines`, etc.), and/or let the legend's `relation` category
   distinguish between relation subtypes.
3. Click-to-preview a node's content (e.g., a hover/click side panel).
4. Click-to-open a node in the document editor/viewer (reusing
   `LinkRenderer.render_node_link`, as `tree_map` already does for its
   "Open in document" links).
5. Filters/grouping (by document, node type, coverage, free text; e.g. a
   toggle to hide `relation`/`file` edges and see just the plain
   containment tree).
6. Single-document graph view (in addition to the project-wide graph).
7. Consider an SRS requirement in
   `docs/strictdoc_21_l2_high_level_requirements.sdoc` for this screen,
   as exists for `tree_map` (`SDOC-SRS-157`).
8. Performance ceiling is untested against large projects — if the graph
   becomes sluggish on big document trees, revisit (e.g., a node-count
   warning). Adding file nodes makes this more relevant since large
   projects with heavy source traceability could add many extra nodes.
