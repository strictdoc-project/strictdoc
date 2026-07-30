# TOC + chunked lazy loading — test coverage

Maps each success criterion in `task_1_toc_highlighting.md` to the e2e
test that verifies it. A test only counts as coverage here if it does not
depend on the project's ambient `chunked_documents_threshold` default - each
test sets its own `strictdoc_config.py` (or otherwise forces the fixture
document over its chunking threshold) so it keeps exercising chunking regardless
of what that default is.

Scope: TOC current-section highlighting and TOC/hash navigation
correctness under chunking, per `task_1_toc_highlighting.md`. Two things are
visible on this branch but out of scope here: chunk-preload behavior itself
(`StrictDoc.onInsert` wiring for placeholders inserted after page load,
`lazy_loading` Scenario 6) has its own existing coverage; the
placeholder's visual CSS (`node.css`, the striped/gradient marker for
unloaded chunks) is purely cosmetic and has no test at all - this
project has no screenshot/visual-regression testing infrastructure, so
adding one is out of scope unless visual behavior receives product-level
requirements.

| # | Required behavior | Verified by |
|---|---|---|
| 1 | `intersected` (current-section highlight) tracks anchors added by content-only DOM updates (lazy chunk loading) | `tests/end2end/navigation/toc/toc_highlighting_lazy_chunks` |
| 2 | Clicking a TOC link to an already-loaded target fires a real `hashchange` event and updates the `targeted` highlight | `tests/end2end/navigation/toc/toc_click_navigation_chunked` |
| 3 | CSS `:target` matches a force-loaded (not-yet-in-DOM-at-click-time) target | `tests/end2end/screens/document/lazy_loading`, Scenario 5 |
| 4 | CSS `:target` matches an already-loaded target under chunking | `toc_click_navigation_chunked` |
| 5 | Scroll ends with an already-loaded target on-screen when unloaded chunks sit between the current position and it | `lazy_loading`, Scenario 7 |
| 6 | CSS `:target` and the `targeted` TOC highlight both match a force-loaded target reached via a full top-level page load (stable UID/MID link → `stable_uri_forwarder.js` → server `/UID/{uid_or_mid}` redirect), as opposed to a TOC click or scroll-triggered lazy loading; the target also ends up on-screen | `tests/end2end/stable_url_links/03_web_server_chunked` |
| 7 | `intersected` reflects the actual destination (not an intermediate node passed through while a chunk was loading) after a TOC-click/hash-driven navigation to a force-loaded or gap-crossing target | `lazy_loading`, Scenarios 5 and 7 |
| 8 | Clicking the TOC entry for the section the URL is already on (`location.hash` unchanged - no `hashchange` fires for it) still scrolls back to it | `toc_click_navigation_chunked` |
| 9 | Editing a node whose own chunk is loaded, while the chunks immediately before and after it are still unloaded placeholders, behaves the same as in a non-chunked document (TOC/highlighting update correctly, no error) | `test_edit_in_isolated_middle_chunk_keeps_neighbors_unloaded` |
| 10 | Steady-state TOC highlighting locates the visible section in a 600-anchor document without a geometry scan proportional to all loaded anchors; the destination remains correctly highlighted | `tests/end2end/navigation/toc/toc_highlighting_large_document` |
| 10 | Deleting a node under the same isolated-middle-chunk condition | The premise is obsolete: delete replaces the complete `frame_document_content`, so old neighboring placeholders do not survive. Delete restoration is covered by the viewport-controller tests. |
| 11 | Creating a new node under the same isolated-middle-chunk condition | The premise is obsolete: create replaces the complete `frame_document_content`, so old neighboring placeholders do not survive. Local, distant, and non-chunked create are covered by the viewport-controller tests. |

Row 9 is the surviving isolated-middle-chunk scenario. A node edit uses
`DocumentScreenViewObject.render_updated_nodes_and_toc()`: it updates the whole
TOC and replaces only the affected node frame. The test therefore verifies that
chunk N remains rendered while the unchanged N-1/N+1 placeholders remain lazy.

Create and delete use different response templates: both replace the complete
`frame_document_content`. Chunk boundaries, MID indexes, and placeholder
cursor URLs are regenerated from the current document tree. Consequently, the
old concern that neighboring placeholders retain stale pre-operation cursors
does not apply to these actions. Their viewport positioning and subsequent
target-chunk loading are covered in
`tests/end2end/screens/document/lazy_loading_scroll_preservation`.

`loadChunkThenScroll()` also guards against a stale/moved TOC anchor
(a target that never actually appears once its chunk loads) bouncing
the hash forever: `refreshTargetElement()` is only called once the
target is confirmed present. This is a defensive fix for a rare,
hard-to-construct edge case (a renamed/relocated anchor whose TOC entry
still points at an old id) and is not separately covered by an e2e
test.

Assertion support: `assert_node_in_viewport_by_anchor` (`screen_document.py`)
checks that a target actually landed on-screen (`getBoundingClientRect()`
against the scroll container's bounds), rather than merely being present
somewhere in the DOM or text - used everywhere rows 5-6 need it, since
DOM presence and `:target` don't by themselves prove the scroll landed.

## Writing tests that exercise an unloaded-chunk scenario

A test asserting "this chunk is still unloaded" is only meaningful if
the chunk is actually large enough to stay unloaded:
`toc_chunk_navigation.js` preloads any placeholder within 800px of the
viewport (`PRELOAD_MARGIN`), so a chunk whose real or estimated height
does not clear that margin on both sides will load regardless of
distance in chunk-index terms.

- Size fixtures so each chunk's content comfortably exceeds the
  viewport height plus 800px on each side - `chunked_documents_threshold
  = 10` on a several-dozen-node document (as in `lazy_loading` and
  `stable_url_links/03_web_server_chunked`) is a known-good ratio.
- A target that lives in chunk 0 is exempt from this concern: chunk 0
  is always rendered inline, never subject to lazy-load/preload timing.
- Assert the intended DOM state directly (e.g., a chunk's content is
  absent, or a specific unrelated chunk stays unloaded after the
  scenario) rather than relying on the fixture's sizing alone to make
  it true.

## Content viewport restoration

The content viewport restoration feature is defined in
`task_2_content_viewport_restoration.md`.

Direct coverage lives in:
`tests/end2end/screens/document/lazy_loading_scroll_preservation`.

The test fixture contains two documents:

- `document.sdoc`: 35 requirements with `chunked_documents_threshold = 10`,
  so the document renders as four chunks;
- `control.sdoc`: 9 requirements, below the threshold, so it stays
  non-chunked.

The chunked tests first load chunk 1 and chunk 2 through normal scrolling.
Chunk 1 is then loaded above the viewport. After a full document content
replacement, that chunk becomes a placeholder again. This creates the geometry
change that the restoration script must handle.

| # | Required behavior | Verified by |
|---|---|---|
| 1 | Creating a node from a visible create form restores to the created node near the form's previous viewport position | `test_create_scrolls_to_new_node` |
| 2 | Deleting a visible node keeps the top visible surviving node at the same viewport-relative position | `test_delete_preserves_top_visible_node_position` |
| 3 | Deleting the last node falls back to the previous surviving node at the document end | `test_delete_last_node_falls_back_to_end_of_document` |
| 4 | TOC drag-and-drop move keeps the top visible content node at the same viewport-relative position | `test_move_preserves_top_visible_node_position` |
| 5 | Grammar edit keeps the current content viewport stable after the document content frame is replaced | `test_grammar_edit_preserves_top_visible_node_position` |
| 6 | Node-local edit does not collapse an isolated loaded middle chunk or load its neighboring placeholders | `test_edit_in_isolated_middle_chunk_keeps_neighbors_unloaded` |
| 7 | Local create in chunk 0 restores to the created node where the form was | `test_create_locally_does_not_jump` |
| 8 | Local delete in chunk 0 keeps the visible top node at the same viewport-relative position | `test_delete_locally_does_not_jump` |
| 9 | Non-chunked create keeps the existing create behavior while the restoration script is loaded | `test_non_chunked_create_unaffected` |
| 10 | Non-chunked delete keeps the existing viewport behavior while the restoration script is loaded | `test_non_chunked_delete_unaffected` |
| 11 | Non-chunked move keeps the existing viewport behavior while the restoration script is loaded | `test_non_chunked_move_unaffected` |
| 12 | Non-chunked grammar edit keeps the existing viewport behavior while the restoration script is loaded | `test_non_chunked_grammar_edit_unaffected` |

For non-chunked documents, the test checks that the restoration script does not
change ordinary full-content update behavior.
