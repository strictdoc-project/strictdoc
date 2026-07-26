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
- Fixes, as a side effect, a pre-existing and independent case of the
  same underlying gap: canceling a node edit (Cancel, without saving)
  re-inserts the node's read-view anchor without updating the TOC
  frame, so the highlighting for that node went stale after any Cancel
  before this task.
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

The same class of gap already exists today, independently of chunking:
canceling a node edit (`cancel_edit_requirement`) calls
`render_updated_nodes_and_toc([requirement], node_updated=False)` -
with `node_updated=False`, the `frame-toc` update is skipped, so only
the node's read-view content (with a freshly re-inserted anchor) is
streamed back. This is the same "content changed, TOC frame did not"
shape as the chunking case, just triggered by a different, already-
shipped feature - and the fix in this task closes it too.

## HOW

React to new content anchors via the shared `StrictDoc.onInsert(selector,
callback)` contract (`app_core.js`, introduced by
`developer/tasks/20260724_stimulus_free/task.md`), registering for
`CONTENT_ELEMENT_SELECTOR` (`sdoc-anchor`), instead of a dedicated
`MutationObserver` on the content container — per that contract, feature
scripts must not each run their own subtree-wide `MutationObserver` for
this purpose. On a triggering call (coalesced via
`requestAnimationFrame`, matching the existing debouncing pattern used
elsewhere in the file — necessary here since `onInsert` calls back once
per matched element, not once per mutation batch), re-run
`processAnchorList()` for the content frame and recompute currently
visible sections, without resetting the TOC link mappings
(`processLinkList()` / `resetState()`).

This is safe without a full state reset because `processLinkList()`
already captures a `link` reference for every node's anchor id from
the initial full TOC scan, including nodes whose content has not yet
appeared in the DOM. When `processAnchorList()` later discovers a new
anchor id, it merges the newly found anchor element into the existing
entry for that id, which already carries the correct TOC link.

The new `onInsert` registration fires only for elements matching
`CONTENT_ELEMENT_SELECTOR` (`sdoc-anchor`) - either the inserted node
itself or a descendant of it - and does not fire for removals or for
unrelated markup changes. Concretely, for the existing edit flow:

- Opening a node's edit form replaces its read view (turbo-stream
  `replace`) with form markup that contains no `sdoc-anchor` at all -
  this observer never fires while a node is being edited.
- Saving a node re-inserts its read view (with a fresh anchor) *and*
  updates `frame-toc` in the same response, so this observer's firing
  here is redundant with the existing `frame-toc` observer - both run,
  `processAnchorList()`'s own `anchorsCount`/`anchorsSig` check finds
  nothing changed on the second pass, so the net effect is one extra
  cheap, coalesced no-op pass.
- Canceling a node's edit re-inserts its read view (with a fresh
  anchor) *without* touching `frame-toc` (see WHY) - this is the one
  existing-feature path where this observer is not redundant: it is
  the only thing that re-associates the `IntersectionObserver` with
  the newly-inserted anchor element, fixing the stale-highlight-after-
  Cancel bug described above.

Beyond today's existing flows, this observer is also what activates
once a mechanism exists that inserts content without mutating
`frame-toc` at all on initial insertion - which is the
lazy-chunk-loading case this task is meant to prepare for.

Open implementation consideration: `processAnchorList()` performs a
full re-scan and signature computation over all anchors currently in
the DOM on each run. Under frequent content-only mutations (e.g.,
scrolling through many lazily-loaded chunks in quick succession), the
cost of this re-scan grows with the total number of anchors already
present. Start with the full re-scan approach; if measurement shows
this to be a performance concern on large documents, consider
processing `MutationRecord.addedNodes`/`removedNodes` directly for an
incremental update instead of a full re-scan.

Out of scope: the pre-existing `MutationObserver` on `frame-toc` is not
migrated to `StrictDoc.onInsert` as part of this task. It reacts to the
TOC container being replaced wholesale, not to a specific new element
of interest appearing — a different kind of reaction than what
`onInsert` is designed for. `TOC_ELEMENT_SELECTOR` (`'a'`) is also too
generic to register page-wide via `onInsert` without matching unrelated
links elsewhere on the page, and doing so would call back once per
matched link instead of once per replace event, requiring a new
coalescing wrapper that does not exist for this path today (unlike
`scheduleAnchorRescan`/`scheduleHighlightRefresh`). Migrating it is a
possible separate future cleanup, not required by this task's success
criteria.
