# Content viewport stability under dynamic document geometry

## WHAT

The DOCUMENT screen must keep the content that the user is looking at visually
stable when asynchronously rendered content changes the document's geometry.

Visual stability is defined in terms of document content, not the scrollbar's
numeric position. The controller chooses a meaningful visible element, records
where that element appears inside the `.main` viewport, and keeps it at that
same viewport-relative coordinate. This selected element is called the
**witness**:

```text
witness_top_after == witness_top_before
```

For example, if the top of a visible node is 120 pixels below the top of
`.main`, loading content somewhere above that node must not move it away from
the 120-pixel position. The browser's `scrollTop` value may need to change to
produce this result.

This requirement applies when:

- a lazy placeholder is replaced with the rendered nodes of its chunk;
- the estimated height assigned to a placeholder is removed;
- the complete `frame_document_content` DOM is replaced after a server
  operation;
- the replacement DOM introduces new lazy placeholders that subsequently load;
- content that has already been inserted changes height later;
- the user creates, deletes, moves, or edits document content;
- the same server operations are performed in a non-chunked document.

The controller must also respect newer user intent. If the user scrolls or
navigates after a position was recorded, an older asynchronous callback must
not return the viewport to that recorded position.

Some operations intentionally request a new position instead of preserving the
old one:

- after creating a node, the new node must appear at the top of the content
  viewport and remain there while surrounding content finishes loading;
- after deleting a visible node, the next surviving node must occupy the
  boundary from which the deleted node disappeared; when the last node is
  deleted, the previous surviving node provides the fallback boundary;
- after moving nodes or editing the document grammar, the content currently
  visible to the user must remain stable unless the operation explicitly
  requests another target;
- TOC and URL-fragment navigation must finish at the requested navigation
  target and must not be overridden by passive viewport preservation, meaning
  preservation of the existing reading position when no explicit destination
  was requested.

If a geometry change occurs entirely below the visible content, the controller
must not adjust scrolling. The browser's normal document flow already produces
the correct result in that case.

Automated coverage, the geometric meaning of the test scenarios, and the
remaining optional hardening cases are documented in
`test_audit_content_viewport_stability.md`.

## WHY

The numeric value of `.main.scrollTop` cannot identify what the user is looking
at in a dynamically rendered document.

Consider a viewport positioned in the middle of a long document. Several
unloaded chunks exist above it. Each unloaded chunk is represented by a
placeholder whose height is only an estimate. When one of those placeholders
is replaced with real DOM, the rendered chunk may be much taller or shorter
than the estimate. Every node below it then receives a new document coordinate.
Keeping the old `scrollTop` would show different content even though the
scrollbar itself had not been changed explicitly.

A full server response creates a related problem. Create, delete, move, and
grammar-edit operations can replace the entire content frame. The old DOM
elements disappear, loaded areas may become placeholders again, and subsequent
chunk loads continue changing geometry after the initial replacement. A
one-time restoration immediately after inserting the response is therefore
not sufficient.

Native browser scroll anchoring helps with ordinary layout changes, but it does
not cover the complete product behavior:

- it cannot preserve an element after that element's DOM has been replaced;
- it cannot know that a newly created node is the intended destination;
- it cannot implement the required deletion boundary;
- application code may still issue a delayed correction based on an older
  position and pull against the user's current scrolling.

The application therefore needs one coordinated mechanism that understands
semantic document identities, asynchronous rendering stages, operation
targets, and newer user input.

## HOW

### Overview

`content_viewport_restoration.js` implements a stateful viewport controller for
the DOCUMENT screen.

The controller follows the same general sequence for every supported geometry
change:

1. Before the DOM changes, record which meaningful document element represents
   the current viewport position and where that element appears in `.main`.
2. Allow the DOM mutation to happen.
3. Find the same semantic element in the resulting DOM.
4. Measure how far it moved relative to `.main`.
5. Change `.main.scrollTop` by exactly that difference.
6. Continue protecting the selected position through related asynchronous
   changes, unless newer user input or navigation supersedes it.

The recorded element and coordinate are called a **semantic viewport
snapshot**. The element that represents the position is called the
**witness**. These names emphasize that the controller preserves meaningful
document content rather than a raw pixel offset in the document.

### Choosing a semantic witness

For ordinary reading, the controller prefers a visible `sdoc-node`. It does
not rely only on the zero-height `sdoc-anchor` placed before a node.

This distinction matters when the viewport is in the middle of a tall node.
The node's anchor may already be above the viewport, while the node's content
still fills most of the visible area. Recording only the anchor would describe
a position outside the content the user is actually viewing. Recording the
visible node preserves that position correctly.

A snapshot stores:

- the stable semantic identifier used to find the element after DOM
  replacement;
- the kind of witness that was selected;
- the witness's vertical coordinate relative to the top of `.main`;
- additional witnesses in visual order that can be used as fallbacks.

If the primary witness no longer exists after an operation, the controller
tries the fallback witnesses. If none of them survives, the controller does
not invent a position and does not apply a scroll correction.

### Deciding which position has priority

Several events can request different viewport positions at nearly the same
time. The controller resolves such conflicts using the following priority:

1. Explicit navigation, such as a TOC click or URL-fragment change, controls
   the final position because the user requested a specific destination.
2. An operation-specific target controls the position when the operation has a
   defined UX result. A newly created node is the main example.
3. Otherwise, the controller preserves the passive reading snapshot captured
   from the currently visible content.

The implementation calls the currently authoritative snapshot or target a
**viewport lock**. A lock does not disable user scrolling. It means only that
related asynchronous layout callbacks must continue restoring that semantic
target until the work has settled or newer user intent cancels it.

Every lock and delayed callback receives a monotonically increasing
**generation** number. When the user starts another scroll, initiates
navigation, or otherwise establishes a newer position, the controller advances
the generation. A callback from an older generation then becomes a no-op. This
prevents a late chunk response or `requestAnimationFrame` callback from
returning the viewport to an obsolete position.

Wheel, touch, pointer, and scrolling-key input are treated as direct evidence
of user intent. A `scroll` event by itself is not enough: layout changes and
controller-applied compensation also produce `scroll` events, and those events
must not be mistaken for a new user action.

### Loading a lazy chunk while the viewport is idle

An ordinary lazy chunk load changes geometry in two stages:

1. Turbo replaces the placeholder's frame contents with the rendered chunk.
2. The `turbo:frame-load` handler removes the placeholder styling and its
   estimated `min-height`.

Both stages can move content below the chunk. The controller therefore cannot
restore only once.

The event sequence for an idle viewport is:

1. On `turbo:before-fetch-response`, after the response has arrived but before
   Turbo renders it, capture the current semantic viewport snapshot. Capturing
   when the request starts would be too early because the user could scroll
   while the network response is in flight.
2. A frame-local `MutationObserver` detects the actual DOM insertion. Its
   microtask immediately restores the snapshot. This early correction matters
   because Turbo can insert the real DOM one paint opportunity before emitting
   `turbo:frame-load`; waiting for frame-load alone would allow the user to see
   one uncompensated jump.
3. On `turbo:frame-load`, after the estimated `min-height` has been removed,
   restore the snapshot again. This is the final correction for the complete
   placeholder-to-rendered-content height difference.

The result is that a chunk above the viewport may change the document's total
height substantially, while the witness visible inside `.main` remains at the
same coordinate.

If the chunk is below the witness, the witness does not move. The shared
positioning function measures a negligible difference and performs no
`scrollTop` write. In this case the controller observes the event but leaves
the result to normal browser layout.

### Loading a lazy chunk during continuous user scrolling

Exact restoration is correct while the viewport is idle, but it can feel wrong
while the user is actively scrolling.

During continuous movement, a snapshot captured on the preceding scroll event
is already slightly behind the user's current gesture. Restoring that exact
coordinate can produce a small step in the opposite direction: for example, a
brief downward jump while the user is scrolling upward.

To avoid fighting the user, the controller tracks a short **user-scroll
session**:

- wheel, touch, pointer, or scrolling-key input starts the session;
- subsequent `.main` scroll events extend it;
- automatic layout scrolling and controller-owned compensation cannot start
  such a session.

While a passive chunk response is waiting to render, genuine user scroll events
update its snapshot to the newest semantic position. A frame
`MutationObserver` freezes that snapshot when DOM insertion begins, so any
scroll event caused by the insertion itself cannot be recorded as user intent.

If the chunk finishes rendering while the user-scroll session is still active,
the controller does not force exact passive restoration for that frame.
Instead, native browser scroll anchoring handles the layout change while the
gesture continues. Once scrolling becomes idle, later chunk loads use exact
semantic compensation again.

This exception applies only to passive reading. An explicit navigation target
or operation-specific target remains authoritative even if additional chunks
load while it is being positioned.

### Placeholder height estimates and preloading

An unloaded chunk is represented by a placeholder with an estimated
`min-height`. The estimate gives the unloaded part of the document approximate
physical space. Without that space, many placeholders could be close to the
viewport simultaneously and begin loading at once, and the scrollbar would
initially represent only the already rendered content.

An `IntersectionObserver` also begins loading a placeholder shortly before it
enters the visible viewport. This preload margin reduces the chance that the
user reaches an empty placeholder and has to wait for its response.

These two mechanisms improve loading behavior, but neither provides the
correctness guarantee:

- the estimated height is intentionally approximate and may differ greatly
  from the rendered chunk height;
- preloading changes when the geometry mutation occurs, not whether it occurs.

The viewport controller is responsible for stability when the estimate is
wrong. The estimate reduces the typical size and visibility of geometry
changes; it is not used as proof that the viewport will remain stable.

### Finding targets that are inside unloaded chunks

After a full content replacement, the semantic witness or operation target may
belong to a chunk that is currently represented only by a placeholder. The
target element cannot be positioned until its chunk has been rendered.

Each lazy placeholder therefore contains the MIDs of all document nodes in its
chunk. The controller uses this complete MID-to-chunk index to find and load
the frame that owns a requested node.

This index must be independent of TOC data. Some valid operation targets, such
as untitled `TEXT` nodes, have no TOC entry. TOC metadata remains suitable for
TOC navigation, but it cannot serve as the complete index of document content.

### Full content replacement

Before `frame_document_content` is replaced, the controller records either:

- the operation-specific target and its requested viewport coordinate; or
- the passive semantic viewport snapshot.

For creation, several forms may be open at the same time. DOM order does not
identify which form produced the response. When Turbo starts submitting a
create form, the controller records that form's frame ID. The server reuses
the same frame ID for the created node, so the controller can restore the node
that belongs to the submitted form rather than another open form.

If submission fails, the controller discards this target because no full
content replacement will consume it. After a successful submission, the
controller keeps the target until the replacement stream starts rendering.

After replacement, the controller resolves the same semantic identity in the
new DOM. If it belongs to an unloaded chunk, the controller first finds that
chunk through the MID index and loads it. Only then can it position the actual
target element.

The first successful positioning does not end the operation. The replacement
may contain placeholders above the target, and those chunks can load later.
Their changing heights would move a correctly positioned target again.
Therefore, the replacement snapshot becomes the active viewport lock for its
generation. Related lazy loads reuse the same target and coordinate until the
layout settles or newer user input or navigation advances the generation.

This continuing lock is what keeps a newly created node at the requested
viewport coordinate even when the node is located several chunks away from the
form and chunks above it render afterward.

### Delayed height changes after chunk rendering

Geometry can change after Turbo has finished loading a frame. An image, widget,
font, or nested layout may acquire its final size later.

For the current viewport-lock generation, the controller observes rendered
`sdoc-node` elements with `ResizeObserver`. When an observed node changes size,
the controller schedules restoration of the same semantic lock on the next
animation frame.

The observer uses each node's `border-box`, not the default `content-box`.
Changes to padding or border alter the node's outer height and move every
element below it even when the content-box size stays unchanged. Observing the
outer layout box therefore matches the geometry that affects viewport
positioning.

This guarantee is deliberately bounded. The controller observes relevant
rendered chunk nodes while the corresponding lock generation is current. It
does not claim to detect every possible geometry mutation anywhere on the
page, and passive delayed restoration is not imposed on a confirmed active
user-scroll frame.

### Operation-specific behavior

Create:

- record the submitted creation form rather than selecting an open form by DOM
  order;
- use the form's frame ID to identify the created node, which receives the same
  frame ID from the server;
- find and load the node's chunk even if the node has no TOC entry;
- place the rendered node at the top of the content viewport;
- retain that target through related chunk loads and delayed height changes.

Delete:

- before sending the confirmed delete operation, determine whether the removed
  node intersects the viewport;
- record the removed node's visible boundary and adjacent semantic content;
- after replacement, place the next surviving node at that boundary;
- at the end of the document, use the previous surviving node's bottom edge
  when no next node exists.

Move:

- preserve the passive semantic snapshot across the Turbo stream update;
- use an explicit moved-node target only when the operation defines one.

Grammar edit:

- preserve the passive semantic snapshot across full content replacement.

The drag-and-drop move path receives its Turbo stream through a manual fetch.
It passes the response to the standard `turbo:before-stream-render` lifecycle
so capture happens immediately before rendering, rather than at drag start
while the user may still change the viewport.

### Applying scroll compensation

One shared function performs immediate vertical positioning for both viewport
restoration and TOC navigation:

1. Measure the target's current coordinate relative to `.main`.
2. Subtract the requested viewport-relative coordinate to obtain the remaining
   vertical difference.
3. Add that difference to `.main.scrollTop`.
4. Temporarily avoid smooth scrolling so compensation is applied in the same
   rendering step instead of animating toward a coordinate that may change
   again.
5. Skip the write when the remaining difference is negligible.

Skipping negligible writes is important. A needless `scrollTop` assignment
would create another scroll event and could make the controller appear to own
a frame in which the browser already produced the correct result.

During active scrolling, the scroll handler updates snapshots only if at least
one current-generation passive chunk is still waiting to render and can accept
the newer snapshot. It checks this pending state in memory before calling the
geometry-heavy `captureViewportAnchor()`. Ordinary scroll events and stale
pending requests therefore do not scan and measure all loaded document
content.

### Runtime integration

The controller is exposed through the shared `StrictDoc.contentViewport`
namespace:

- `capture()` creates a semantic viewport snapshot;
- `restore(snapshot)` resolves the snapshot in the current DOM and compensates
  its position;
- `beginExplicitNavigation(frameId)` advances the generation and records that
  a chunk load belongs to TOC or hash navigation;
- `invalidate()` advances beyond work that must no longer restore its old
  position;
- `scrollElementToOffset(element, offset)` applies the shared immediate
  positioning behavior;
- `renderManualStreamMessage(html)` renders the drag-and-drop response through
  the lifecycle that captures immediately before the Turbo stream mutation.

`toc_chunk_navigation.js` calls `beginExplicitNavigation()` before
force-loading the chunk that contains a navigation destination. It then uses
`scrollElementToOffset()` after the target exists. This ordering ensures that
passive chunk compensation cannot override an explicit TOC or URL-fragment
destination.
