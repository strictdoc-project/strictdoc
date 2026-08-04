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

Native browser scroll anchoring helps with ordinary layout changes, but it
cannot coordinate the complete product behavior:

- it cannot preserve an element after that element's DOM has been replaced;
- it cannot know that a newly created node is the intended destination;
- it cannot implement the required deletion boundary;
- application code may still issue a delayed correction based on an older
  position and pull against the user's current scrolling.

The content viewport therefore opts out of native scroll anchoring. Otherwise
the browser and the controller can compensate the same chunk change in
different rendering phases and move the content twice. One controller owns all
geometry compensation inside the content viewport.

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

A passive chunk response that is still waiting to render is different from an
obsolete operation target. When another wheel or keyboard event advances the
generation, that pending passive snapshot moves into the new generation.
Passive resize locks for already loaded chunks move with it. Otherwise user
input between response arrival and DOM insertion would discard compensation
for the chunk that the user is approaching.

Wheel, touch, pointer, and scrolling-key input cancel an operation-specific
position from the previous state. Ordinary `scroll` events update the
`scrollTop` baseline stored in passive locks. They do not start a new
generation because layout changes and controller-applied corrections also
produce `scroll` events.

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
   microtask immediately compensates the measured geometry change. This early
   correction matters
   because Turbo can insert the real DOM one paint opportunity before emitting
   `turbo:frame-load`; waiting for frame-load alone would allow the user to see
   one uncompensated jump.
3. On `turbo:frame-load`, after the estimated `min-height` has been removed,
   compensate only the remaining geometry change. This is the final correction
   for the complete placeholder-to-rendered-content height difference.

The result is that a chunk above the viewport may change the document's total
height substantially, while the witness visible inside `.main` remains at the
same coordinate.

If the chunk is below the witness, the witness does not move. The shared
positioning function measures a negligible difference and performs no
`scrollTop` write. In this case the controller observes the event but leaves
the result to normal browser layout.

### Loading a lazy chunk during continuous user scrolling

Passive compensation preserves geometry, not an old viewport coordinate. For
each witness the snapshot stores its coordinate inside the scrollable document:

```text
content_top = witness_viewport_top + scrollTop
```

User scrolling changes `witness_viewport_top` and `scrollTop` by opposite
amounts, so `content_top` stays unchanged. Inserting or resizing content above
the witness changes `content_top`. The controller adds that geometry delta to
the current `scrollTop`; it never replaces the current position with the value
captured before the gesture. Wheel, keyboard, touch, and scrollbar movement
therefore continue in their original direction while the layout correction is
composed with them.

When shrinking content makes the document shorter near its end, the browser
must clamp `scrollTop` to the new maximum even though native anchoring is
disabled. The controller subtracts this already-applied automatic movement
from the measured geometry delta and adds only the uncompensated remainder.
Without this subtraction, one height change would be handled twice.

Several chunks can change before all of their observers run. After one passive
lock compensates the geometry visible at that moment, the controller updates
the document-coordinate baselines of every current passive lock. A later
callback then measures only geometry that appeared after that correction. If
each lock updated only itself, another lock could include an already handled
chunk delta and move the viewport twice.

This mechanism applies to geometry changes of every size and does not depend
on a time window, input speed, or input device. A viewport-height threshold is
incorrect because even a modest mismatch between estimated and real chunk
height creates a clearly visible jump during very slow scrolling.

This exception applies only to passive reading. An explicit navigation target
or operation-specific target remains authoritative even if additional chunks
load while it is being positioned.

For an operation-specific target, the controller restores once when
`turbo:frame-load` reports that the placeholder has been removed and once more
on the next animation frame. Related frame-load work can finish changing
geometry after the event handler; without the second correction, that late
change can move the target away from its saved coordinate. Direct user input
advances the viewport generation, so the delayed correction cannot pull
against a newer user action.

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
the controller compensates in the observer callback, after layout and before
paint. Waiting for another animation frame would expose the displaced content
for one paint opportunity.

The observer uses each node's `border-box`, not the default `content-box`.
Changes to padding or border alter the node's outer height and move every
element below it even when the content-box size stays unchanged. Observing the
outer layout box therefore matches the geometry that affects viewport
positioning.

This guarantee is deliberately bounded. The controller observes relevant
rendered chunk nodes while the corresponding lock generation is current. It
does not claim to detect every possible geometry mutation anywhere on the
page. Passive observation survives direct user scrolling so a delayed resize
can be composed with the reader's current position.

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
- build the complete semantic node order from rendered `article-<MID>` frames
  and the MID indexes of unloaded chunks, rather than from TOC entries;
- record the removed node's visible boundary and the MID of its actual next or
  previous node, including nodes such as untitled `TEXT` that are absent from
  TOC;
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

Explicit navigation and operation targets use exact vertical positioning:

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

Passive chunk loading and delayed resizing use additive geometry compensation
instead. The controller compares the witness's saved and current
document-relative coordinates, subtracts any `scrollTop` clamp already applied
by the browser, and adds only the remaining delta. Ordinary scroll events
update the passive locks' `scrollTop` baselines without rescanning visible
document content.

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
