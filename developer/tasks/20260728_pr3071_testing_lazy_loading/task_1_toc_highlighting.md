# TOC navigation and highlighting correctness under chunked (lazy-loaded) documents

## WHAT

TOC current-section highlighting, deep-link navigation (TOC click,
`hashchange`, initial URL fragment), and native browser fragment
semantics (`:target`, `hashchange`) must preserve the same
observable, user-facing behavior for a chunked (lazy-loaded) document
as for a non-chunked one - not necessarily the same internal
mechanism or timing (e.g., a not-yet-loaded target's chunk is
force-loaded first, and fragment-navigation processing runs again
once it exists):

- Current-section highlighting (`intersected`) must correctly track
  content that appears in the DOM after initial page load, regardless
  of cause, and must end up reflecting the actual destination after a
  hash/TOC-driven navigation - not an intermediate node passed through
  while a chunk was still loading.
- Clicking a TOC link, an in-page `hashchange` (script-driven,
  back/forward), and an initial URL fragment (including one resolved
  via a stable UID/MID redirect) must each: update the `targeted`
  highlight, make CSS `:target` match the destination node, and
  actually scroll the viewport to it - whether that node's chunk is
  already loaded or still needs to be force-loaded, and regardless of
  whether any chunks between the current position and the destination
  are loaded. A real `hashchange` event is the mechanism for the first
  two triggers; the initial-fragment case has no prior state to change
  from, so no `hashchange` fires for it - the `window` `load` handler
  covers it instead. Exception: clicking the TOC link for the section
  the URL's hash is already on does not change `location.hash`, so no
  `hashchange` fires there either - that case scrolls to the target
  directly instead of going through the hash-change path.
- No regression to non-chunked documents or to any existing
  navigation/highlighting behavior (node create/update/delete, folder
  collapse/expand, Cancel) - including when the edited/created/deleted
  node's own chunk is already loaded but the chunks immediately before
  and after it are still unloaded placeholders.
- `toc_highlighting.js`'s reaction to newly-inserted content must not
  depend on the specific mechanism of any one chunking implementation -
  it must generalize to "content appeared in the DOM," regardless of
  cause. `toc_chunk_navigation.js` is not held to that same generality:
  it is inherently tied to the document-chunk-frame contract
  (`data-chunk-frame`, `document-chunk-N` ids) of this specific
  chunking implementation.

Current test-coverage status against these criteria:
`test_coverage_audit.md` in this directory.

## WHY

Server-side lazy loading of large documents in chunks (PR #3049)
inserts content into the DOM well after initial page load, and drives
deep-link navigation programmatically. Both TOC highlighting and TOC
navigation predate chunking and were built assuming all content - and
the TOC itself - are fully present and synchronized from the first
`load` event. Chunking breaks that assumption in three independent
ways:

1. `toc_highlighting.js` only re-scans content anchors when the TOC
   frame itself mutates. Before chunking, almost every content change
   was accompanied by a TOC-frame mutation (the server always
   re-renders and streams the full TOC alongside any content change) -
   Cancel was already a narrow, pre-existing exception (see
   `../20260726_toc_highlight_improvement/task.md`). Lazily-loaded
   chunks are the primary case where content changes without touching
   the TOC frame at all, and the one that made the gap visible.
2. `.main`'s `scroll-behavior: smooth` means any scroll into a chunked
   document animates toward an endpoint computed once, up front. Chunks
   between the current position and the destination can still be
   resolving from an estimated placeholder height to their real
   rendered height while that animation is in flight, shifting the
   target's actual position mid-scroll - the animation then lands
   short of it.
3. CSS `:target` and the `hashchange` event are both tied to the
   browser's actual fragment-navigation processing. Driving navigation
   programmatically (needed to force-load a chunk before scrolling to
   it) can silently produce neither, unless done carefully.

## HOW

**`toc_highlighting.js`** (see
`../20260726_toc_highlight_improvement/task.md` for the original,
detailed writeup): react to newly-inserted content anchors via the
shared `StrictDoc.onInsert` contract, in addition to the existing
TOC-frame observer.

The steady-state scroll path keeps an ordered cache of anchors that have TOC
links. Section intervals are vertically ordered, so two binary searches locate
the interval overlapping the viewport without reading every loaded anchor's
geometry. Only TOC links whose `intersected` state changed receive an attribute
write. A 600-anchor regression records DOM geometry reads rather than unstable
wall-clock time: the previous full scan performed 1199 reads for one update;
the logarithmic implementation performs 19, with a browser-tolerant ceiling of
64.

`StrictDoc.onInsert` coalesces anchors inserted in one frame. When they form
one new contiguous DOM range with unique IDs, the range is inserted into the
ordered anchor caches and only those new anchors are registered with
IntersectionObserver. In a 600-node document, loading an equal 100-anchor chunk
previously registered 200 anchors near the beginning and 600 near the end; the
incremental path registers 100 in both positions.

Replacing an existing anchor element with the same ID, or inserting several
disjoint ranges in one frame, uses the established full reconciliation
fallback. This preserves edit/save/cancel and structurally complex update
semantics without imposing their cost on normal lazy chunk insertion.

**`toc_chunk_navigation.js`**:
- `scrollToFragment()` temporarily forces the scroll container's
  `scrollBehavior` to `"auto"` for the duration of a single
  programmatic jump, removing the animation window a mid-flight layout
  shift could otherwise race against.
- All TOC-link-click navigation is driven uniformly through a real
  `location.hash` assignment (not `history.pushState`), whether the
  target is already loaded or needs force-loading, so `hashchange` and
  `:target` are produced through the browser's own native
  fragment-navigation processing, the same as for a non-chunked
  document.
- `refreshTargetElement()`: browsers decide `:target` once, when
  fragment-navigation processing runs, and do not re-evaluate it later
  just because a matching element subsequently appears. Once a
  force-loaded chunk's target exists, its hash is bounced through a
  `history.replaceState`-only placeholder and back to a real
  `location.hash` assignment, re-triggering that decision without
  leaving an extra browser-history entry.
