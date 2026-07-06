# Expand the TOC branch to the active anchor

## WHAT

When the user navigates to an anchor (clicking a TOC link, clicking an
in-content link, following an external/bookmarked URL with a `#fragment`,
or loading the page directly on a fragment), the TOC branch containing
that anchor shall expand if it was collapsed — up to the anchor, not
deeper. If the anchor itself is a collapsed folder, its own children
stay collapsed; only the chain of ancestor branches above it opens.

## WHY

Issue #2939. `collapsible_toc.js` (collapse/expand) and
`toc_highlighting.js` (anchor → TOC link mapping, hash navigation) do
not coordinate. If the anchor's branch is collapsed, the link stays
hidden in the DOM, and `toc_highlighting.js` silently moves the
highlight up to the nearest *visible* ancestor instead of revealing the
actual target. The TOC selection and the URL fragment then disagree
about what's "current".

## HOW

`collapsible_toc.js` (collapse/expand state) and `toc_highlighting.js`
(anchor → TOC-link mapping, IntersectionObserver-based highlighting)
are independent concerns reacting to independent triggers (clicks vs.
scroll). That separation is preserved: `collapsible_toc.js` reacts to
URL navigation on its own, the same way it already reacts to clicks,
rather than being driven through `toc_highlighting.js`'s highlight
recompute pipeline.

- `collapsible_toc.js` adds a `hashchange` listener, plus re-checks the
  current `location.hash` after every TOC re-render (covers Turbo-frame
  swaps, which use the History API and don't fire `hashchange`).
- On a match, it walks up the ancestor `<li>` chain from the target
  link, expanding any collapsed branch — stopping at the link's own
  `<li>`, so a collapsed *target* folder is not auto-expanded into its
  children.
- The target link is resolved by anchor id, not by receiving a live DOM
  reference from `toc_highlighting.js` — the two scripts don't need to
  share internal state for this.
- One narrow cross-script signal is needed, declared in `app_core.js`
  alongside the existing `TOC_STATE_CHANGED`: `TOC_FRAGMENT_RESOLVED`.
  `toc_highlighting.js` emits it only when a hash points at a
  renamed/renumbered anchor and it silently corrects the URL via
  `history.replaceState()` — which, unlike a real navigation, does not
  fire `hashchange`, so `collapsible_toc.js` has no other way to learn
  about the corrected target. Payload is `{ anchor: string }` (an id),
  not a DOM reference. The full bus contract (each event, who
  emits/listens, why) is documented once in `app_core.js`.

This design has no feedback-loop risk: collapsing a branch doesn't
change the URL, so it can never re-trigger `hashchange` or
`TOC_FRAGMENT_RESOLVED`.

### Files touched

- `strictdoc/export/html/_static/app_core.js` — `TOC_FRAGMENT_RESOLVED`
  event and the bus contract documentation.
- `strictdoc/export/html/_static/collapsible_toc.js` — ancestor-expand
  logic, anchor-id resolution, the `hashchange` listener, and the
  `TOC_FRAGMENT_RESOLVED` listener.
- `strictdoc/export/html/_static/toc_highlighting.js` — emits
  `TOC_FRAGMENT_RESOLVED` from the renamed-anchor branch of
  `handleHashChange()`.
- `tests/end2end/navigation/toc/toc_navigation/test_case.py` (and its
  `input`/`expected_output` fixtures) — covers: collapse a 3-level-
  nested branch (`Parent section` > `Child section` > `Grandchild
  section`), navigate directly to the hidden `#SECTION_CHILD` URL (full
  page load, not a TOC click), assert the ancestor branch opens, and
  that `Child section`'s own collapsed state (hiding `Grandchild
  section`) is left untouched — "up to the anchor, not deeper". This
  belongs in `toc_navigation` (anchor-navigation behavior), not
  `toc_highlighting` (IntersectionObserver-driven highlighting).
