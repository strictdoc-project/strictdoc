# Media zoom

## WHAT

Every image, or rendered Mermaid/PlantUML diagram, in a document shall show
a `zoom-in` cursor on hover.

Clicking a media element shall open a full-viewport overlay with a clone of
that media. The overlay shall be a dedicated full-viewport viewer, not the
existing constrained modal component. It shall open with the media fit to
the viewport, without enlarging it past its natural pixel size. Selecting
text inside a diagram (e.g. a Mermaid/PlantUML label) shall not open the
overlay.

Inside the overlay:

- The mouse wheel shall zoom centered on the cursor position. Zooming beyond
  the media's natural size shall be allowed.
- Dragging (optionally with Space held) shall pan the media. Content shall be
  unselectable while dragging and selectable/copyable at rest.
- Arrow keys shall pan the media, independent of Space. Alt held shall pan
  faster.
- A double-click shall toggle between fit-to-screen and 100%.
- Escape or a click on the backdrop shall close the overlay.
- A small hint in the corner of the overlay shall show the pan/zoom keys.

The current zoom level shall be exposed through a dedicated function,
decoupled from its on-screen indicator, which is designed separately once the
above is implemented.

## WHY

Documents shrink embedded images and diagrams to the page width
(`sdoc-autogen img, svg { max-width: 100% }`), which can make large diagrams
or screenshots illegible. Users need to inspect such content at full or
larger size without leaving the document.

The affordance applies to every image and diagram, not only ones StrictDoc
has visibly shrunk: a reader should not have to guess which media responds
to a click, and a small screenshot can still hide detail worth enlarging.

## HOW

New shared static module `media_zoom.js` + `media_zoom.css` under
`strictdoc/export/html/_static/`, included from `document/index.jinja` and
`table/index.jinja` next to `modal.js`, `pan_with_space.js`, and the
Mermaid/PlantUML scripts.

- An image or diagram gets the zoom affordance as soon as its natural size
  can be read (`naturalWidth` for `<img>`, `viewBox` for Mermaid/PlantUML's
  SVG output); a broken image or a viewBox-less SVG gets none, since the
  overlay would have nothing to size itself from.
- The overlay is built by cloning the media node (`cloneNode(true)`); the
  original document DOM is left untouched, so opening/closing needs no
  teardown of the source element. The clone keeps the source's `id`:
  Mermaid scopes its generated `<style>` to it, so stripping the id would
  leave the clone's shapes unstyled.
- The initial view fits the media to the viewport, capped so it never
  enlarges past the media's own natural pixel size; a small image opens at
  1:1 instead of blown up to fill the screen.
- The overlay is tagged `data-js-modal` for consistency with the rest of
  the modal vocabulary, but closing on Escape is handled directly in
  `media_zoom.js`: `modal.js` (whose delegated Escape handler would
  otherwise cover this) is only loaded on the server-mode document screen,
  not in static HTML exports, and the zoom overlay has to work in both.
- A double-click's second `mousedown` is intercepted (`event.detail > 1`)
  to stop the browser's own word-selection from firing before the
  fit/natural toggle runs.
- Pan uses the same `grab`/`grabbing` cursor convention as
  `pan_with_space.js`, but drives a CSS `transform: scale() translate()`
  instead of `scrollLeft`/`scrollTop`, to support zoom-to-cursor. Shared
  drag logic is factored out only if real duplication appears once both
  exist.
- A small `sdoc-media-zoom-hint` label in the corner names the pan/zoom
  keys, styled with the same tokens as the rest of the UI chrome
  (`--color-bg-ui`, `--color-fg-secondary-invert`); `pointer-events: none`
  keeps it from blocking a backdrop click meant to close the overlay.
- A click that ends a text-selection drag still fires as an ordinary
  `click`; the open-on-click handler checks `window.getSelection()` first
  and skips opening the overlay when it is non-empty, since a plain click
  (no drag) always leaves the selection empty.
- Arrow-key panning mirrors `pan_with_space.js`'s own arrow-key handling
  (same step size, same Alt-held speedup), and exists independently of
  Space+drag: on at least one reported Linux setup, Space+drag panning
  did not work at all, so mouse-drag cannot be the only way to pan.
- e2e coverage: `tests/end2end/screens/document/media_zoom/`.
