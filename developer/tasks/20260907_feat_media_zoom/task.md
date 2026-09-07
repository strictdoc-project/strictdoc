# Media zoom

## WHAT

An image, or a rendered Mermaid/PlantUML diagram, whose natural size exceeds
its displayed (shrunk-to-fit) size beyond a threshold shall show a `zoom-in`
cursor on hover. Media within the threshold shall show no such affordance.

Clicking a zoomable media element shall open a full-viewport overlay with a
clone of that media. The overlay shall be a dedicated full-viewport viewer,
not the existing constrained modal component.

Inside the overlay:

- The mouse wheel shall zoom centered on the cursor position. Zooming beyond
  the media's natural size shall be allowed.
- Dragging (optionally with Space held) shall pan the media. Content shall be
  unselectable while dragging and selectable/copyable at rest.
- A double-click shall toggle between fit-to-screen and 100%.
- Escape or a click on the backdrop shall close the overlay.

The current zoom level shall be exposed through a dedicated function,
decoupled from its on-screen indicator, which is designed separately once the
above is implemented.

## WHY

Documents shrink embedded images and diagrams to the page width
(`sdoc-autogen img, svg { max-width: 100% }`), which can make large diagrams
or screenshots illegible. Users need to inspect such content at full or
larger size without leaving the document.

## HOW

New shared static module `media_zoom.js` + `media_zoom.css` under
`strictdoc/export/html/_static/`, included from `document/index.jinja` and
`table/index.jinja` next to `modal.js`, `pan_with_space.js`, and the
Mermaid/PlantUML scripts.

- Zoomability check: natural vs. displayed size (`naturalWidth`/`viewBox`
  vs. `getBoundingClientRect()`), with a tolerance ratio to absorb rounding.
- The overlay is built by cloning the media node (`cloneNode(true)`); the
  original document DOM is left untouched, so opening/closing needs no
  teardown of the source element.
- Escape-to-close reuses the existing delegated Escape handler in `modal.js`
  by marking the overlay `data-js-modal`.
- Pan uses the same `grab`/`grabbing` cursor convention as
  `pan_with_space.js`, but drives a CSS `transform: scale() translate()`
  instead of `scrollLeft`/`scrollTop`, to support zoom-to-cursor. Shared
  drag logic is factored out only if real duplication appears once both
  exist.
- `docs/test/test.sdoc` holds manual/e2e test fixtures: a small and a large
  node for each of images, Mermaid, and PlantUML.
