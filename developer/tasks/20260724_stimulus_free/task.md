# Remove Stimulus dependency from UI controllers

## WHAT

Migrate all remaining Stimulus-based controllers in
`strictdoc/export/html/_static/controllers/` to plain, dependency-free JS
files colocated in `strictdoc/export/html/_static/`, following the
conventions already established by the existing plain-JS scripts in that
directory (`app_core.js`, `dropdown_menu.js`, `static_html_search.js`,
`stable_uri_forwarder.js`).

Scope of this task — controllers to migrate:

- `scroll_into_view_controller.js`
- `deletable_field_controller.js`
- `movable_field_controller.js`
- `copy_to_clipboard_controller.js`
- `dropdown_menu_controller.js`
- `modal_controller.js`
- `tabs_controller.js`
- `draggable_list_controller.js`
- `autocompletable_field_controller.js`

Requirements:

- No user-visible behavior change for any migrated control: copy to
  clipboard (node anchor, inline RST anchor, stable link, field content),
  delete field, move field up/down, per-node dropdown menu, modal open/close
  (including Escape and cancel button), grammar-form tabs, TOC drag-and-drop
  reorder, and autocompletable fields (typing, keyboard navigation,
  click-to-open, multiple-choice/tag mode) must all work exactly as they do
  today.
- For `copy_to_clipboard_controller.js` specifically: the "misconfigured
  button" case (a copy button with no `sdoc-field` context) must be detected
  and visually flagged eagerly, at the point the button is set up/inserted —
  not lazily on click, and without unconditionally calling
  `event.preventDefault()` for buttons that were never wired up.
- Each migrated script stays a single self-contained file (IIFE), no
  bundler, no build step introduced.
- `data-controller` / Stimulus target (`data-*-target`) attributes tied to a
  migrated controller are removed from the corresponding Jinja templates and
  replaced with plain selectors/data-attributes, consistent with the
  existing plain-JS scripts in `strictdoc/export/html/_static/`.
- Cross-script communication (if any is needed between migrated scripts, or
  with existing plain scripts) goes through `window.StrictDoc.*` in
  `app_core.js`, only for genuine shared contracts — not as a default
  integration mechanism.
- Any control that needs to react to newly-inserted markup (Stimulus's
  `connect()` semantics) registers through the shared
  `StrictDoc.onInsert(selector, callback)` contract in `app_core.js`, backed
  by a single page-wide `MutationObserver`. Scripts must not create their own
  `MutationObserver` for this purpose — with several scripts each running
  their own subtree-wide observer, every DOM mutation anywhere on the page
  would be scanned once per script instead of once total.
- `tasks.py` (`lint-format-js`) is updated to include every new file path.
- `<script src="...">` includes in every consuming Jinja template
  (`strictdoc/export/html/templates/screens/document/document/index.jinja`,
  `.../table/index.jinja`, and the `modal_controller` consumers in
  `strictdoc/features/{diff_and_changelog,trace,search,project_index,deep_trace}`)
  are updated to the new paths.
- End state: no template references `controllers/*.js`, and
  `stimulus_umd.min.js` / `stimulus_application.js` are no longer loaded or
  referenced anywhere.
- Existing unit/integration/e2e tests must keep passing. Where a migrated
  control has no automated coverage, proper test coverage (unit,
  integration, or end-to-end, per `SDG` — no throw-away smoke tests) must be
  added for it as part of this task.

## WHY

Stimulus is a runtime dependency that only makes sense in the
server-driven GUI (it is not used in static HTML export), and it does work
"for free" (declarative wiring, per-element lifecycle, target/value
attribute parsing) at the cost of controlling exactly what loads and when.
The project wants to keep its frontend scripts modular per-file, without
introducing a bundler, while being able to fully control and economize on
what the UI loads and executes — which requires owning the wiring that
Stimulus currently provides implicitly.

## HOW

Migrate one script at a time, in this order (simplest/lowest-risk first,
most complex last):

1. `scroll_into_view_controller.js` — trivial: a single
   `element.scrollIntoView()` call, invoked at the point where the element is
   inserted into the DOM, via `StrictDoc.onInsert`.
2. `copy_to_clipboard_controller.js` — click-based, one copy button per
   context (node anchor, inline RST anchor, stable link, field content).
   Port to a delegated `click` listener over
   `[data-copy-clipboard-target="button"]`. Unlike a purely lazy,
   click-time-only implementation, the "misconfigured button" check (button
   with no `sdoc-field` context) must still run eagerly, at setup/insertion
   time, so a broken button is visually flagged before any click — this
   establishes the delegated-click pattern the remaining click-driven
   controllers below should follow.
3. `deletable_field_controller.js` — click-based removal of a field; port to
   a delegated `click` listener over `[data-js-delete-field-action]`, matching
   the delegated-click pattern from (2).
4. `movable_field_controller.js` — click-based DOM-sibling swap; same
   delegated-listener approach as (3). The `swapNodes()` helper itself is
   already plain DOM code and needs no changes.
5. `dropdown_menu_controller.js` — this is the per-node action dropdown
   (`components/node/node_controls/index.jinja`), functionally a near-twin of
   the already-migrated `dropdown_menu.js` (used by the view-type menu,
   header actions, and table filter). Evaluate reusing/unifying with the
   existing `dropdown_menu.js` selectors (`data-dropdown-handler` +
   `aria-controls`) instead of keeping a second, parallel implementation with
   its own selectors (`js-dropdown-menu-handler` / `js-dropdown-menu-list`).
   Note: `dropdown_menu.js` predates the `StrictDoc.onInsert` contract and
   currently wires itself up via its own `window.addEventListener("load", ...)`
   scan plus a `MutationObserver` scoped to one specific frame id — when
   touching this file, switch it to `StrictDoc.onInsert` as well so there
   isn't a second, separate observer running alongside the shared one.
6. `modal_controller.js` — needs an on-insert hook (the modal is inserted
   into the DOM via a Turbo Stream response) that wires the Escape listener
   and the cancel-button click, via `StrictDoc.onInsert`, and reliably
   removes the Escape listener when the modal is closed or replaced — do not
   leave stale `document`-level Escape listeners behind after a modal
   closes.
7. `tabs_controller.js` — this control generates its own DOM (`<sdoc-tabs>` /
   `<sdoc-tab>`) from existing `<sdoc-tab-content>` markup rather than only
   wiring listeners onto pre-rendered markup. Port as an `initTabs(root)`
   function registered via `StrictDoc.onInsert`; guard against duplicate
   `<sdoc-tabs>` generation if the surrounding form fragment can be
   re-inserted by Turbo.
8. `draggable_list_controller.js` — HTML5 drag-and-drop with:
   - a single shared `dragState` (and shared `dropIndicator` /
     `dragIndicator` elements) that must stay a single instance across the
     whole list, not duplicated per initialization;
   - a direct dependency on `Turbo.renderStreamMessage()` for the server
     round-trip after a drop, which is independent of Stimulus and must be
     preserved as-is;
   - listeners that need re-wiring whenever the list's `<li>` items are
     replaced by a Turbo Stream response after a move — via `StrictDoc.onInsert`,
     not a dedicated observer for this list.
9. `autocompletable_field_controller.js` — migrate last; largest and
   highest-risk piece. It is an adapted fork of `stimulus-autocomplete` and
   currently relies on Stimulus's typed `static values` API
   (`urlValue`, `minLengthValue`, `hasUrlValue`, etc.) for parsing/defaulting
   `data-*` attributes — this parsing has to be reimplemented by hand.
   Per-instance state (debounce timer, `AbortController`, `mouseDown` flag)
   must stay scoped to each individual autocompletable element, since a page
   can have multiple independent instances at once. Note: the current
   `disconnect()` already contains a pre-existing bug — it calls
   `removeEventListener` with `this.onKeydown` / `this.onInputBlur`, which
   are never assigned anywhere (the real handlers are anonymous functions
   registered inside `connect()`), so those listeners are never actually
   removed today. Do not carry this bug forward into the migrated version.

Cross-cutting, applies to every script above:

- Prefer the delegated-listener pattern (one listener on `document` or on a
  stable ancestor) for anything purely click-driven, matching
  `copy_to_clipboard.js`.
- Prefer `StrictDoc.onInsert` (`app_core.js`) for controls that need to run
  setup logic at the moment new markup is inserted (modal, tabs, per-item
  drag handlers, `dropdown_menu.js`) instead of each script creating its own
  `MutationObserver` — see the `onInsert` contract documented at the top of
  `app_core.js`.
