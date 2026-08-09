# Continuous upward scrolling across a lazy-chunk boundary

## Purpose of this document

This document defines the real product regression protected by
`test_50px_upward_scroll_preserves_short_last_node`. It also defines the
instrumentation constraints that must remain true when the test is made less
timing-sensitive.

The test is not merely checking that scrolling looks smooth. It checks that
two independent sources of viewport movement compose correctly:

1. movement requested by the user through real browser wheel input;
2. compensation applied by the viewport controller when lazy rendering
   changes document geometry above visible content.

A future test rewrite must preserve combined coverage of both an uncompensated
geometry change and restoration of an obsolete pre-scroll position. The
production-shaped test must retain real wheel input. A separate deterministic
companion test may use a synthetic wheel-intent event and a direct `scrollTop`
change to force the otherwise narrow response/render ordering. Making the
production-shaped test pass by ignoring movement near `turbo:frame-load`,
replacing its wheel input with a direct `scrollTop` assignment, or allowing an
arbitrary large step would lose the behavior that this regression suite exists
to protect.

## User-visible scenario

The browser initially displays a lower lazy-loaded chunk. Earlier chunks are
still represented by height-estimated placeholders above the visible content.
The user continuously scrolls upward toward those earlier chunks.

Crossing the lazy-loading boundary starts loading the preceding chunk. Its
real DOM contains five nodes with controlled heights of approximately `150`,
`900`, `145`, `460`, and `140px`. The following chunk contains `520` and
`140px` nodes. These sizes reproduce the reported case in which the final
short node of the newly loaded chunk and an already rendered node below it
could jump visibly when the placeholder was replaced.

The test observes semantic witness `CAB-010` after it appears in the loaded
chunk. It also observes `CAB-016`, which was already present in the initially
loaded lower chunk. A semantic witness is used because the product contract is
about preserving the content the user is looking at, not preserving a numeric
`scrollTop` value.

During upward scrolling, a negative wheel delta decreases `scrollTop` and
moves document content downward inside the viewport. The recorder converts
that input into the same sign as the expected witness movement:

```javascript
state.wheelMovement -= event.deltaY;
```

For a `deltaY` value of `-50`, the cumulative expected witness movement grows
by `+50`. If no layout change occurs, an accepted 50px upward wheel step should
therefore produce approximately:

```text
coordinate_step = +50
input_step      = +50
residual_step   = coordinate_step - input_step = 0
```

Browser wheel input is an intent rather than a guarantee that every event will
produce exactly its delta as scrolling. This distinction is the source of the
current instrumentation race, but it does not change the product invariant
described below.

## Geometry that the controller must compensate

An unloaded chunk reserves space through an estimated placeholder height. When
Turbo renders the response, two geometry changes can occur:

1. Turbo inserts the real nodes into the chunk frame.
2. The frame-load lifecycle removes the placeholder's estimated minimum
   height.

If the real height differs from the estimate, the document coordinate of every
node below that chunk changes. Keeping the same numeric `scrollTop` would move
the semantic witness inside the viewport even if the user did nothing.

For a passive witness, the controller stores its coordinate inside the
scrollable document:

```text
content_top = witness_viewport_top + scrollTop
```

Ordinary user scrolling changes `witness_viewport_top` and `scrollTop` in
opposite directions, so `content_top` remains unchanged. Inserting or resizing
content above the witness changes `content_top`. The controller measures only
that geometry delta and adds it to the `scrollTop` that exists at correction
time:

```text
corrected_scrollTop = current_scrollTop + geometry_delta
```

Using the current value is essential. It retains movement that the user made
after the snapshot was captured. The controller must not assign a saved
pre-scroll `scrollTop` or restore the witness to an old exact viewport
coordinate during passive loading.

When compensation is correct, the geometry change itself contributes
approximately zero to the painted witness trajectory. The witness continues
moving only as explained by the user's accepted scrolling.

## Real regression 1: discarding a pending passive lock

The response for a lazy chunk can arrive before Turbo mutates its frame. The
controller captures a passive snapshot at `turbo:before-fetch-response` and
uses it when the DOM is inserted later.

User input between those events advances the viewport generation. An exact
operation target from the previous generation must be cancelled because the
newer user choice has priority. A pending passive chunk snapshot is different:
the chunk is still about to change geometry above the content that the user is
approaching. Its geometry compensation remains necessary and must move into
the new user-selected generation.

The broken implementation used the general invalidation path:

```javascript
function invalidateForUserInput(event) {
  if (!event.target.closest?.(CONTENT_ROOT_SELECTOR)) return;
  pendingDeleteBoundary = null;
  advanceGeneration();
}
```

`advanceGeneration()` invalidates all delayed work. Consequently, the pending
chunk snapshot retains an old generation number. When Turbo inserts the real
chunk, `compensatePassiveGeometry()` rejects that snapshot as stale and does
nothing.

The mismatch between the placeholder and real chunk then moves the visible
witness independently of wheel input. The original regression produced a
painted displacement of approximately `199px` with no corresponding wheel
movement.

The correct implementation calls `advanceGenerationForUserScroll()`. It
cancels operation-specific locks but carries pending passive locks and passive
resize observations into the new generation.

An intentional mutation that replaces
`advanceGenerationForUserScroll()` with `advanceGeneration()` inside
`invalidateForUserInput()` must make the deterministic companion test
`test_user_scroll_during_chunk_request_supersedes_old_position` fail. Natural
continuous input does not guarantee that a response arrives between two wheel
events on every machine, so requiring the production-shaped 50px test alone to
fail this mutation would itself introduce a timing dependency.

## Real regression 2: restoring an obsolete exact position

Another incorrect implementation can retain a snapshot but treat passive lazy
loading like an exact operation-specific restore. It records where a witness
was before newer user input and later restores that old viewport-relative
coordinate when the chunk renders.

This may compensate the chunk's geometry, but it also overwrites some or all
of the scrolling performed after capture. To the user, content pauses, jumps
too far in the gesture direction, or moves briefly against the gesture when a
chunk appears.

Passive compensation must therefore be additive. It measures the change in
the witness's document coordinate and adds only that change to the current
`scrollTop`. Exact restoration remains appropriate for explicit destinations,
such as a newly created node, but not for ordinary reading during continuous
scrolling.

An intentional mutation that replaces passive calls to
`compensatePassiveGeometry()` with `restoreViewportAnchor()` must make
`test_user_scroll_during_chunk_request_supersedes_old_position` fail. The
production-shaped continuous-scroll tests provide complementary browser-input
coverage, while the controlled response/render ordering proves deterministically
that newer movement survives chunk rendering.

## Meaning of the current flaky failure

The test currently stores cumulative wheel-event movement beside witness
coordinates sampled after animation frames. It calculates:

```text
residual_step = coordinate_step - input_step
```

The CI failure reported a residual sequence beginning with `+50`:

```text
[50.0, 0.0, 0.0, ...]
```

That value alone does not show the raw movement pair. For example, it could
come from either of the following:

```text
coordinate_step = 100, input_step = 50
```

or:

```text
coordinate_step = 50, input_step = 0
```

The current assertion prints only residuals, so it cannot distinguish those
cases. Selenium places forty wheel actions and 5ms pauses into one W3C action
sequence, while the page samples geometry through `requestAnimationFrame` and
`setTimeout`. The browser may batch wheel dispatch, scrolling, layout, Turbo
mutation, and painted sampling differently on a loaded CI runner. A wheel event
also expresses input intent; clamping, event coalescing, or an intervening
layout change can prevent its numeric delta from becoming an identical
`scrollTop` change.

The isolated `+50` is therefore not the same signature as the real `199px`
uncompensated geometry regression. It indicates that the current recorder does
not expose enough synchronized raw state to determine which movement occurred.

## Requirements for safer instrumentation

Every painted sample should be one coherent record rather than values spread
across parallel arrays. At minimum, it should include:

```javascript
{
  timestamp,
  witnessTop,
  initialWitnessTop,
  scrollTop,
  wheelMovement,
  loadedChunkIds,
}
```

Chunk lifecycle boundaries should be recorded with the same clock and sample
sequence. Failure output must include the raw witness, `scrollTop`, and wheel
steps rather than only their derived residual.

The final behavioral assertions must still prove all of the following:

1. Real Selenium wheel input caused the viewport to travel upward through the
   natural lazy-loading boundary.
2. The intended preceding chunk actually loaded through Turbo.
3. Chunk insertion did not add a visible witness movement unrelated to
   accepted user scrolling.
4. Chunk insertion did not restore an older exact position and thereby cancel
   or reverse newer user movement.
5. A later ResizeObserver geometry change composes with continuing input under
   the same rule.
6. The deterministic companion test rejects both intentional production
   mutations described above.

The test must not hide the loading interval, discard the first sample after
frame-load, replace wheel input with direct `scrollTop` writes, or permit a
large arbitrary discontinuity. Any of those approaches could make CI green
while removing protection against the user-visible jump.

## Validation protocol for a test rewrite

The normal implementation must pass repeated headless runs on the developer's
browser and on the Linux Chrome environment used by GitHub Actions.

The rewritten tests must then be run against at least these two temporary,
uncommitted production mutations. The mutation oracle is
`test_user_scroll_during_chunk_request_supersedes_old_position`, whose event
listener runs after the production `turbo:before-fetch-response` listener. It
therefore injects newer wheel intent and deterministic viewport movement after
the production snapshot but before Turbo mutates the frame:

1. In `invalidateForUserInput()`, replace
   `advanceGenerationForUserScroll()` with `advanceGeneration()`.
   The test must report an independently produced geometry displacement.
2. In the passive chunk-render path, replace additive
   `compensatePassiveGeometry()` with exact `restoreViewportAnchor()`.
   The test must report that newer wheel movement was overwritten, reversed,
   or supplemented by an unexplained discontinuity.

After each mutation check, restore the production source and confirm that the
normal implementation passes again. These mutation checks are validation of
the test design; the broken variants must never be committed.
