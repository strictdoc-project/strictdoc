(() => {
  const strictDoc = window.StrictDoc;
  if (!strictDoc) {
    throw new Error(
      "content_viewport_restoration.js requires app_core.js to be loaded first."
    );
  }

  const CONTENT_FRAME_ID = "frame_document_content";
  const CONTENT_ROOT_SELECTOR = "[js-toc_highlighting-content_root]";
  const TOC_FRAME_SELECTOR = "turbo-frame#frame-toc";
  const CHUNK_PLACEHOLDER_CLASS = "document-chunk-placeholder";
  const CREATE_REQUIREMENT_ACTION = "/actions/document/create_requirement";
  const SCROLL_KEYS = new Set([
    "ArrowDown",
    "ArrowUp",
    "End",
    "Home",
    "PageDown",
    "PageUp",
    " ",
  ]);
  // A frame load immediately following real scrolling still belongs to that
  // continuous user gesture. Exact semantic restoration during this window
  // would use a snapshot from the preceding scroll frame and cause a small
  // step opposite to the user's direction.
  const ACTIVE_SCROLL_WINDOW_MS = 120;
  // sdoc-anchor can be zero-height. Keep edge-aligned anchors visible.
  const VIEWPORT_EDGE_TOLERANCE = 2;
  const pendingChunkSnapshots = new WeakMap();
  const pendingChunkFrames = new Set();
  const explicitNavigationFrames = new WeakMap();
  const geometryLocks = new WeakMap();
  const observedGeometryElements = new Set();
  let activeViewportLock = null;
  let geometryResizeObserver = null;
  let pendingDeleteBoundary = null;
  let pendingResizeLock = null;
  let resizeRestoreScheduled = false;
  let controlledScrollActive = false;
  let controlledScrollToken = 0;
  let generation = 0;
  let userScrollActiveUntil = Number.NEGATIVE_INFINITY;

  function contentRoot() {
    return document.querySelector(CONTENT_ROOT_SELECTOR);
  }

  function isInContentViewport(element, rootRect) {
    const rect = element.getBoundingClientRect();
    return (
      rect.bottom >= rootRect.top - VIEWPORT_EDGE_TOLERANCE &&
      rect.top <= rootRect.bottom + VIEWPORT_EDGE_TOLERANCE
    );
  }

  function isNodeInContentViewport(node, rootRect) {
    const rect = node.getBoundingClientRect();
    return (
      rect.bottom > rootRect.top + VIEWPORT_EDGE_TOLERANCE &&
      rect.top < rootRect.bottom - VIEWPORT_EDGE_TOLERANCE
    );
  }

  function isCreateRequirementForm(form) {
    return (
      form?.getAttribute("action") === CREATE_REQUIREMENT_ACTION ||
      form?.action.endsWith(CREATE_REQUIREMENT_ACTION)
    );
  }

  function isPendingCreateFrame(frame) {
    return isCreateRequirementForm(frame.querySelector("form"));
  }

  function contentTargetForNodeFrame(frame) {
    return frame.querySelector("sdoc-node") || frame;
  }

  function advanceGeneration() {
    generation += 1;
    activeViewportLock = null;
    clearGeometryObservation();
    return generation;
  }

  function isCurrentGeneration(expectedGeneration) {
    return expectedGeneration === generation;
  }

  function clearGeometryObservation() {
    if (geometryResizeObserver) {
      observedGeometryElements.forEach((element) => {
        geometryResizeObserver.unobserve(element);
      });
    }
    observedGeometryElements.clear();
    pendingResizeLock = null;
  }

  function captureVisibleCreateForm(rootRect) {
    const form = Array.from(document.querySelectorAll("sdoc-form form")).find(
      isCreateRequirementForm
    );
    if (!form || !isInContentViewport(form, rootRect)) return null;

    const frame = form.closest("turbo-frame[id]");
    if (!frame) return null;

    // For create, identify the submitted form by its frame: that frame becomes
    // the created node. Capture the inner form's top, because
    // scroll_into_view.js scrolls that element and its CSS scroll-margin
    // defines the visible form position.
    const rect = form.getBoundingClientRect();
    return {
      type: "nodeFrame",
      frameId: frame.id,
      offsetTop: rect.top - rootRect.top,
    };
  }

  function captureViewportAnchor() {
    const root = contentRoot();
    if (!root) return null;

    const rootRect = root.getBoundingClientRect();
    const target = captureVisibleCreateForm(rootRect);
    const candidates = [];
    const candidateAnchorIds = new Set();

    root.querySelectorAll("sdoc-node").forEach((node) => {
      if (!isNodeInContentViewport(node, rootRect)) return;
      const anchor = node.querySelector("sdoc-anchor[id]");
      if (!anchor) return;

      const rect = node.getBoundingClientRect();
      const containsViewportTop =
        rect.top <= rootRect.top + VIEWPORT_EDGE_TOLERANCE &&
        rect.bottom > rootRect.top + VIEWPORT_EDGE_TOLERANCE;
      candidates.push({
        type: "node",
        id: anchor.id,
        offsetTop: rect.top - rootRect.top,
        distance: containsViewportTop
          ? 0
          : Math.abs(rect.top - rootRect.top),
      });
      candidateAnchorIds.add(anchor.id);
    });

    root.querySelectorAll("sdoc-anchor[id]").forEach((anchor) => {
      if (candidateAnchorIds.has(anchor.id)) return;
      if (!isInContentViewport(anchor, rootRect)) return;
      const rect = anchor.getBoundingClientRect();
      candidates.push({
        type: "anchor",
        id: anchor.id,
        offsetTop: rect.top - rootRect.top,
        distance: Math.abs(rect.top - rootRect.top),
      });
    });

    if (!target && candidates.length === 0) return null;
    candidates.sort((left, right) => left.distance - right.distance);
    return { target, candidates };
  }

  function targetForCandidate(candidate, anchor) {
    if (candidate.type === "node") {
      return anchor.closest("sdoc-node") || anchor;
    }
    return anchor;
  }

  function nodeTargetForAnchor(anchor) {
    return anchor.closest("sdoc-node") || anchor;
  }

  function tocLinkForAnchor(anchorId) {
    const toc = document.querySelector(TOC_FRAME_SELECTOR);
    if (!toc) return null;
    return toc.querySelector(`a[anchor="${CSS.escape(anchorId)}"]`);
  }

  function chunkFrameForAnchor(anchorId) {
    const link = tocLinkForAnchor(anchorId);
    const item = link?.closest("li");
    const frameId = item?.getAttribute("data-chunk-frame");
    return frameId ? document.getElementById(frameId) : null;
  }

  function chunkFrameForNodeFrame(frameId) {
    const nodeId = frameId?.startsWith("article-")
      ? frameId.slice("article-".length)
      : null;
    if (!nodeId) return null;

    // A created node can be several chunks away from its visible form. TEXT
    // and custom grammar elements may also be absent from TOC, so operation
    // target resolution must use the complete placeholder MID index first.
    const indexedFrame = contentRoot()?.querySelector(
      `turbo-frame[data-node-mids~="${CSS.escape(nodeId)}"]`
    );
    if (indexedFrame) return indexedFrame;

    // Compatibility fallback for content rendered without the chunk index.
    const toc = document.querySelector(TOC_FRAME_SELECTOR);
    if (!toc) return null;
    const item = toc.querySelector(`li[data-nodeid="${CSS.escape(nodeId)}"]`);
    const chunkFrameId = item?.getAttribute("data-chunk-frame");
    return chunkFrameId ? document.getElementById(chunkFrameId) : null;
  }

  function restoreElementEdge(target, edge, offsetTop) {
    const root = contentRoot();
    if (!root) return;

    const rootRect = root.getBoundingClientRect();
    const targetRect = target.getBoundingClientRect();
    const targetEdge = edge === "bottom" ? targetRect.bottom : targetRect.top;
    const delta = targetEdge - rootRect.top - offsetTop;
    if (Math.abs(delta) <= 1) {
      // Geometry inserted below the viewport normally leaves the visible
      // anchor untouched. In that case the browser already has the correct
      // scroll position: do not write scrollTop and do not mark a synthetic
      // controlled-scroll session. The same measured no-op also covers any
      // other DOM change that did not actually displace the semantic witness.
      return;
    }

    const previousScrollBehavior = root.style.scrollBehavior;
    root.style.scrollBehavior = "auto";
    controlledScrollActive = true;
    controlledScrollToken += 1;
    const currentControlledScrollToken = controlledScrollToken;
    requestAnimationFrame(() => {
      if (currentControlledScrollToken === controlledScrollToken) {
        controlledScrollActive = false;
      }
    });

    root.scrollTop += delta;

    const updatedTargetRect = target.getBoundingClientRect();
    const updatedTargetEdge =
      edge === "bottom" ? updatedTargetRect.bottom : updatedTargetRect.top;
    const remainingDelta =
      updatedTargetEdge - root.getBoundingClientRect().top - offsetTop;
    if (Math.abs(remainingDelta) > 1) {
      root.scrollTop += remainingDelta;
    }

    root.style.scrollBehavior = previousScrollBehavior || "";
  }

  function restoreElementTop(target, offsetTop) {
    restoreElementEdge(target, "top", offsetTop);
  }

  function ensureAnchorLoaded(anchorId, callback, expectedGeneration) {
    let completed = false;

    function stop() {
      completed = true;
      document.removeEventListener("turbo:frame-load", onFrameLoad);
    }

    function finishIfTargetExists() {
      if (!isCurrentGeneration(expectedGeneration)) {
        stop();
        return false;
      }
      const loadedTarget = document.getElementById(anchorId);
      if (loadedTarget) {
        stop();
        callback(loadedTarget);
        return true;
      }
      return false;
    }

    function waitForTarget(attempts) {
      if (completed || finishIfTargetExists() || attempts === 0) {
        if (attempts === 0) stop();
        return;
      }
      requestAnimationFrame(() => waitForTarget(attempts - 1));
    }

    if (finishIfTargetExists()) {
      return;
    }

    const frame = chunkFrameForAnchor(anchorId);
    if (!frame) {
      return;
    }

    function onFrameLoad(event) {
      if (event.target !== frame) return;
      if (!isCurrentGeneration(expectedGeneration)) {
        stop();
        return;
      }
      document.removeEventListener("turbo:frame-load", onFrameLoad);
      requestAnimationFrame(finishIfTargetExists);
    }

    document.addEventListener("turbo:frame-load", onFrameLoad);
    if (frame.classList.contains(CHUNK_PLACEHOLDER_CLASS)) {
      frame.setAttribute("loading", "eager");
    }
    waitForTarget(60);
  }

  function ensureNodeFrameLoaded(
    frameId,
    candidates,
    callback,
    expectedGeneration
  ) {
    let completed = false;

    function stop() {
      completed = true;
      document.removeEventListener("turbo:frame-load", onFrameLoad);
    }

    function finishIfTargetExists() {
      if (!isCurrentGeneration(expectedGeneration)) {
        stop();
        return false;
      }
      const loadedTarget = document.getElementById(frameId);
      // The same frame first contains the create form, then the created node.
      if (loadedTarget && !isPendingCreateFrame(loadedTarget)) {
        stop();
        callback(contentTargetForNodeFrame(loadedTarget));
        return true;
      }
      return false;
    }

    function waitForTarget(attempts) {
      if (completed || finishIfTargetExists() || attempts === 0) {
        if (attempts === 0) stop();
        return;
      }
      requestAnimationFrame(() => waitForTarget(attempts - 1));
    }

    if (finishIfTargetExists()) {
      return;
    }

    const frames = [];
    const seenFrameIds = new Set();

    function addFrame(frame) {
      if (
        !frame ||
        !frame.classList.contains(CHUNK_PLACEHOLDER_CLASS) ||
        seenFrameIds.has(frame.id)
      ) {
        return;
      }
      seenFrameIds.add(frame.id);
      frames.push(frame);
    }

    addFrame(chunkFrameForNodeFrame(frameId));
    candidates.forEach((candidate) => {
      addFrame(chunkFrameForAnchor(candidate.id));
    });

    function onFrameLoad(event) {
      if (!frames.includes(event.target)) return;
      if (!isCurrentGeneration(expectedGeneration)) {
        stop();
        return;
      }
      requestAnimationFrame(finishIfTargetExists);
    }

    if (frames.length > 0) {
      document.addEventListener("turbo:frame-load", onFrameLoad);
    }
    frames.forEach((frame) => frame.setAttribute("loading", "eager"));
    waitForTarget(60);
  }

  function restoreViewportAnchor(snapshot, expectedGeneration = generation) {
    if (!snapshot || !isCurrentGeneration(expectedGeneration)) return;

    if (snapshot.target?.type === "nodeFrame") {
      ensureNodeFrameLoaded(
        snapshot.target.frameId,
        snapshot.candidates,
        (target) => {
          if (!isCurrentGeneration(expectedGeneration)) return;
          restoreElementTop(target, snapshot.target.offsetTop);
        },
        expectedGeneration
      );
      return;
    }

    if (snapshot.target?.type === "anchorBoundary") {
      ensureAnchorLoaded(snapshot.target.id, (target) => {
        if (!isCurrentGeneration(expectedGeneration)) return;
        restoreElementEdge(
          nodeTargetForAnchor(target),
          snapshot.target.edge,
          snapshot.target.offsetTop
        );
      }, expectedGeneration);
      return;
    }

    const candidate = snapshot.candidates.find((item) => {
      const frame = chunkFrameForAnchor(item.id);
      return document.getElementById(item.id) || frame;
    });
    if (!candidate) return;

    ensureAnchorLoaded(candidate.id, (target) => {
      if (!isCurrentGeneration(expectedGeneration)) return;
      restoreElementTop(
        targetForCandidate(candidate, target),
        candidate.offsetTop
      );
    }, expectedGeneration);
  }

  function observeChunkGeometry(frame, viewportLock) {
    if (!window.ResizeObserver) return;

    if (!geometryResizeObserver) {
      geometryResizeObserver = new ResizeObserver((entries) => {
        entries.forEach((entry) => {
          const entryLock = geometryLocks.get(entry.target);
          if (entryLock?.generation === generation) {
            pendingResizeLock =
              activeViewportLock?.generation === generation
                ? activeViewportLock
                : entryLock;
          }
        });
        if (!pendingResizeLock || resizeRestoreScheduled) return;

        resizeRestoreScheduled = true;
        requestAnimationFrame(() => {
          resizeRestoreScheduled = false;
          const viewportLockToRestore = pendingResizeLock;
          pendingResizeLock = null;
          if (!viewportLockToRestore) return;
          restoreViewportAnchor(
            viewportLockToRestore.snapshot,
            viewportLockToRestore.generation
          );
        });
      });
    }

    frame.querySelectorAll("sdoc-node").forEach((node) => {
      geometryLocks.set(node, viewportLock);
      observedGeometryElements.add(node);
      // Viewport geometry follows the node's outer layout box. Content-box
      // observation misses padding and border changes even though they move
      // every semantic witness below the node.
      geometryResizeObserver.observe(node, { box: "border-box" });
    });
  }

  function isFullContentFrameReplace(streamElement) {
    return (
      streamElement?.tagName === "TURBO-STREAM" &&
      streamElement.getAttribute("action") === "replace" &&
      streamElement.getAttribute("target") === CONTENT_FRAME_ID
    );
  }

  function captureDeleteBoundary(nodeId) {
    const root = contentRoot();
    const frame = document.getElementById(`article-${nodeId}`);
    const node = frame?.querySelector("sdoc-node");
    if (!root || !node) return null;

    const rootRect = root.getBoundingClientRect();
    if (!isNodeInContentViewport(node, rootRect)) return null;

    const toc = document.querySelector(TOC_FRAME_SELECTOR);
    if (!toc) return null;
    const tocItems = Array.from(toc.querySelectorAll("li[data-nodeid]"));
    const deletedItemIndex = tocItems.findIndex(
      (item) => item.getAttribute("data-nodeid") === nodeId
    );
    if (deletedItemIndex < 0) return null;

    const nextLink = tocItems[deletedItemIndex + 1]?.querySelector("a[anchor]");
    const previousLink =
      tocItems[deletedItemIndex - 1]?.querySelector("a[anchor]");
    const nodeRect = node.getBoundingClientRect();
    const boundaryOffset = nodeRect.top - rootRect.top;

    if (nextLink) {
      return {
        target: {
          type: "anchorBoundary",
          id: nextLink.getAttribute("anchor"),
          edge: "top",
          offsetTop: boundaryOffset,
        },
        candidates: [],
      };
    }
    if (previousLink) {
      return {
        target: {
          type: "anchorBoundary",
          id: previousLink.getAttribute("anchor"),
          edge: "bottom",
          offsetTop: boundaryOffset,
        },
        candidates: [],
      };
    }
    return null;
  }

  document.addEventListener("click", (event) => {
    const confirmLink = event.target.closest?.(
      "a[data-testid='confirm-action']"
    );
    if (!confirmLink) return;

    const actionUrl = new URL(confirmLink.href, document.baseURI);
    if (!actionUrl.pathname.endsWith("/delete_requirement")) return;
    const nodeId = actionUrl.searchParams.get("node_id");
    pendingDeleteBoundary = nodeId
      ? captureDeleteBoundary(nodeId)
      : null;
  });

  document.addEventListener("turbo:before-stream-render", (event) => {
    if (!isFullContentFrameReplace(event.target)) return;

    const restoreGeneration = advanceGeneration();
    const snapshot =
      pendingDeleteBoundary || captureViewportAnchor();
    pendingDeleteBoundary = null;
    if (!snapshot) return;
    activeViewportLock = {
      generation: restoreGeneration,
      snapshot,
    };

    // Turbo performs the stream action after this event on the next frame.
    // Restore in the following task, after the replacement DOM is present.
    setTimeout(() => {
      requestAnimationFrame(() => {
        restoreViewportAnchor(snapshot, restoreGeneration);
      });
    }, 0);
  });

  document.addEventListener("turbo:before-fetch-response", (event) => {
    const frame = event.target;
    if (
      !frame?.id?.startsWith("document-chunk-") ||
      !frame.classList.contains(CHUNK_PLACEHOLDER_CLASS)
    ) {
      return;
    }

    const navigationGeneration = explicitNavigationFrames.get(frame);
    if (navigationGeneration === generation) {
      return;
    }

    const followsActiveViewportLock =
      activeViewportLock?.generation === generation;
    const snapshot = followsActiveViewportLock
      ? activeViewportLock.snapshot
      : captureViewportAnchor();
    if (!snapshot) return;
    clearPendingChunkSnapshot(frame);
    const pendingSnapshot = {
      generation,
      snapshot,
      followsActiveViewportLock,
      renderStarted: false,
      renderObserver: null,
    };
    pendingSnapshot.renderObserver = new MutationObserver(() => {
      pendingSnapshot.renderStarted = true;
      if (!passiveUserScrollIsActive(pendingSnapshot)) {
        // Turbo can insert the real chunk DOM one paint opportunity before it
        // emits turbo:frame-load. Restore in the mutation microtask so the
        // placeholder-to-content height delta never reaches a painted frame.
        // frame-load still performs the final correction after the placeholder
        // class and its estimated min-height have been removed.
        restoreViewportAnchor(
          pendingSnapshot.snapshot,
          pendingSnapshot.generation
        );
      }
    });
    pendingSnapshot.renderObserver.observe(frame, {
      childList: true,
      subtree: true,
    });
    pendingChunkSnapshots.set(frame, pendingSnapshot);
    pendingChunkFrames.add(frame);
  });

  function clearPendingChunkSnapshot(frame) {
    const pendingSnapshot = pendingChunkSnapshots.get(frame);
    pendingChunkSnapshots.delete(frame);
    pendingChunkFrames.delete(frame);
    pendingSnapshot?.renderObserver?.disconnect();
    return pendingSnapshot;
  }

  function passiveUserScrollIsActive(pendingSnapshot) {
    return (
      !pendingSnapshot.followsActiveViewportLock &&
      performance.now() <= userScrollActiveUntil
    );
  }

  document.addEventListener("turbo:frame-load", (event) => {
    const frame = event.target;
    if (!frame?.id?.startsWith("document-chunk-")) return;

    const pendingSnapshot = clearPendingChunkSnapshot(frame);
    explicitNavigationFrames.delete(frame);
    if (!pendingSnapshot) return;

    if (passiveUserScrollIsActive(pendingSnapshot)) {
      // A snapshot is always one scroll frame behind an actively moving
      // viewport. Exact restoration here creates a small step opposite to the
      // user's direction. Let native scroll anchoring own this frame instead.
      // Operation-specific locks remain exact even during user input.
      return;
    }

    restoreViewportAnchor(
      pendingSnapshot.snapshot,
      pendingSnapshot.generation
    );
    observeChunkGeometry(frame, pendingSnapshot);
  });

  document.addEventListener("turbo:fetch-request-error", (event) => {
    const frame = event.target;
    if (!frame?.id?.startsWith("document-chunk-")) return;
    clearPendingChunkSnapshot(frame);
    explicitNavigationFrames.delete(frame);
  });

  document.addEventListener(
    "scroll",
    (event) => {
      const root = contentRoot();
      if (event.target !== root) return;
      if (
        !controlledScrollActive &&
        performance.now() <= userScrollActiveUntil
      ) {
        // Only a session started by wheel/touch/pointer/key input may be
        // extended here. Scroll events caused by layout or by this controller
        // must never impersonate user intent.
        userScrollActiveUntil =
          performance.now() + ACTIVE_SCROLL_WINDOW_MS;
      }
      if (
        pendingChunkFrames.size === 0 ||
        performance.now() > userScrollActiveUntil
      ) {
        return;
      }

      const pendingSnapshotsToRebase = [];
      pendingChunkFrames.forEach((frame) => {
        const pendingSnapshot = pendingChunkSnapshots.get(frame);
        if (
          pendingSnapshot !== undefined &&
          pendingSnapshot.generation === generation &&
          !pendingSnapshot.followsActiveViewportLock &&
          !pendingSnapshot.renderStarted
        ) {
          pendingSnapshotsToRebase.push(pendingSnapshot);
        }
      });
      if (pendingSnapshotsToRebase.length === 0) {
        // User input invalidates the previous generation immediately, while
        // its already-started frame requests may remain pending until their
        // frame-load events arrive. Reject those cheap state-only candidates
        // before captureViewportAnchor scans and measures every loaded node
        // and anchor on this scroll event.
        return;
      }

      const latestSnapshot = captureViewportAnchor();
      if (!latestSnapshot) return;

      pendingSnapshotsToRebase.forEach((pendingSnapshot) => {
        // Keep passive reading position current while the viewport is still
        // moving between response arrival and the actual frame mutation.
        // Once rendering starts, the observer freezes the last user position
        // so layout-induced scroll events cannot redefine the witness.
        pendingSnapshot.snapshot = latestSnapshot;
      });
    },
    {
      capture: true,
      passive: true,
    }
  );

  function beginExplicitNavigation(frameId) {
    pendingDeleteBoundary = null;
    const navigationGeneration = advanceGeneration();
    const frame = frameId ? document.getElementById(frameId) : null;
    if (frame) {
      explicitNavigationFrames.set(frame, navigationGeneration);
    }
    return navigationGeneration;
  }

  function invalidateForUserInput(event) {
    if (!event.target.closest?.(CONTENT_ROOT_SELECTOR)) return;
    userScrollActiveUntil = performance.now() + ACTIVE_SCROLL_WINDOW_MS;
    pendingDeleteBoundary = null;
    advanceGeneration();
  }

  function invalidateViewport() {
    pendingDeleteBoundary = null;
    return advanceGeneration();
  }

  document.addEventListener("wheel", invalidateForUserInput, {
    capture: true,
    passive: true,
  });
  document.addEventListener("touchstart", invalidateForUserInput, {
    capture: true,
    passive: true,
  });
  document.addEventListener("pointerdown", invalidateForUserInput, {
    capture: true,
    passive: true,
  });
  document.addEventListener("keydown", (event) => {
    if (!SCROLL_KEYS.has(event.key)) return;
    if (event.target.matches?.("input, textarea, [contenteditable='true']")) {
      return;
    }
    userScrollActiveUntil = performance.now() + ACTIVE_SCROLL_WINDOW_MS;
    invalidateViewport();
  });

  strictDoc.contentViewport = strictDoc.contentViewport || {};
  strictDoc.contentViewport.beginExplicitNavigation =
    beginExplicitNavigation;
  strictDoc.contentViewport.capture = captureViewportAnchor;
  strictDoc.contentViewport.invalidate = invalidateViewport;
  strictDoc.contentViewport.restore = restoreViewportAnchor;
  strictDoc.contentViewport.scrollElementToOffset = restoreElementTop;
})();
