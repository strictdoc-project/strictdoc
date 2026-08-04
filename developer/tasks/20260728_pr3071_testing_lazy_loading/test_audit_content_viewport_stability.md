# Content viewport stability: test audit

This audit maps the behavioral contract in
`task_2_content_viewport_stability.md` to automated coverage and records the
remaining optional hardening scenarios.

This document records what is currently tested, what each test proves, and
which stronger regressions are intentionally deferred. It is separate from the
solution description because the implementation contract and the practical
limits of browser UX testing evolve at different rates.

## Geometric contract

The important value is not `.main.scrollTop`. Placeholder replacement, node
rendering, images, fonts, widgets, and later content changes can all change the
height of document geometry above the viewport, making the same `scrollTop`
refer to different content.

The stable value is a semantic witness and its viewport-relative coordinate:

```text
witness_top = witness.getBoundingClientRect().top
              - viewport.getBoundingClientRect().top
```

When an idle document mutation changes geometry above the witness by `delta`,
the controller must compensate the scroll by the same `delta`, leaving
`witness_top` unchanged. Geometry below the witness should require no
compensation.

During continuous user scrolling, restoring an earlier exact viewport
coordinate can reverse part of the user's movement. Passive preservation
therefore stores the witness's coordinate inside the scrollable document and
adds only changes to that geometry to the current `scrollTop`. Native scroll
anchoring is disabled in the content viewport so the browser and controller do
not both compensate one mutation. Explicit operation targets such as a newly
created node still use exact semantic restoration.

## Current fixtures

The main committed fixture contains 35 requirements with a chunk threshold of
10. It creates four chunks and supports full-content replacement, local edits,
create, delete, move, and grammar-edit scenarios.

A generated tall-chunk fixture makes the real height of a chunk above the
viewport substantially different from its placeholder estimate. This is the
deterministic geometry regression: a lower visible witness must remain in place
when the upper placeholder is replaced.

A generated `SECTION + TEXT` fixture contains a section whose subtree spans
several short chunks. "Add TEXT below" creates a sibling far from the visible
form. The created `TEXT` has no TOC entry, so the test also exercises the
complete MID-to-chunk index.

## Current automated coverage

### Passive chunk geometry

`test_user_scroll_during_chunk_request_supersedes_old_position`

- starts an upper chunk request;
- lets the controller capture at `turbo:before-fetch-response`;
- generates wheel intent and moves the content by 120 pixels before Turbo
  mutates the frame;
- proves that the user movement is real and non-zero;
- verifies that rendering does not restore the stale response-time coordinate.

This deterministically protects against the original large "jump back" race.
It models the ordering between response capture, newer user intent, and DOM
replacement. It does not reproduce a long physical trackpad gesture.

### Create

`test_create_scrolls_to_new_node`

- creates a requirement in a chunked document after full content replacement;
- verifies that the new node appears at the top of the content viewport.

`test_create_from_second_open_form_scrolls_to_its_new_node`

- opens two creation forms at the same time;
- submits the second form explicitly;
- verifies that the controller uses the submitted form's frame ID rather than
  the first form in DOM order;
- verifies that the node created from the second form appears at the top of the
  content viewport.

`test_create_text_below_large_section_scrolls_to_distant_new_node`

- opens "Add TEXT below" on a section with a large subtree;
- creates a sibling that belongs to a distant unloaded chunk;
- verifies that a node absent from TOC is resolved through the placeholder MID
  index, its actual chunk is loaded, and it is placed at the top of the content
  viewport.

`test_created_node_stays_stable_when_chunk_above_loads`

- creates a node in a lower chunk;
- then loads an earlier chunk;
- verifies over time that the operation-specific new-node lock survives the
  later geometry change above it.

### Delete

`test_delete_keeps_removed_node_boundary_in_place` verifies the stronger UX
contract: the next surviving node occupies the viewport boundary from which
the visible node was removed.

`test_delete_untitled_text_keeps_removed_boundary_in_place` uses two adjacent
untitled `TEXT` nodes in a lazy chunk. It first proves that the deleted node has
no TOC item, then verifies that the controller finds its next sibling through
the complete MID order and puts that sibling at the deleted boundary.

`test_delete_last_node_falls_back_to_end_of_document` verifies the fallback to
the previous surviving node when no next node exists.

### Move, grammar, and local updates

`test_move_preserves_top_visible_node_position` verifies the manual
fetch/Turbo-stream integration path and preservation of an unaffected visible
witness during one TOC drag.

`test_grammar_edit_preserves_top_visible_node_position` verifies passive
restoration across a full content-frame replacement initiated outside the
content viewport.

`test_edit_in_isolated_middle_chunk_keeps_neighbors_unloaded` verifies that a
node-local edit does not collapse its already loaded chunk or load the
unchanged placeholders on either side.

### Related coverage outside the controller test file

The chunked TOC tests separately verify:

- native hash behavior and repeat clicking of an already loaded target;
- TOC highlighting after a lazy chunk adds its content to the DOM.

Chunked stable-URL tests cover UID and MID links. Unit tests for
`DocumentChunk` verify chunk slicing and preservation of every node MID used by
the semantic placeholder index.

Create, delete, move, and grammar editing are also exercised by their own
non-chunked feature suites. This file does not repeat those operation tests:
its chunked scenarios exercise the same viewport-controller paths and add
full-frame replacement, lazy target resolution, or later chunk geometry.

## Delayed geometry coverage and limits

After a chunk load, the controller observes rendered `sdoc-node` elements with
`ResizeObserver`. A later node-height change is compensated after layout and
before paint in the observer callback. This covers such causes as content
inside a node acquiring its final height after the Turbo frame has loaded.

`test_delayed_chunk_height_change_above_viewport_stays_stable`:

- loads and settles an upper chunk above a lower witness;
- relies on the production controller to disable native scroll anchoring;
- increases the outer height of a rendered upper node by 600 pixels;
- proves that the height delta is substantial;
- waits for semantic restoration and then samples a stable interval.

The implementation guarantee is also bounded:

- it observes `sdoc-node` elements belonging to a chunk for which idle
  restoration was installed;
- a resize inside such a node is visible through the node's border-box change;
- arbitrary geometry changes outside the observed nodes are not automatically
  covered;
- passive geometry locks survive direct user scrolling and compose a later
  resize delta with the reader's current position;
- a newer user intent or navigation advances the controller generation and
  invalidates old locks.

Therefore, "any later height change can never move the viewport" is broader
than the current implementation and tests. The intended UX invariant is
geometry-source-independent, but its exact controller enforcement currently
applies to observed chunk nodes while the relevant lock remains current.

## Hardening coverage

The hardening scenarios use shared `Screen_Document` helpers. Browser and Turbo
lifecycle instrumentation stays out of test cases; scenarios describe source
geometry, user action, and the expected semantic invariant.

### Paint interval, not only the settled result

`test_tall_chunk_replacement_has_no_paint_frame_jump`:

1. places a witness at a non-degenerate coordinate in a loaded lower chunk;
2. keeps a tall, strongly misestimated placeholder immediately above it;
3. records `witness_top` after every browser paint opportunity;
4. triggers the upper chunk load;
5. continues through DOM mutation, placeholder-class removal, compensation,
   and settled frames;
6. proves that the real/placeholder height delta is large;
7. requires every paintable sample to remain within tolerance.

The recorder schedules a zero-delay task from `requestAnimationFrame`. This
observes geometry after the paint opportunity, including later callbacks in
the same animation-frame phase, while ignoring synchronous intermediate
JavaScript state.

### Natural continuous scrolling across a preload boundary

`test_natural_downward_wheel_scroll_does_not_step_backward`:

1. start with an unloaded chunk in the direction of travel and a witness in
   the currently loaded chunk;
2. generate Selenium W3C wheel actions at short intervals;
3. cross the natural preload boundary without setting `loading="eager"`;
4. record the semantic witness trajectory after paint opportunities;
5. prove that the browser-triggered lazy frame loaded;
6. require the content trajectory to remain monotonic in the gesture
   direction.

Unlike idle stability, the witness is expected to move. The assertion is about
direction and discontinuity, not equality to a fixed coordinate. This case
approaches an unloaded chunk below the witness and verifies that geometry below
visible content does not trigger a correction. The production-shaped tests
below cover upward scrolling while upper geometry changes.

`test_slow_upward_scroll_does_not_jump_when_oversized_chunk_loads`:

1. keeps an unloaded chunk with an oversized penultimate node above an
   ordinary unloaded chunk;
2. navigates to the following chunk so both earlier chunks remain unloaded;
3. slowly scrolls upward until the ordinary chunk loads and its first node
   moves down past the viewport top;
4. proves that the oversized earlier chunk loads next and that its node is
   taller than the viewport;
5. samples the ordinary chunk's first node around that load and rejects any
   step larger than three 80px wheel inputs;
6. separately samples a witness that already existed in the initially loaded
   chunk while the ordinary intermediate chunk appears.

Before semantic geometry compensation, the oversized chunk moved the
witness by `20878.8125px` in one painted step in two consecutive runs. With
compensation, the test passes. The separate existing-witness samples show no
corresponding large jump when the ordinary intermediate chunk loads; the
earlier `1347px` change belonged to the newly appearing witness and did not
establish a visible jump of existing content.

`test_very_slow_upward_scroll_preserves_short_last_node` reproduces the
reported sub-viewport jump with five nodes sized to `150`, `900`, `145`, `460`,
and `140px`, followed by `520` and `140px` nodes. It scrolls upward in `8px`
wheel steps and continuously samples a node that already exists in the lower
loaded chunk. With compensation limited to displacements larger than one
viewport, loading the upper chunk moved that witness by `199px` in one painted
step. Additive compensation of the measured document-geometry delta removes
the jump.

`test_50px_upward_scroll_preserves_short_last_node` runs the same five-node
geometry with continuous `50px` wheel input. The recorder stores cumulative
wheel movement beside every painted coordinate and asserts on their
difference, so wheel events batched into one frame cannot be mistaken for a
layout jump. Before passive locks followed user-driven generation changes,
this test exposed a `199px` displacement with no corresponding wheel input.
Carrying passive, but not operation-specific, locks into the new generation
removes that race.

`test_60px_upward_scroll_preserves_delayed_chunk_height_change` adds a distinct
geometry source: it increases an upper node by `120px` after load and verifies
that ResizeObserver compensation composes with continuing wheel input without
an intermediate painted jump.

`test_arrow_up_scroll_does_not_reverse_when_chunk_loads` sends ArrowUp every
`50ms` through the same boundary and increases the upper chunk mismatch by
about `200px`. Exact restoration of the pre-render coordinate reproduced a
painted `435px` forward jump; live diagnostics on the L2 requirements page had
also shown smaller reverse steps at chunks 34 and 33. The permanent fixture
rejects both movement opposite to ArrowUp and a forward step too large to come
from one key action. Additive document-geometry compensation passes without a
keyboard-specific timing exception.

The complete regression run also exposed a separate late adjustment in
`test_created_node_stays_stable_when_chunk_above_loads`. The controller restored
the created node at `turbo:frame-load`, but later rendering work moved it by
about `101px` after that event. Repeating the operation-specific restore on the
next animation frame removes the race. This path remains separate from passive
additive compensation.

### Near-simultaneous loading of multiple chunks

`test_near_simultaneous_upper_chunk_loads_compose_stably`:

1. keeps two independent unloaded chunks above a lower witness;
2. gives the chunks different placeholder/real height deltas;
3. switches both frames to eager loading in one JavaScript task;
4. lets their responses and frame mutations complete independently;
5. records the witness through both replacements;
6. proves that the cumulative geometry delta is substantial;
7. requires every paintable sample to remain at the original coordinate.

This verifies that loading one frame cannot erase or overwrite pending state
for the other and that neither delta is applied twice. Response order is not
artificially controlled; the test exercises the naturally produced
interleaving.

The pruned 19-test run made one interleaving reproducible: one lock compensated
the geometry of both chunks, but only updated its own baseline. The other lock
then applied `767.5px` of already handled geometry again. Synchronizing all
current passive baselines after each correction makes the isolated regression
pass and protects the common additive-compensation mechanism.

A later optional variant could combine concurrent loading with active
scrolling, where neither passive frame may pull the viewport back to an older
snapshot.

## Remaining optional geometry combinations

- force both possible response orders for concurrent chunks;
- move a subtree from above to below the current viewport and the reverse;
- delete a visible structural node with a large descendant subtree;
- trigger multiple lazy loads while an operation-specific create target is
  locked.

These extend confidence but are lower priority now that paint-interval,
continuous-scroll, concurrent-load, and delayed-resize regressions are present.

## Current assessment

The viewport-stability file now contains 20 tests. The 19-test pruned suite
passed in approximately 2 minutes 9 seconds; the untitled-`TEXT` deletion
regression passes in its targeted run. Before pruning, 33 tests took
approximately 13 minutes.
Removed numeric variants did not represent separate branches of the final
algorithm; removing their server startups accounts for most of the reduction.

The previously recorded full project suite completed with 402 passing tests.
The multiple-open-form regression was added afterward and passes in its
targeted run. The full project suite has not been rerun after this addition.

The 19-test suite gives good protection for semantic correctness, painted
idle-frame correctness, wheel continuity in both directions,
concurrent upper loads, delayed observed-node resize, operation positioning,
full-content replacement, and the known stale-snapshot race.

It does not prove every response ordering, operation structure, or geometry
change outside observed nodes. Manual verification remains useful for
platform-specific trackpad behavior and the optional structural combinations.
Slow scrolling in both directions has been manually confirmed without the
reported backward jump.
