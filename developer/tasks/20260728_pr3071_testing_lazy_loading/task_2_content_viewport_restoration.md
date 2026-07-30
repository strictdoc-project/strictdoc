# Content viewport restoration: feature scope

The DOCUMENT screen must preserve the semantic content the user is viewing
while server updates and lazy rendering change document geometry.

## Problem

Raw `.main.scrollTop` is not a stable document position. A loaded chunk and its
placeholder can have different heights, and a full content replacement can
turn previously rendered nodes back into placeholders. The same pixel offset
can therefore point to different semantic content after an update.

The stable value is a semantic witness and its coordinate relative to the
`.main` viewport. When geometry above that witness changes, the viewport must
be compensated by the same amount unless newer user navigation or scrolling
owns the position.

## Scope

Viewport restoration covers:

- lazy placeholders being replaced by rendered chunks;
- removal of estimated placeholder height;
- full replacement of `frame_document_content`;
- delayed outer-box height changes in observed chunk nodes;
- create, delete, move, grammar edit, and ordinary passive reading;
- both chunked and non-chunked server documents.

TOC/hash navigation is a separate owner of viewport intent. It keeps native
fragment, history, and `:target` semantics and must take priority over passive
restoration.

## Final architecture

The feature is implemented by the stateful controller in
`content_viewport_restoration.js`. It:

- captures visible `sdoc-node` content and semantic anchor fallbacks;
- associates asynchronous work with controller generations;
- distinguishes passive reading, active user scrolling, explicit navigation,
  and operation-specific positioning;
- restores before paint when chunk DOM insertion changes upper geometry, then
  performs a final correction after placeholder height is removed;
- delegates passive loads to native scroll anchoring during confirmed active
  scrolling so an old snapshot cannot pull against the user's gesture;
- uses a complete MID-to-chunk index for operation targets that are absent from
  TOC;
- observes relevant rendered nodes by `border-box` for delayed geometry
  changes;
- exposes the shared `StrictDoc.contentViewport` runtime contract used by TOC
  navigation and the manual drag-and-drop stream path.

The complete invariant, event ordering, ownership rules, operation behavior,
and runtime API are specified in
`task_4_stateful_viewport_controller.md`.

## Test coverage

Direct end-to-end coverage lives in
`tests/end2end/screens/document/lazy_loading_scroll_preservation`.

The geometric meaning of each scenario, hardening methodology, current
guarantees, and remaining optional combinations are recorded in
`task_4_stateful_viewport_controller_test_audit.md`.
