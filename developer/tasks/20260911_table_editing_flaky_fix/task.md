# Reliable table inline editing

## WHAT

Table inline editing shall preserve user input and display the latest accepted
server value when requests or Turbo Stream rendering complete out of order.

Cancellation, reactivation, validation, and duplicate save triggers shall have
deterministic results on slow servers.

## WHY

Table editing has repeatedly failed in CI while passing locally. The failures
come from races between user actions, network responses, and Turbo's deferred
DOM updates. Timing-based test waits hide some failures without making the UI
safe.

**There are two root causes.**

1. Turbo applies a response on a later animation frame. The response check and
   the DOM update do not happen at the same time, which creates a real race
   condition. In other words, a user action can make the response stale after
   the code checks it but before Turbo changes the DOM.
2. Editor loading, activation, and saving have separate lifetimes. The code did
   not always distinguish these states, so a late response from an earlier state
   could damage the current state of the cell by closing a reopened editor,
   restoring an old error, or discarding a correction.

Fast responses make both race conditions less likely, but do not eliminate them.

Early saves, duplicate save events, shared-form comparisons, and timing-based
tests exposed these problems but were not separate root causes.

## HOW

Apply cell-targeted responses only while their edit session is current. Keep
the active editor intact when an older save completes, but record accepted
server markup as the new cancellation baseline. Queue a changed value behind
an in-flight save and discard only true duplicate triggers.

Exercise each response ordering with deterministic headless E2E tests.
