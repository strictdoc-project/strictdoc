# Fix TOC highlighting on the Table screen

## WHAT

TOC highlighting (the IntersectionObserver-driven "what's currently
visible gets highlighted in the TOC" behavior, from
`toc_highlighting.js`) shall work on the Table screen the same way it
already works on the Document screen.

## WHY

Issue #2946. `toc_highlighting.js` looks up the page's content
container by a hardcoded selector:

```js
const CONTENT_FRAME_SELECTOR = 'turbo-frame#frame_document_content';
...
const contentFrame = document.querySelector(CONTENT_FRAME_SELECTOR)?.parentNode;
if (!tocFrame || !contentFrame) { return }
```

`<turbo-frame id="frame_document_content">` only exists on the
Document screen (`screens/document/document/main.jinja`). The Table
screen's content (`screens/document/table/main.jinja`) is a
`<div class="content"><table>...</table></div>` with no such
turbo-frame — it has no single element that gets wholesale-replaced by
a turbo-stream; node edits update individual `<td>` cells in place.

`<sdoc-anchor>` elements and the `#frame-toc` sidebar both exist on the
Table screen, so highlighting *could* work there — only the content-root
lookup fails, causing `contentFrame` to be `undefined` and the entire
highlighting setup (link/anchor mapping, IntersectionObserver,
MutationObserver) to bail out at the guard clause above before doing
anything.

## HOW

`contentFrame` is resolved once, when the script's `load` handler runs,
and kept as a closure variable for the rest of the page's lifetime - it
is not itself a `MutationObserver` target (that observer watches
`tocFrame`/`#frame-toc`; content/anchor re-scans piggyback on TOC
updates, since both re-render together). `contentFrame` is only used
for `querySelectorAll('sdoc-anchor')` and as the bounding box for "end
of content". So the only requirement on it is to be an element that is
never itself replaced/detached - not a specific DOM depth.

Replace the implicit, Document-screen-specific lookup
(`turbo-frame#frame_document_content` + `.parentNode`, where the
`.parentNode` step exists only to step off the turbo-frame itself,
which *does* get replaced wholesale by `action="replace"` streams, onto
its never-replaced parent) with an explicit marker attribute,
`js-toc_highlighting-content_root`, placed directly on each screen's
own never-replaced content container:

- Document screen: on `<div class="main">` in
  `screens/document/document/main.jinja` (the same element
  `.parentNode` already resolved to - now explicit in markup instead of
  implicit in JS).
- Table screen: on `<div class="content">` in
  `screens/document/table/main.jinja` (this screen has no full-content
  turbo-frame at all - the div itself is never replaced; only rows/cells
  inside it are).

In `toc_highlighting.js`, `CONTENT_FRAME_SELECTOR` becomes
`[js-toc_highlighting-content_root]` and the `?.parentNode` step is
dropped, since the marker is already on the right element.

No changes to the IntersectionObserver / anchor-highlighting logic
itself, or to `collapsible_toc.js` - only how the content root is
located.

### Files touched

- `strictdoc/export/html/_static/toc_highlighting.js` - selector and
  lookup change.
- `strictdoc/export/html/templates/screens/document/document/main.jinja` -
  add the marker attribute.
- `strictdoc/export/html/templates/screens/document/table/main.jinja` -
  add the marker attribute.
- `tests/end2end/navigation/toc/toc_highlighting_table/` (new) - e2e
  coverage for highlighting on the Table screen.
