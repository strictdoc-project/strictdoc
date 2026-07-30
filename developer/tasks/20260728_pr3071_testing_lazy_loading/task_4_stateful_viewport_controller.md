# Stateful content viewport controller

The DOCUMENT screen keeps the content currently viewed by the user stable while
asynchronous rendering changes document geometry.

## Core invariant

For every relevant DOM/layout mutation, the controller identifies a semantic
content witness and records its vertical coordinate relative to the `.main`
content viewport.

If the user has not expressed a newer navigation or scroll intent, the same
witness remains at the same viewport-relative coordinate after the mutation:

```text
witness_top_after == witness_top_before
```

The position is semantic rather than based on raw `scrollTop`. A pixel scroll
offset does not represent a stable document position when rendered chunks and
estimated placeholders have different heights.

## Mutation sources

The controller covers:

- a lazy document chunk replacing its placeholder with rendered nodes;
- removal of the placeholder's estimated `min-height`;
- full replacement of `frame_document_content`;
- subsequent lazy loads caused by newly inserted placeholders;
- delayed layout changes belonging to inserted content when they can affect the
  selected witness.

Capture happens as late as possible before the DOM/layout mutation. Network
request start is not a valid capture point because the user can scroll or start
another operation while the response is in flight.

## Semantic witness

The passive reading witness is selected from visible `sdoc-node` content, not
only from zero-height `sdoc-anchor` elements. This preserves a viewport located
in the middle of a tall node whose anchor is above the viewport.

A snapshot contains:

- a stable semantic identifier;
- the witness type;
- its viewport-relative vertical coordinate;
- fallback witnesses in visual order.

If the primary witness disappears, the first surviving fallback is used. The
controller does nothing when no meaningful witness survives.

## Intent and priority

The controller distinguishes passive preservation from explicit positioning:

1. Explicit user navigation, including TOC/hash navigation, owns the final
   viewport position.
2. An operation-specific target, such as a newly created node, owns the position
   while the operation and its resulting layout changes settle.
3. Otherwise the passive semantic witness is preserved.

A newer user scroll or navigation invalidates stale asynchronous restoration.
Every deferred callback is associated with a controller generation and becomes
a no-op when a newer intent supersedes it.

Wheel, touch, pointer, and scrolling-key input advance the generation and
release the active lock. This prevents asynchronous callbacks from fighting a
new user position.

Passive reading has two modes:

- while the viewport is idle, the controller owns the result and restores the
  semantic witness exactly;
- during a confirmed continuous user scroll, the browser owns the current
  frame and the controller does not apply a competing correction.

A user-scroll session starts only from wheel, touch, pointer, or scrolling-key
input and is extended by subsequent content scroll events. Controller-owned
scrolling and scrolling caused solely by layout changes cannot start such a
session.

## Chunk loading

For an ordinary preload/lazy load, the controller captures the current witness
on the last Turbo event before frame rendering. The response-time snapshot
remains live during a confirmed user-scroll session: content-root scroll events
replace it with the latest semantic witness. A frame `MutationObserver` freezes
the snapshot when DOM rendering begins, preventing layout-induced scroll events
from being mistaken for newer user intent.

For an idle viewport or an operation-specific lock, the same mutation callback
also performs an early restore. Turbo can insert the real chunk DOM one paint
opportunity before it emits `turbo:frame-load`; waiting only for frame-load
exposes the complete placeholder/content height delta for one painted frame.
The mutation-microtask restore prevents that frame, and frame-load performs the
final correction after removing the placeholder class and estimated
`min-height`.

If rendering completes while the user-scroll session is still active, the
controller deliberately skips exact passive restoration and delayed geometry
locking for that frame. Exact restoration is one scroll frame behind an
actively moving viewport and appears as a small jump opposite to the user's
direction. Native scroll anchoring therefore owns that frame. Once scrolling
settles, ordinary chunk loads again receive exact semantic compensation.

This exception applies only to passive reading. An active create/delete/move
positioning lock remains authoritative and exact.

For a chunk loaded specifically to resolve TOC/hash navigation, the navigation
target is registered as the owner of the load. Passive compensation must not
override that target.

Lazy placeholders expose the MIDs of every node they contain. This semantic
chunk index is independent of TOC: nodes such as `TEXT` may have no TOC item
but must still be resolvable as operation targets. TOC metadata remains the
navigation index; placeholder MID metadata is the complete node-to-chunk index.

The placeholder estimate and preload mechanism remain part of the design. The
estimate reduces blank space and prevents all frames loading at once;
correctness does not depend on its accuracy.

## Full content replacement

Before replacing `frame_document_content`, the controller records either:

- the current operation-specific target; or
- the passive semantic viewport snapshot.

After replacement it resolves the semantic target in the new DOM. If the target
belongs to an unloaded chunk, that chunk is loaded before positioning.

Restoration remains effective across lazy loads caused by the replacement so
that subsequent geometry changes above the target do not invalidate an
initially correct position.

The full-replacement snapshot becomes the active viewport lock. Ordinary chunk
loads inherit that lock until a newer user input or explicit navigation
advances the generation. This is what keeps a newly created node at its
requested position while neighboring placeholders resolve later.

Loaded chunk nodes are observed with `ResizeObserver` for the current
generation. If post-render processing changes their height, the controller
re-applies the same semantic lock on the next animation frame.

Observation uses the node's `border-box`, not the default `content-box`.
Padding and border changes move all document geometry below a node even when
its content box is unchanged, so only the outer layout box matches the viewport
stabilization contract.

## Scrolling primitive

One shared primitive performs immediate vertical compensation:

- measure the target against the `.main` viewport;
- calculate the remaining delta;
- apply that delta to `.main.scrollTop`;
- avoid smooth animation for compensation;
- do nothing when the measured delta is negligible.

The negligible-delta check happens before writing `scrollTop` or marking a
controller-owned scroll session. Loading or resizing content entirely below
the viewport therefore remains native browser flow: the shared controller
measures the semantic witness but does not claim scroll ownership when the
witness did not move.

During active scrolling, response-time snapshots are rebased only while a
current-generation passive chunk is still waiting to render. The scroll
handler first filters pending chunks using state stored in memory. It calls
the geometry-heavy `captureViewportAnchor()` only when at least one snapshot
can actually accept the result. Stale requests may remain pending until their
`turbo:frame-load` events, but they no longer cause a full loaded-document scan
on every intervening scroll event.

TOC navigation and viewport compensation use this primitive instead of
independently changing and restoring inline `scrollBehavior`.

## Operation behavior

- Create: resolve the created node by MID, load its actual chunk even when the
  node is omitted from TOC, position it at the requested top coordinate, and
  retain it through resulting chunk/layout changes until settling or newer
  user input.
- Delete: retain the semantic boundary around the removed content, falling back
  to an adjacent surviving node at the document end.
- Move: keep the content viewport stable unless the operation provides an
  explicit moved-node target.
- Grammar edit: keep the passive content viewport stable.

For delete, the confirmed action URL provides the MID of the node being
removed. If that node intersects the viewport, the controller records its top
boundary and the adjacent TOC anchor before the server response replaces the
content. The next surviving node is placed at that boundary. At the document
end, the previous surviving node's bottom edge is used.

## Runtime integration

`content_viewport_restoration.js` owns the shared
`StrictDoc.contentViewport` namespace:

- `capture()` returns the current semantic snapshot;
- `restore(snapshot)` resolves and restores it;
- `beginExplicitNavigation(frameId)` advances the generation and marks a chunk
  load as belonging to TOC/hash navigation;
- `invalidate()` releases stale locks;
- `scrollElementToOffset(element, offset)` performs immediate compensation;
- `renderManualStreamMessage(html)` lets the DnD path render its response while
  the standard `turbo:before-stream-render` lifecycle performs capture.

`toc_chunk_navigation.js` registers explicit navigation before force-loading a
target chunk and uses the shared immediate scroll primitive after the target
exists.

The controller captures ordinary chunk geometry on
`turbo:before-fetch-response`. It restores on `turbo:frame-load`, after the
earlier chunk-navigation listener has removed the placeholder class and its
estimated `min-height`.

## Test contract

Tests verify stability over time, not merely one moment at which the target
happens to be correctly positioned.

The base regression scenario:

1. Load a middle/lower chunk and position a semantic witness in the viewport.
2. Keep an earlier chunk represented by a placeholder.
3. Make the earlier chunk's real height substantially different from its
   placeholder height.
4. Trigger the earlier chunk load.
5. Sample the witness coordinate throughout the render/settling interval.
6. Fail if it leaves the allowed tolerance after the controller begins
   preserving it.

Separate scenarios cover full content replacement, create, delete, move,
TOC/hash navigation, and manual scrolling that supersedes stale restoration.

The create regression uses a `SECTION + TEXT` grammar. A visible create form is
opened with "Add TEXT below" on a section whose subtree spans several chunks.
The created sibling belongs to a distant unloaded chunk and has no TOC item.
The test requires the controller to load that exact chunk by MID, place the
created `TEXT` at the form coordinate, and keep it there. This behavior was also
confirmed manually on the real User Guide document.

The continuous-scroll regression moves the viewport after
`turbo:before-fetch-response` has captured its first snapshot but before Turbo
mutates the chunk frame. It begins with actual wheel intent, verifies that the
scroll step is non-zero, and requires frame rendering not to restore the stale
response-time coordinate. The idle upper-chunk test separately verifies that
exact semantic compensation still applies when the user is not scrolling.

Manual verification with slow scrolling in both directions while chunks load
confirmed that passive rendering no longer produces a visible backward jump.

The delayed-resize regression disables native scroll anchoring after an upper
chunk has loaded, increases the outer height of one of its rendered nodes by
600 pixels, and verifies that a lower semantic witness remains fixed. The test
failed with default `ResizeObserver` content-box observation and passes with
border-box observation.

The paint-frame regression samples the witness after every browser paint
opportunity while a strongly misestimated upper placeholder is replaced. It
initially exposed a one-frame movement of approximately 14938 pixels even
though settled assertions passed. Early restoration from the frame
`MutationObserver` removes that painted jump.

The natural-scroll regressions use Selenium W3C wheel input in both directions
to cross lazy preload boundaries. They assert a monotonic content trajectory in
the gesture direction while an upper or lower chunk loads. The concurrent
regression starts two upper chunk loads in one JavaScript task and verifies
that their independent snapshots and cumulative geometry deltas compose
without stale or duplicate compensation.
