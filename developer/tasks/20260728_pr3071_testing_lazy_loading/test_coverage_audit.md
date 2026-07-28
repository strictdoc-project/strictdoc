# TOC + chunked lazy loading — test coverage

Maps each success criterion in `task.md` to the e2e test that verifies
it. A test only counts as coverage here if it does not depend on the
project's ambient `chunked_documents_threshold` default - each test
sets its own `strictdoc_config.py` (or otherwise forces the fixture
document over its chunking threshold) so it keeps exercising chunking
regardless of what that default is.

Scope: TOC current-section highlighting and TOC/hash navigation
correctness under chunking, per `task.md`. Two things are visible on
this branch but out of scope here: chunk-preload behavior itself
(`StrictDoc.onInsert` wiring for placeholders inserted after page load,
`lazy_loading` Scenario 6) has its own existing coverage; the
placeholder's visual CSS (`node.css`, the striped/gradient marker for
unloaded chunks) is purely cosmetic and has no test at all - this
project has no screenshot/visual-regression testing infrastructure, so
adding one is a disproportionate response unless the visual result
turns out to matter for a reason beyond appearance.

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
| 9 | Editing a node whose own chunk is loaded, while the chunks immediately before and after it are still unloaded placeholders, behaves the same as in a non-chunked document (TOC/highlighting update correctly, no error) | Not yet covered |
| 10 | Deleting a node under the same isolated-middle-chunk condition | Not yet covered |
| 11 | Creating a new node under the same isolated-middle-chunk condition | Not yet covered |

Rows 9-11 target the same scenario: the edited/created/deleted node's
chunk (call it chunk N) is already loaded, chunk N-1 and chunk N+1 are
not. `DocumentScreenViewObject.render_updated_nodes_and_toc()` always
re-renders the *whole* TOC and streams a `replace` for the affected
node(s) - both computed from the document's current node list at
request time. Chunk N-1/N+1's placeholders, if already present in the
DOM, keep the `src` URL (cursor MID + count) that was computed when
the page was first rendered; that URL is never refreshed by an edit
happening elsewhere. Whether create/delete (which change the total
node count and can shift where chunk boundaries fall) leaves those
already-rendered placeholders pointing at a `from_node` cursor that
still resolves to a sensible, non-overlapping, non-duplicated window
once they do eventually load is the open question to check first, for
rows 10 and 11 in particular.

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
