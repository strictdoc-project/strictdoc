# TOC current-section highlighting: track anchors added by content-only DOM updates

## WHAT

Extend the TOC "current section" highlighting mechanism
(`strictdoc/export/html/_static/toc_highlighting.js`) so that it
correctly tracks document nodes whose anchors are inserted into the
content area after the initial page load, through any DOM update that
does not also update the TOC frame (`frame-toc`).

Success criteria:

- When a document node that was not present in the DOM at initial page
  load later appears in the content area and is scrolled into view,
  its corresponding TOC entry is marked as the current section, with
  the same behavior as for a node that was present at initial load.
- No regression to existing highlighting behavior: node creation,
  update, deletion, and folder expand/collapse continue to update the
  current-section highlight exactly as today.
- The fix must not depend on the specific mechanism, naming
  convention, or markup used by any given content-loading feature
  (e.g., must not assume a particular turbo-frame id pattern or a
  particular JS event). It must generalize to "content appeared in the
  DOM," regardless of cause.
- The fix relies on the following invariant, which must continue to
  hold: the TOC (`frame-toc`) is always rendered in full on initial
  page load, listing every document node, regardless of whether that
  node's content is present in the DOM at that time. Any future
  content-loading feature must not turn the TOC itself into a
  partially or lazily rendered structure, or this mechanism breaks.

## WHY

`toc_highlighting.js` determines which section is "current" using an
`IntersectionObserver` over content anchors (`sdoc-anchor` elements).
The set of anchors under observation is (re)built by
`processAnchorList()`, which only runs in two situations: once on the
page's `load` event, and whenever the TOC frame's own DOM mutates
(tracked via a `MutationObserver` on `frame-toc`).

This is sufficient today because, on the server side, every operation
that changes document content (creating, updating, or deleting a node)
always re-renders and streams a full TOC update to `frame-toc` in the
same turbo-stream response as the content change
(`DocumentScreenViewObject.render_updated_nodes_and_toc()`: the TOC
partial is always re-rendered and pushed to `frame-toc` whenever
`node_updated` is true, alongside the turbo-stream updates for the
affected node content). As a result, content mutation and TOC mutation
are always coupled in the current system, and observing `frame-toc` is
enough to catch every case where the set of visible anchors changes.

An upcoming feature renders large documents in lazily-loaded chunks:
additional document nodes are fetched and inserted into the content
area via independent turbo-frame requests, well after the initial page
load. The TOC is rendered in full up front and is not re-streamed when
a chunk loads — this is the first scenario where document content
changes without any corresponding mutation of `frame-toc`. The current
highlighting mechanism has no path that reacts to this, so once a user
scrolls into a node that was not present in the DOM at initial load,
the current-section highlight stops updating and remains stuck on the
last section that was tracked.

This task addresses that gap ahead of the lazy-chunk-loading feature
landing, so that TOC highlighting is already correct once it does,
without requiring changes to the incoming feature itself.

## HOW

Add a second `MutationObserver`, alongside the existing one on
`frame-toc`, targeting the stable content container
(`[js-toc_highlighting-content_root]`), configured for
`childList: true, subtree: true`. On a triggering mutation
(coalesced via `requestAnimationFrame`, matching the existing
debouncing pattern used elsewhere in the file), re-run
`processAnchorList()` for the content frame and recompute currently
visible sections, without resetting the TOC link mappings
(`processLinkList()` / `resetState()`).

This is safe without a full state reset because `processLinkList()`
already captures a `link` reference for every node's anchor id from
the initial full TOC scan, including nodes whose content has not yet
appeared in the DOM. When `processAnchorList()` later discovers a new
anchor id, it merges the newly found anchor element into the existing
entry for that id, which already carries the correct TOC link.

Given the coupling described above, this change is a no-op under all
current (non-lazy-loading) content-mutation paths, since those already
trigger the existing `frame-toc` observer. It only becomes active once
a mechanism exists that inserts content without mutating `frame-toc`
— which is exactly the case this task is meant to prepare for.

Open implementation consideration: `processAnchorList()` performs a
full re-scan and signature computation over all anchors currently in
the DOM on each run. Under frequent content-only mutations (e.g.,
scrolling through many lazily-loaded chunks in quick succession), the
cost of this re-scan grows with the total number of anchors already
present. Start with the full re-scan approach; if measurement shows
this to be a performance concern on large documents, consider
processing `MutationRecord.addedNodes`/`removedNodes` directly for an
incremental update instead of a full re-scan.
