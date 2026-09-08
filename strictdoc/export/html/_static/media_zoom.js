// Lets a reader zoom into any image or rendered Mermaid/PlantUML diagram
// in a document. Opens a full-viewport overlay with a clone of the media;
// the initial view fits it to the viewport without enlarging it past its
// natural pixel size, and wheel/double-click let the reader zoom in
// further from there.
//
// Uses StrictDoc.onInsert (app_core.js) instead of a dedicated
// MutationObserver, so late-arriving media (async Mermaid/PlantUML
// rendering, lazily loaded document chunks) is picked up the same way as
// media present at initial parse.

(() => {

  const SEL_MEDIA = 'sdoc-autogen img, sdoc-autogen svg';
  const ZOOMABLE_ATTR = 'data-js-zoomable';
  const SEL_ZOOMABLE = '[data-js-zoomable]';

  // Initial reasonable bounds/rates, not derived from any measurement --
  // revisit by feel if wheel-zoom ever feels too fast/slow, or the zoom
  // caps feel too tight/loose.
  const MIN_SCALE = 0.1;
  const MAX_SCALE = 8;
  const WHEEL_ZOOM_SENSITIVITY = 0.0015;
  const FIT_VIEWPORT_PADDING = 32;

  /*
   * Zoomability marking.
   */

  function naturalSize(el) {
    if (el.tagName === 'IMG') {
      return el.naturalWidth
        ? { width: el.naturalWidth, height: el.naturalHeight }
        : null;
    }
    const viewBox = el.viewBox && el.viewBox.baseVal;
    return viewBox && viewBox.width
      ? { width: viewBox.width, height: viewBox.height }
      : null;
  }

  function markZoomable(el) {
    // naturalSize can fail to resolve for a broken image or an SVG
    // without a viewBox; such an element gets no affordance, since
    // openOverlay would have nothing to size the stage from.
    if (naturalSize(el)) el.setAttribute(ZOOMABLE_ATTR, '');
  }

  window.StrictDoc.onInsert(SEL_MEDIA, (el) => {
    if (el.tagName === 'IMG' && !el.complete) {
      el.addEventListener('load', () => markZoomable(el), { once: true });
      return;
    }
    markZoomable(el);
  });

  /*
   * Overlay: one at a time, built by cloning the source element. The
   * clone is a snapshot -- edits to the source or the document tree while
   * the overlay is open never need to be reflected back into it.
   */

  // Set on open, read/written by every handler below, cleared on close.
  // `overlay.isConnected` also self-heals it: modal.js's own Escape
  // handler removes the overlay element directly (see below), without
  // calling back into this module.
  let state = null;

  function getState() {
    if (state && !state.overlay.isConnected) state = null;
    return state;
  }

  function clamp(value, min, max) {
    return Math.min(max, Math.max(min, value));
  }

  function computeFitScale(natural) {
    const availableWidth = window.innerWidth - FIT_VIEWPORT_PADDING * 2;
    const availableHeight = window.innerHeight - FIT_VIEWPORT_PADDING * 2;
    // Capped at 1: "fit" never enlarges media past its natural pixel
    // size. Without the cap, a small image would open blown up to fill
    // the viewport instead of at the size it's actually stored at;
    // zooming in past that remains available via wheel/double-click.
    return Math.min(
      availableWidth / natural.width, availableHeight / natural.height, 1
    );
  }

  function applyTransform() {
    state.stage.style.transform =
      `translate(${state.translateX}px, ${state.translateY}px) ` +
      `scale(${state.scale})`;
  }

  function resetView(mode) {
    state.scale = mode === 'natural' ? 1 : computeFitScale(state.natural);
    state.translateX =
      (window.innerWidth - state.natural.width * state.scale) / 2;
    state.translateY =
      (window.innerHeight - state.natural.height * state.scale) / 2;
    applyTransform();
  }

  function closeOverlay() {
    const current = getState();
    if (!current) return;
    current.overlay.remove();
    state = null;
  }

  function openOverlay(sourceEl) {
    closeOverlay();

    const natural = naturalSize(sourceEl);
    if (!natural) return;

    // A snapshot, not the live node: unaffected by edits/removal of the
    // source while the overlay is open, and needs no teardown on close.
    const clone = sourceEl.cloneNode(true);
    // Otherwise the clone would still match SEL_ZOOMABLE, and clicking it
    // inside the overlay would open a second, nested overlay on top of
    // this one.
    clone.removeAttribute(ZOOMABLE_ATTR);
    // Keep the id: Mermaid scopes its generated styling to it (a <style>
    // element inside the SVG itself, keyed off "#mermaid-<n> .node rect"
    // and similar) -- stripping it would leave the clone's shapes
    // unstyled. A duplicate id while the overlay is open is harmless: CSS
    // id selectors match every element that has it, not just the first.
    // Mermaid/PlantUML set an inline "max-width" on the SVG root to fit
    // the page; the clone renders outside sdoc-autogen, at its own
    // explicit pixel size, so both constraints must be cleared.
    clone.style.maxWidth = 'none';
    clone.style.width = `${natural.width}px`;
    clone.style.height = `${natural.height}px`;

    const stage = document.createElement('sdoc-media-zoom-stage');
    stage.appendChild(clone);

    const overlay = document.createElement('sdoc-media-zoom');
    // Tagged data-js-modal for consistency with the rest of the modal
    // vocabulary (and to pick up modal.js's Escape handling where that
    // script is loaded), but not relied on: modal.js is only loaded on
    // the server-mode document screen, not in static exports, so Escape
    // is handled directly below regardless of whether modal.js is present.
    overlay.setAttribute('data-js-modal', '');
    overlay.appendChild(stage);

    const hint = document.createElement('sdoc-media-zoom-hint');
    // Fixed to the overlay, not the stage: must stay put while panning/
    // zooming moves the stage underneath it.
    hint.innerHTML = 'Use <kbd>Space</kbd> to pan, wheel to zoom.';
    overlay.appendChild(hint);

    overlay.addEventListener('click', (event) => {
      // Only a click landing directly on the backdrop (not bubbled up
      // from the stage/media) closes it -- clicking the zoomed content
      // itself must not.
      if (event.target === overlay) closeOverlay();
    });
    // The browser selects the word/line under the pointer on the second
    // mousedown of a double-click, before "dblclick" itself ever fires --
    // preventDefault() in the dblclick handler below is too late to stop
    // it. event.detail counts clicks in the sequence, so >1 here means
    // "this mousedown is part of a multi-click"; blocking only that case
    // leaves plain single-click-and-drag text selection untouched.
    overlay.addEventListener('mousedown', (event) => {
      if (event.detail > 1) event.preventDefault();
    });
    overlay.addEventListener('dblclick', (event) => {
      event.preventDefault();
      state.isNaturalView = !state.isNaturalView;
      resetView(state.isNaturalView ? 'natural' : 'fit');
    });
    overlay.addEventListener('wheel', handleWheel, { passive: false });

    document.getElementById('modal').replaceChildren(overlay);

    state = {
      overlay,
      stage,
      natural,
      scale: 1,
      translateX: 0,
      translateY: 0,
      isNaturalView: false,
      dragOrigin: null,
    };
    resetView('fit');
  }

  function handleWheel(event) {
    const current = getState();
    if (!current) return;
    event.preventDefault();

    const cursorX = event.clientX;
    const cursorY = event.clientY;
    // Point in the untransformed content currently under the cursor;
    // recovering the translation that keeps it under the cursor after
    // rescaling is what makes the zoom feel anchored to the pointer.
    const contentX = (cursorX - current.translateX) / current.scale;
    const contentY = (cursorY - current.translateY) / current.scale;

    const zoomFactor = Math.exp(-event.deltaY * WHEEL_ZOOM_SENSITIVITY);
    current.scale = clamp(current.scale * zoomFactor, MIN_SCALE, MAX_SCALE);
    current.translateX = cursorX - contentX * current.scale;
    current.translateY = cursorY - contentY * current.scale;
    applyTransform();
  }

  document.addEventListener('click', (event) => {
    const source = event.target.closest?.(SEL_ZOOMABLE);
    if (!source) return;
    // A click that ends a text-selection drag (mousedown, move, mouseup)
    // still fires as an ordinary "click" -- a non-empty selection at this
    // point means the user was selecting a diagram label, not asking to
    // open the viewer. A plain click (no drag) always leaves the
    // selection empty, since it collapses/clears whatever was selected
    // before, so this only ever blocks the actual selection case.
    if (window.getSelection()?.toString().length > 0) return;
    openOverlay(source);
  });

  document.addEventListener('keydown', (event) => {
    if (event.key !== 'Escape') return;
    if (!getState()) return;
    closeOverlay();
  });

  /*
   * Space-held panning, mirroring pan_with_space.js's convention: content
   * stays selectable/copyable by default, holding Space switches to
   * grab/drag, and only the drag itself suppresses selection.
   */

  document.addEventListener('keydown', (event) => {
    const current = getState();
    if (!current) return;
    if (event.key !== ' ' && event.key !== 'Spacebar') return;
    const active = document.activeElement;
    if (active?.tagName === 'INPUT' || active?.tagName === 'TEXTAREA' ||
        active?.isContentEditable) {
      return;
    }
    event.preventDefault();
    current.overlay.setAttribute('data-space-pressed', '');
  });

  document.addEventListener('keyup', (event) => {
    const current = getState();
    if (!current) return;
    if (event.key !== ' ' && event.key !== 'Spacebar') return;
    current.dragOrigin = null;
    current.overlay.removeAttribute('data-space-pressed');
    current.overlay.removeAttribute('data-dragging');
  });

  document.addEventListener('mousedown', (event) => {
    const current = getState();
    if (!current || !current.overlay.hasAttribute('data-space-pressed')) {
      return;
    }
    if (!current.overlay.contains(event.target)) return;
    event.preventDefault();
    current.dragOrigin = {
      startX: event.clientX,
      startY: event.clientY,
      startTranslateX: current.translateX,
      startTranslateY: current.translateY,
    };
    current.overlay.setAttribute('data-dragging', '');
  });

  document.addEventListener('mousemove', (event) => {
    const current = getState();
    if (!current || !current.dragOrigin) return;
    event.preventDefault();
    const origin = current.dragOrigin;
    current.translateX = origin.startTranslateX + (event.clientX - origin.startX);
    current.translateY = origin.startTranslateY + (event.clientY - origin.startY);
    applyTransform();
  });

  document.addEventListener('mouseup', () => {
    const current = getState();
    if (!current) return;
    current.dragOrigin = null;
    current.overlay.removeAttribute('data-dragging');
  });

})();
