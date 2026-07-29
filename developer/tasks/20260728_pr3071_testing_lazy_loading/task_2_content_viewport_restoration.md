# Content viewport restoration after full document content replacement

The DOCUMENT screen must preserve the user's visible content area after
document content updates.

## WHAT

- Full replacement of `frame_document_content` must not make the content
  viewport jump to a different document area just because previously-loaded
  chunks were rendered again as unloaded placeholders.
- The preserved position must be based on a semantic content anchor, not on
  raw `scrollTop`.
- Restoration must work for chunked documents:
  - if the preserved anchor is still in the DOM, scroll it back to the same
    relative viewport position;
  - if the preserved anchor is inside an unloaded chunk placeholder, force-load
    that chunk first and then restore the position;
  - if the closest preserved anchor no longer exists, fall back to another
    visible anchor captured before replacement.
- Creating a node from a visible create form must restore to the created node,
  not to the node that used to be visible behind the form.
- Restoration must also be harmless for non-chunked documents. Short documents
  still go through the same script in server mode, but usually do not need lazy
  chunk loading support.
- Restoration must cover create, delete, move, and grammar-edit flows.

## WHY

Before chunked rendering, the DOCUMENT screen did not have an explicit
StrictDoc mechanism for restoring the content viewport after a full DOM
replacement. The existing behavior relied on the browser keeping the current
raw scroll position while only the document content was replaced.

That looked like correct position preservation because the full document DOM had
stable geometry: after replacement, the nodes above the current viewport had
roughly the same height as before, so the same pixel scroll offset still pointed
at the same document area.

The lazy-chunk navigation/preload work introduced chunk geometry into the
DOCUMENT screen: a document area can now be represented either by real rendered
content or by an unloaded placeholder. This is useful for large documents, but
it breaks the old implicit scroll stability. A chunk that was loaded before a
full content replacement can become an unloaded placeholder after the
replacement. The real chunk content and its placeholder do not necessarily have
the same height. When that happens above the current viewport, the unchanged
raw scroll position starts pointing at a different part of the document.

So the old behavior was not a real scroll-preservation mechanism. It was a side
effect of stable full-DOM geometry. With chunking, geometry is no longer stable.
This feature replaces that assumption by capturing what the user was looking at
as a semantic viewport anchor and restoring it after the DOM replacement, with
lazy-load chunk support.

`toc_chunk_navigation.js` is only related as the feature that introduced and
uses lazy document chunks for explicit fragment navigation: TOC clicks, hash
changes, initial URL fragments, `:target`, and browser-visible URL state.
Content viewport restoration solves the separate scroll-stability problem:
keeping the user's current content area stable across full content frame
replacement without using the URL hash.

Both scripts use the same document chunk contract because they both sometimes
need to load a chunk before they can reach an anchor: TOC entries know the chunk
frame that contains their target via `data-chunk-frame`, and unloaded chunks are
represented by `turbo-frame.document-chunk-placeholder`.

## HOW

The chosen implementation is a separate browser script:
`strictdoc/export/html/_static/content_viewport_restoration.js`.

It is loaded on the server DOCUMENT screen. It owns scroll stability after
content replacement, while `toc_chunk_navigation.js` owns explicit hash/TOC
navigation.

The implementation is scoped to server-side Turbo Stream replacements of
`frame_document_content`. That is the current replacement path for create,
delete, move, and grammar-edit flows.

The mechanism does not use URL hash navigation. It does not change
`location.hash`, does not create browser history entries, and does not rely on
CSS `:target`.

The script listens for Turbo Stream rendering:

- on `turbo:before-stream-render`, it checks whether the stream is
  `action="replace"` for `target="frame_document_content"`;
- before Turbo performs the replacement, it captures visible
  `sdoc-anchor[id]` elements inside `[js-toc_highlighting-content_root]`;
- it stores candidates sorted by closeness to the top of the content viewport;
- after Turbo has rendered the replacement, it restores the first candidate that
  still exists or can be loaded through a lazy chunk placeholder.

The capture includes anchors that sit exactly on the viewport edge. In the DOM,
`sdoc-anchor` can have zero height, so strict rectangle intersection would miss
the top visible node when it is aligned with the top edge.

The captured data is semantic and viewport-relative:

```js
{
  candidates: [
    {
      id: "REQ-025",
      offsetTop: 120,
      distance: 120
    }
  ]
}
```

`offsetTop` is the anchor's top position relative to the content viewport, not
relative to the whole page and not a raw `scrollTop`.

When a visible create form is present, the script captures that form's
`turbo-frame` as a stronger target:

```js
{
  target: {
    type: "nodeFrame",
    frameId: "article-...",
    offsetTop: 0
  },
  candidates: [...]
}
```

The temporary create form and the final created node use the same frame id.
Restoration waits until the frame no longer contains the create form, then
scrolls the actual `sdoc-node` content back near the form's previous position.

Restoration works as follows:

- if `document.getElementById(anchorId)` exists, scroll the page so the anchor
  returns to its captured viewport-relative position;
- otherwise, find the TOC link for that anchor, read its `data-chunk-frame`,
  switch the corresponding placeholder frame from `loading="lazy"` to
  `loading="eager"`, wait for `turbo:frame-load`, and then restore the position;
- if the closest captured anchor no longer exists, try the next captured visible
  anchor.

The lazy-load wait also handles races where the chunk frame is already present
but the target anchor is not yet in the DOM. In that case, the script waits
briefly for the anchor instead of relying only on the placeholder class.

The script temporarily sets the content container's inline
`scrollBehavior = "auto"` while restoring. This avoids smooth-scroll animation
racing against chunk placeholder/content height changes. The previous inline
value is restored immediately after the jump.

Restoration first adjusts the content root's `scrollTop`. If that does not move
the target, it applies the remaining delta to `window.scrollBy()`. This keeps
the code correct for the DOCUMENT screen's actual scroll container while still
working if the content root itself is scrollable.

The script exposes the implementation through:

```js
StrictDoc.contentViewport.capture()
StrictDoc.contentViewport.restore(snapshot)
StrictDoc.contentViewport.renderManualStreamMessageWithRestore(html, snapshot)
```

This namespace is documented in `app_core.js`. It is an intentional shared
runtime contract, separate from `StrictDoc.onInsert` and the TOC/hash modules.

Most server actions go through Turbo's normal stream rendering and are handled
by the `turbo:before-stream-render` listener. TOC drag-and-drop move is
different: `draggable_list.js` sends `fetch()` manually and calls
`Turbo.renderStreamMessage(html)` through
`StrictDoc.contentViewport.renderManualStreamMessageWithRestore(html, snapshot)`.
For that path, `draggable_list.js` captures the viewport at `dragstart`, then
passes the returned streams and snapshot to the shared content viewport
restoration mechanism. The timing of "render streams, then restore after Turbo
has applied the stream actions" stays inside
`content_viewport_restoration.js`.

Important trade-offs:

- The mechanism preserves the viewed content area. It does not automatically
  define operation-specific navigation such as "always scroll to the moved
  node". If a workflow needs that behavior, it should pass an explicit operation
  target instead of relying on generic viewport preservation.
- The mechanism does not update `location.hash` and does not affect `:target`.
  That remains the responsibility of `toc_chunk_navigation.js`.
- If every captured visible anchor disappears and no fallback candidate can be
  loaded, the script does nothing. This is preferable to inventing an unrelated
  scroll target.

## Test Coverage

Direct coverage for this feature lives in:
`tests/end2end/screens/document/lazy_loading_scroll_preservation`.

Required direct scenarios:

- chunked create from a visible create form: the created node appears near the
  form's previous top position;
- chunked delete of a visible node: the top visible surviving node keeps its
  viewport-relative top position;
- chunked delete of the last node, restoring to the previous surviving node;
- chunked TOC drag-and-drop move: the top visible content node keeps its
  viewport-relative top position;
- chunked grammar-edit: the top visible content node keeps its
  viewport-relative top position;
- chunked local create/delete near the top of the current viewport;
- chunked local edit of a loaded node: the loaded chunk does not collapse back
  into a placeholder because node-local edit does not replace the whole content
  frame.

The script is also loaded for non-chunked documents. These documents do not use
lazy chunks, but the new `turbo:before-stream-render` handler must not disturb
their existing full-replace behavior. Required non-chunked counterparts:

- create;
- delete;
- move;
- grammar-edit.

Adjacent regression coverage must continue to pass:

- `tests/end2end/screens/document/lazy_loading`;
- `tests/end2end/navigation/toc/toc_click_navigation_chunked`;
- `tests/end2end/navigation/toc/toc_highlighting_lazy_chunks`;
- `tests/end2end/stable_url_links/03_web_server_chunked`.

These tests do not define content viewport restoration itself, but they protect
lazy chunk loading, TOC navigation/highlighting, and stable-link behavior that
uses the same document chunk contract.
