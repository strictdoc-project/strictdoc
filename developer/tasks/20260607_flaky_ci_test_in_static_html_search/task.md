# 2026-06-07 Fix the flaky test in Static HTML Search (Windows)

## WHAT

Fix the following flaky tests:

- `01_search_on_both_server_and_in_static_html`
- `02_regex_special_character_search_on_both_server_and_in_static_html`

We have been observing these two tests to fail randomly, and we opened a bug report to track this:

https://github.com/strictdoc-project/strictdoc/issues/2872

## WHY

We should have no flaky tests as they slow down the development and compromise the test suite integrity.

## HOW

The common flaky point is the Static HTML Search startup sequence.

Both tests type into the search input immediately after the Project Index page
is loaded. The page's `document.readyState` can already be complete while the
generated static search index is still being loaded asynchronously. If the first
input event is handled before the index is ready, the search UI returns without
showing results and does not replay the input automatically.

The fix is to publish an explicit startup signal from
`static_html_search.js`:

- `StrictDoc.search.isReady` stores the durable readiness state.
- `StrictDoc.bus` publishes the `static-html-search:ready` event when the index
  and node lookup are ready.

The End-to-End Project Index screen helper waits for the usable search payload
before it types into the Static HTML Search input. It checks the current state,
listens for the ready event, and polls for the `index` and `nodesByMid` data so
that a missed event or a temporary refresh state does not make the test flaky.
This creates an intentional link between the flaky tests and the startup
behavior they exercise.

Follow the Developer Guide's newspaper style when placing helper methods:
public screen actions/assertions stay above private `_` helpers.
