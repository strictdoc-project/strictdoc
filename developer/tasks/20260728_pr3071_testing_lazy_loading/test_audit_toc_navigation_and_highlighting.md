# TOC navigation and highlighting: test audit

Maps each success criterion in
`task_1_toc_navigation_and_highlighting.md` to the e2e test that verifies it.
A test only counts as coverage here if it does not depend on the project's
ambient `chunked_documents_threshold` default - each test sets its own
`strictdoc_config.py` (or otherwise forces the fixture document over its
chunking threshold) so it keeps exercising chunking regardless of what that
default is.

Scope: TOC current-section highlighting and TOC/hash navigation
correctness under chunking, per
`task_1_toc_navigation_and_highlighting.md`. Two things are
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
| 11 | Inserting an equal-size lazy chunk registers only its new anchors, independently of the number of anchors loaded earlier; replacing an existing anchor after Cancel reconnects `IntersectionObserver` from the detached DOM element to its same-ID replacement | `tests/end2end/navigation/toc/toc_highlighting_chunk_insertion` |

Row 9 is the relevant isolated-middle-chunk scenario. A node edit uses
`DocumentScreenViewObject.render_updated_nodes_and_toc()`: it updates the whole
TOC and replaces only the affected node frame. The test therefore verifies that
chunk N remains rendered while the unchanged N-1/N+1 placeholders remain lazy.

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
