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

During continuous user scrolling, exact restoration has a different problem:
a captured witness coordinate is already one scroll frame behind the user's
movement. Restoring it can produce a short step opposite to the scrolling
direction. During a confirmed active scroll session the browser therefore owns
the current passive-reading frame. Exact semantic restoration resumes after
scrolling settles. Explicit operation targets such as a newly created node
remain authoritative.

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

A nine-node control document remains below the chunk threshold and verifies
that the controller does not regress non-chunked behavior.

## Current automated coverage

### Passive chunk geometry

`test_visible_anchor_stays_stable_when_tall_chunk_above_loads`

- loads a lower chunk and keeps the adjacent tall upper chunk as a placeholder;
- records a semantic witness in the lower chunk;
- replaces the upper placeholder with much taller real content;
- verifies that the witness has the same viewport-relative coordinate after
  loading and remains stable during the following sampling interval.

This proves idle compensation for one large geometry delta above the viewport.

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

`test_create_locally_does_not_jump` covers creation in the inline chunk.
`test_non_chunked_create_unaffected` covers the non-chunked path.

### Delete

`test_delete_preserves_top_visible_node_position` verifies that an unaffected
visible witness remains at its coordinate.

`test_delete_keeps_removed_node_boundary_in_place` verifies the stronger UX
contract: the next surviving node occupies the viewport boundary from which
the visible node was removed.

`test_delete_last_node_falls_back_to_end_of_document` verifies the fallback to
the previous surviving node when no next node exists.

`test_delete_locally_does_not_jump` and
`test_non_chunked_delete_unaffected` cover inline and non-chunked paths.

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

Non-chunked move and grammar-edit counterparts verify that the shared
controller does not regress the legacy rendering path.

### Related coverage outside the controller test file

The chunked TOC tests separately verify:

- native hash behavior and repeat clicking of an already loaded target;
- TOC highlighting after a lazy chunk adds its content to the DOM.

Chunked stable-URL tests cover UID and MID links. Unit tests for
`DocumentChunk` verify chunk slicing and preservation of every node MID used by
the semantic placeholder index.

## Delayed geometry coverage and limits

After an idle chunk load, the controller observes rendered `sdoc-node` elements
with `ResizeObserver`. A later node-height change schedules restoration of the
same semantic lock on the next animation frame. This is intended to cover such
causes as content inside a node acquiring its final height after the Turbo
frame has loaded.

`test_delayed_chunk_height_change_above_viewport_stays_stable`:

- loads and settles an upper chunk above a lower witness;
- disables native scroll anchoring to isolate controller behavior;
- increases the outer height of a rendered upper node by 600 pixels;
- proves that the height delta is substantial;
- waits for semantic restoration and then samples a stable interval.

The implementation guarantee is also bounded:

- it observes `sdoc-node` elements belonging to a chunk for which idle
  restoration was installed;
- a resize inside such a node is visible through the node's border-box change;
- arbitrary geometry changes outside the observed nodes are not automatically
  covered;
- during confirmed active scrolling, passive exact restoration and delayed
  geometry locking for that frame are deliberately skipped in favor of native
  browser anchoring;
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

`test_natural_upward_wheel_scroll_does_not_step_backward` and
`test_natural_downward_wheel_scroll_does_not_step_backward`:

1. start with an unloaded chunk in the direction of travel and a witness in
   the currently loaded chunk;
2. generate Selenium W3C wheel actions at intervals shorter than the
   active-scroll window;
3. cross the natural preload boundary without setting `loading="eager"`;
4. record the semantic witness trajectory after paint opportunities;
5. prove that the browser-triggered lazy frame loaded;
6. require the content trajectory to remain monotonic in the gesture
   direction.

Unlike idle stability, the witness is expected to move. The assertion is about
direction and discontinuity, not equality to a fixed coordinate. The upward
test approaches an unloaded chunk above the witness; the downward test
approaches an unloaded chunk below it. Together they prove that neither
replacement creates a painted step against the user's gesture.

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

The final full project suite completed with 402 passing tests.

The suite gives good protection for settled semantic correctness, painted
idle-frame correctness, natural wheel continuity in both directions,
concurrent upper loads, delayed observed-node resize, operation positioning,
full-content replacement, and the known stale-snapshot race.

It does not prove every response ordering, operation structure, or geometry
change outside observed nodes. Manual verification remains useful for
platform-specific trackpad behavior and the optional structural combinations.
Slow scrolling in both directions has been manually confirmed without the
reported backward jump.
