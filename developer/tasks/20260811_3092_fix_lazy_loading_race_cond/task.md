# Document lazy loading: fix TOC navigation race condition

## WHAT

Clicking a second TOC link before an earlier click's chunk finishes loading
must not move the URL hash/scroll back to the earlier fragment. Only the
most recently requested fragment may drive navigation once its chunk loads.

## WHY

Reported in [issue #3092](https://github.com/strictdoc-project/strictdoc/issues/3092).

`loadChunkThenScroll` (`strictdoc/export/html/_static/toc_chunk_navigation.js`)
registers a `turbo:frame-load` listener per click, with no shared state on
which fragment is currently desired. Clicking a slow-chunk fragment, then a
fast-chunk fragment before the first resolves, leaves the stale listener to
fire later and bounce the hash/scroll back to the first fragment.

An analogous race is already guarded elsewhere in the same feature
(`content_viewport_restoration.js`'s generation counter).

## HOW

Added a module-level `pendingFragment` in `toc_chunk_navigation.js`, set at
the top of `navigateToFragment()` on every call. `onFrameLoad` now checks
`fragment !== pendingFragment` and skips `refreshTargetElement()` if a newer
navigation has superseded it (listener is still always removed).
