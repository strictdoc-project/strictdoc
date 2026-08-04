// Keep the document content that the user is reading at the same viewport
// coordinate when server edits replace the content or lazy chunks change the
// page height. Save a visible node or anchor before the change, then scroll it
// back to the same place after the surrounding geometry changes.
(() => {

  const strictDoc = window.StrictDoc;
  if (!strictDoc) {
    throw new Error(
      "content_viewport_restoration.js requires app_core.js to be loaded first."
    );
  }

  // --- Configuration and viewport state ---

  // The server replaces the content frame. The controller measures the saved
  // node or anchor inside the content root and restores it there.
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
  // Count an anchor on the viewport edge as visible, even when it has no
  // height.
  const VIEWPORT_EDGE_TOLERANCE = 2;
  // Keep the saved viewport position and the watcher that detects insertion
  // for each chunk whose response has arrived but has not finished rendering.
  // The controller uses this state to correct the geometry when Turbo inserts
  // the real content and again when the placeholder's estimated height is
  // removed.
  const pendingChunkSnapshots = new WeakMap();
  // Keep pending frames iterable so their passive geometry corrections survive
  // viewport generations started by user input.
  const pendingChunkFrames = new Set();
  // Remember chunks owned by explicit navigation so passive restoration does
  // not compete with the requested destination.
  const explicitNavigationFrames = new WeakMap();
  // Associate each submitted create form with its future node, so another open
  // form cannot select the wrong node merely because it comes first in the DOM.
  const submittedCreateTargets = new WeakMap();

  // Track saved viewport positions and delayed corrections for loaded chunks.
  // Each correction records the current viewport version, called a generation.
  // If navigation, user input, or another content change starts a newer
  // generation, an older correction does nothing instead of moving the user
  // back to an obsolete position.
  const geometryLocks = new WeakMap();
  const observedGeometryElements = new Set();
  let activeViewportLock = null;
  let geometryResizeObserver = null;
  let pendingCreateTarget = null;
  let pendingDeleteBoundary = null;
  let pendingResizeLock = null;
  let generation = 0;

  // --- Measuring the content viewport ---

  // Return the scrollable content area in which the document is displayed.
  function contentRoot() {
    return document.querySelector(CONTENT_ROOT_SELECTOR);
  }

  // Return true when the element is visible inside the content viewport.
  // Count an element on the viewport edge as visible, including a zero-height
  // anchor placed exactly on that edge.
  function isInContentViewport(element, rootRect) {
    const rect = element.getBoundingClientRect();
    return (
      rect.bottom >= rootRect.top - VIEWPORT_EDGE_TOLERANCE &&
      rect.top <= rootRect.bottom + VIEWPORT_EDGE_TOLERANCE
    );
  }

  // Return true when a document node intersects the content viewport.
  function isNodeInContentViewport(node, rootRect) {
    const rect = node.getBoundingClientRect();
    return (
      rect.bottom > rootRect.top + VIEWPORT_EDGE_TOLERANCE &&
      rect.top < rootRect.bottom - VIEWPORT_EDGE_TOLERANCE
    );
  }

  // Return true only for a form that creates a requirement node.
  function isCreateRequirementForm(form) {
    return (
      form?.getAttribute("action") === CREATE_REQUIREMENT_ACTION ||
      form?.action.endsWith(CREATE_REQUIREMENT_ACTION)
    );
  }

  // Return true when the frame contains a form that creates a requirement node.
  function isPendingCreateFrame(frame) {
    return isCreateRequirementForm(frame.querySelector("form"));
  }

  // Use the sdoc-node inside the frame as the element whose position is
  // restored. If the frame has no sdoc-node, use the frame itself.
  function contentTargetForNodeFrame(frame) {
    return frame.querySelector("sdoc-node") || frame;
  }

  // Start a new viewport state. Clear the active restore position and stop
  // watching node sizes from the previous state. Delayed callbacks compare
  // their generation with this new value and stop instead of moving the
  // viewport for an operation that is no longer current.
  function advanceGeneration() {
    generation += 1;
    activeViewportLock = null;
    clearGeometryObservation();
    return generation;
  }

  // Return true only while delayed work belongs to the current viewport state.
  function isCurrentGeneration(expectedGeneration) {
    return expectedGeneration === generation;
  }

  // Stop observing nodes from the previous viewport state. Their later size
  // changes must not trigger a restore for a new document state.
  function clearGeometryObservation() {
    if (geometryResizeObserver) {
      // Stop observing each node registered for the previous viewport state.
      observedGeometryElements.forEach((element) => {
        geometryResizeObserver.unobserve(element);
      });
    }
    observedGeometryElements.clear();
    pendingResizeLock = null;
  }

  // --- Saving the visible document position ---

  // Save the submitted create form's frame id as the identity of the future
  // node. The server reuses that id for the created node, so the controller can
  // find it even if it appears inside a lazy chunk and put its top at the top
  // of the content viewport.
  function createTargetForSubmittedForm(form) {
    if (!isCreateRequirementForm(form)) return null;
    const frame = form.closest("turbo-frame[id]");
    if (!frame) return null;

    return {
      type: "nodeFrame",
      frameId: frame.id,
      offsetTop: 0,
    };
  }

  // Combine an operation-specific target, when supplied, with several visible
  // nodes and anchors saved before DOM replacement. If one visible witness
  // disappears, the controller can try another saved place.
  function captureViewportAnchor(target = null) {
    const root = contentRoot();
    if (!root) return null;

    const rootRect = root.getBoundingClientRect();

    // Store possible places for restoring the viewport after DOM replacement.
    // Each item identifies either a visible node or a visible anchor.
    // The controller can try these places if the main target is unavailable,
    // Their anchor ids can also identify a lazy chunk that may contain the
    // target.
    const candidates = [];
    const candidateAnchorIds = new Set();

    // Save every visible node that has an anchor usable as a stable identity.
    root.querySelectorAll("sdoc-node").forEach((node) => {
      if (!isNodeInContentViewport(node, rootRect)) return;
      const anchor = node.querySelector("sdoc-anchor[id]");
      if (!anchor) return;

      // Use the visible node, not only its anchor. An anchor can have no
      // height and sit above the viewport while its node still fills the
      // viewport.
      const rect = node.getBoundingClientRect();
      const containsViewportTop =
        rect.top <= rootRect.top + VIEWPORT_EDGE_TOLERANCE &&
        rect.bottom > rootRect.top + VIEWPORT_EDGE_TOLERANCE;
      candidates.push({
        type: "node",
        id: anchor.id,
        offsetTop: rect.top - rootRect.top,
        contentTop: rect.top - rootRect.top + root.scrollTop,
        distance: containsViewportTop
          ? 0
          : Math.abs(rect.top - rootRect.top),
      });
      candidateAnchorIds.add(anchor.id);
    });

    // Save visible anchors not already represented by their containing node.
    root.querySelectorAll("sdoc-anchor[id]").forEach((anchor) => {
      if (candidateAnchorIds.has(anchor.id)) return;
      if (!isInContentViewport(anchor, rootRect)) return;

      // Also save visible anchors that the first pass did not save. A node can
      // contain more than one anchor, and each anchor id can identify a place
      // to restore after the DOM is replaced.
      const rect = anchor.getBoundingClientRect();
      candidates.push({
        type: "anchor",
        id: anchor.id,
        offsetTop: rect.top - rootRect.top,
        contentTop: rect.top - rootRect.top + root.scrollTop,
        distance: Math.abs(rect.top - rootRect.top),
      });
    });

    // If there is no operation target, visible node, or anchor to save, return
    // no restore target. The caller then leaves the current scroll position
    // unchanged.
    if (!target && candidates.length === 0) return null;
    // Prefer a node that contains the viewport's top edge; otherwise try
    // witnesses in order of the distance between their top and that edge.
    candidates.sort((left, right) => left.distance - right.distance);
    return { target, candidates, scrollTop: root.scrollTop };
  }

  // --- Finding nodes, anchors, and their lazy chunks ---

  // Return the DOM element that represents a saved node or anchor candidate.
  function targetForCandidate(candidate, anchor) {
    // A node candidate represents the whole visible node. An anchor candidate
    // represents only that anchor, so restore the exact kind of target saved.
    if (candidate.type === "node") {
      return anchor.closest("sdoc-node") || anchor;
    }
    return anchor;
  }

  // Return the document node containing an anchor, or the anchor itself when
  // no containing node exists.
  function nodeTargetForAnchor(anchor) {
    return anchor.closest("sdoc-node") || anchor;
  }

  // Find the TOC link that points to a content anchor. The link tells the
  // controller which lazy chunk contains that anchor.
  function tocLinkForAnchor(anchorId) {
    const toc = document.querySelector(TOC_FRAME_SELECTOR);
    if (!toc) return null;
    return toc.querySelector(`a[anchor="${CSS.escape(anchorId)}"]`);
  }

  // Find the lazy chunk that contains the anchor whose position the controller
  // needs to restore.
  function chunkFrameForAnchor(anchorId) {
    const link = tocLinkForAnchor(anchorId);
    const item = link?.closest("li");
    const frameId = item?.getAttribute("data-chunk-frame");
    return frameId ? document.getElementById(frameId) : null;
  }

  // Find the lazy chunk that contains the node identified by frameId.
  function chunkFrameForNodeFrame(frameId) {
    const nodeId = frameId?.startsWith("article-")
      ? frameId.slice("article-".length)
      : null;
    if (!nodeId) return null;

    // Use the node IDs stored on each placeholder to find the chunk even when
    // the node content is not loaded and the node is not present in the TOC.
    const indexedFrame = contentRoot()?.querySelector(
      `turbo-frame[data-node-mids~="${CSS.escape(nodeId)}"]`
    );
    if (indexedFrame) return indexedFrame;

    // If the placeholder has no node-ID list, find the chunk through the TOC.
    const toc = document.querySelector(TOC_FRAME_SELECTOR);
    if (!toc) return null;
    const item = toc.querySelector(`li[data-nodeid="${CSS.escape(nodeId)}"]`);
    const chunkFrameId = item?.getAttribute("data-chunk-frame");
    return chunkFrameId ? document.getElementById(chunkFrameId) : null;
  }

  // --- Applying a saved position ---

  // Scroll the content so the target's top or bottom edge returns to its saved
  // distance from the top of the content viewport.
  function restoreElementEdge(target, edge, offsetTop) {
    const root = contentRoot();
    if (!root) return;

    const rootRect = root.getBoundingClientRect();
    const targetRect = target.getBoundingClientRect();
    const targetEdge = edge === "bottom" ? targetRect.bottom : targetRect.top;
    const delta = targetEdge - rootRect.top - offsetTop;
    if (Math.abs(delta) <= 1) {
      // Do nothing when the target is already at the saved place. Writing
      // scrollTop in this case would create a needless scroll event from this
      // controller.
      return;
    }

    // Put the target's top or bottom edge back at the saved place inside the
    // content root. Move scrollTop by the measured difference and disable
    // smooth scrolling so animation cannot race with changing chunk sizes.
    const previousScrollBehavior = root.style.scrollBehavior;
    root.style.scrollBehavior = "auto";

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

  // Scroll the content so the target's top edge returns to its saved distance
  // from the top of the content viewport.
  function restoreElementTop(target, offsetTop) {
    restoreElementEdge(target, "top", offsetTop);
  }

  // Move the viewport by a measured geometry delta without replacing the
  // user's current scroll position. The delta adds only space gained or lost
  // above the saved content, so wheel, keyboard, and scrollbar movement that
  // happened meanwhile remains part of scrollTop.
  function compensateScrollTopBy(delta) {
    const root = contentRoot();
    if (!root || Math.abs(delta) <= 1) return;

    const previousScrollBehavior = root.style.scrollBehavior;
    root.style.scrollBehavior = "auto";
    root.scrollTop += delta;
    root.style.scrollBehavior = previousScrollBehavior || "";
  }

  // Move every current passive lock to the geometry that exists after one
  // correction. Several chunks can change before their observers run. Once
  // one lock compensates that combined change, the other locks must start
  // from the same new document coordinates or they would apply part of the
  // change again when their own callbacks run.
  function synchronizePassiveGeometryBaselines(root, currentSnapshot) {
    const snapshots = new Set([currentSnapshot]);
    pendingChunkFrames.forEach((frame) => {
      const viewportLock = pendingChunkSnapshots.get(frame);
      if (
        viewportLock?.generation === generation &&
        !viewportLock.followsActiveViewportLock
      ) {
        snapshots.add(viewportLock.snapshot);
      }
    });
    observedGeometryElements.forEach((element) => {
      const viewportLock = geometryLocks.get(element);
      if (
        viewportLock?.generation === generation &&
        !viewportLock.followsActiveViewportLock
      ) {
        snapshots.add(viewportLock.snapshot);
      }
    });

    const rootTop = root.getBoundingClientRect().top;
    snapshots.forEach((snapshot) => {
      snapshot.candidates.forEach((candidate) => {
        const anchor = document.getElementById(candidate.id);
        if (!anchor) return;
        const target = targetForCandidate(candidate, anchor);
        candidate.contentTop =
          target.getBoundingClientRect().top - rootTop + root.scrollTop;
      });
      snapshot.scrollTop = root.scrollTop;
    });
  }

  // Measure how far the saved content moved inside the scrollable document,
  // then move scrollTop by exactly that geometry change. Coordinates inside
  // the scrollable document do not change when the user scrolls, so this does
  // not need to guess whether a simultaneous scroll event came from the user,
  // the browser, or this controller.
  function compensatePassiveGeometry(snapshot, expectedGeneration) {
    if (!snapshot || !isCurrentGeneration(expectedGeneration)) return;
    const root = contentRoot();
    if (!root) return;

    const rootTop = root.getBoundingClientRect().top;
    let geometryDelta = null;
    snapshot.candidates.forEach((candidate) => {
      const anchor = document.getElementById(candidate.id);
      if (!anchor) return;
      const target = targetForCandidate(candidate, anchor);
      const contentTop =
        target.getBoundingClientRect().top - rootTop + root.scrollTop;
      if (geometryDelta === null) {
        geometryDelta = contentTop - candidate.contentTop;
      }
    });
    if (geometryDelta === null) return;

    // When content shrinks near the end of the document, the browser may have
    // already clamped scrollTop to its new maximum. Subtract that automatic
    // movement so the controller applies only the unhandled part of the
    // geometry change.
    const automaticScrollDelta = root.scrollTop - snapshot.scrollTop;
    compensateScrollTopBy(geometryDelta - automaticScrollDelta);
    // Give every passive lock the new document geometry. Another chunk may
    // already have changed before its own observer runs; leaving its old
    // baseline would make it apply this same delta a second time.
    synchronizePassiveGeometryBaselines(root, snapshot);
  }

  // --- Waiting for a saved node or anchor to appear ---

  // The anchor whose position must be restored may be inside a lazy chunk that
  // is not loaded yet. Start loading that chunk, keep checking for the anchor,
  // and call the restore callback after the anchor appears in the DOM.
  function ensureAnchorLoaded(anchorId, callback, expectedGeneration) {
    let completed = false;

    // Stop waiting and remove the frame-load listener so later frame loads
    // do not call the restore callback again.
    function stop() {
      completed = true;
      document.removeEventListener("turbo:frame-load", onFrameLoad);
    }

    // Check whether the anchor whose position must be restored exists. Call the
    // restore callback when it appears. Stop when the viewport state is no
    // longer current.
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

    // The anchor may be inside a lazy chunk that is not loaded yet.
    // While that chunk is loading, keep checking whether the anchor has
    // appeared in the DOM.
    // Stop checking when the anchor appears, the viewport state changes, or no
    // attempts remain.
    function waitForTarget(attempts) {
      if (completed || finishIfTargetExists() || attempts === 0) {
        if (attempts === 0) stop();
        return;
      }
      // Repeat on the next browser frame to give the chunk time to add the
      // anchor, and stop after the bounded number of attempts.
      requestAnimationFrame(() => waitForTarget(attempts - 1));
    }

    // Load the anchor's chunk before restoring when the replacement left only
    // a lazy placeholder instead of the anchor.
    if (finishIfTargetExists()) {
      return;
    }

    const frame = chunkFrameForAnchor(anchorId);
    if (!frame) {
      return;
    }

    // When this chunk loads, check whether the anchor whose position we need to
    // restore is now in the DOM.
    function onFrameLoad(event) {
      if (event.target !== frame) return;
      if (!isCurrentGeneration(expectedGeneration)) {
        stop();
        return;
      }
      document.removeEventListener("turbo:frame-load", onFrameLoad);
      // Wait for the next browser frame before checking. This lets the browser
      // finish processing the DOM changes caused by the chunk load.
      requestAnimationFrame(finishIfTargetExists);
    }

    document.addEventListener("turbo:frame-load", onFrameLoad);
    if (frame.classList.contains(CHUNK_PLACEHOLDER_CLASS)) {
      frame.setAttribute("loading", "eager");
    }
    waitForTarget(60);
  }

  // The created node may be inside a lazy chunk that is not loaded yet.
  // Load the chunks that may contain the node and wait until the frame for the
  // created node appears in the DOM without a create form. Then call the
  // restore callback with the sdoc-node inside that frame, or with the frame
  // itself when it has no sdoc-node.
  function ensureNodeFrameLoaded(
    frameId,
    candidates,
    callback,
    expectedGeneration
  ) {
    let completed = false;

    // Stop waiting and remove the frame-load listener so later frame loads do
    // not call the restore callback again.
    function stop() {
      completed = true;
      document.removeEventListener("turbo:frame-load", onFrameLoad);
    }

    // Find the frame id assigned to the created node. If a frame with this id
    // still contains a create form, keep waiting. When a frame without the form
    // appears, call the restore callback with its sdoc-node or with the frame
    // itself. Stop when the viewport state is no longer current.
    function finishIfTargetExists() {
      if (!isCurrentGeneration(expectedGeneration)) {
        stop();
        return false;
      }
      const loadedTarget = document.getElementById(frameId);
      if (loadedTarget && !isPendingCreateFrame(loadedTarget)) {
        stop();
        callback(contentTargetForNodeFrame(loadedTarget));
        return true;
      }
      return false;
    }

    // The created node may be inside a lazy chunk that is not loaded yet.
    // While the possible chunks are loading, keep checking whether the frame
    // for the created node has appeared in the DOM.
    // Stop checking when the frame appears, the viewport state changes, or no
    // attempts remain.
    function waitForTarget(attempts) {
      if (completed || finishIfTargetExists() || attempts === 0) {
        if (attempts === 0) stop();
        return;
      }
      // Repeat on the next browser frame to give the chunks time to add the
      // created node, and stop after the bounded number of attempts.
      requestAnimationFrame(() => waitForTarget(attempts - 1));
    }

    // The required frame may already exist before any lazy chunk is loaded.
    // Check for it before starting additional chunk loads.
    if (finishIfTargetExists()) {
      return;
    }

    const frames = [];
    const seenFrameIds = new Set();

    // Add an unloaded placeholder once. Several saved anchors can point to the
    // same chunk, so avoid loading that frame more than once.
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
    // Add unloaded chunks that contain fallback witnesses as alternative
    // places where the created node may appear.
    candidates.forEach((candidate) => {
      addFrame(chunkFrameForAnchor(candidate.id));
    });

    // When any possible chunk finishes loading, check whether the frame for the
    // created node has appeared in the DOM.
    function onFrameLoad(event) {
      if (!frames.includes(event.target)) return;
      if (!isCurrentGeneration(expectedGeneration)) {
        stop();
        return;
      }
      // Wait for the next browser frame before checking. This lets the browser
      // finish processing the DOM changes caused by the chunk load.
      requestAnimationFrame(finishIfTargetExists);
    }

    if (frames.length > 0) {
      document.addEventListener("turbo:frame-load", onFrameLoad);
    }
    // Start loading every possible chunk immediately.
    frames.forEach((frame) => frame.setAttribute("loading", "eager"));
    waitForTarget(60);
  }

  // Restore the position after a content change.
  // After creation, put the new node at the top of the content viewport.
  // After deletion, put the next node's top, or the previous node's bottom,
  // at the top edge of the deleted node.
  // For other content replacements, restore one of the nodes or anchors
  // that was visible before the replacement.
  function restoreViewportAnchor(snapshot, expectedGeneration = generation) {
    if (!snapshot || !isCurrentGeneration(expectedGeneration)) return;

    if (snapshot.target?.type === "nodeFrame") {
      ensureNodeFrameLoaded(
        snapshot.target.frameId,
        snapshot.candidates,
        // Put the created node at the coordinate saved for the create target.
        (target) => {
          if (!isCurrentGeneration(expectedGeneration)) return;
          restoreElementTop(target, snapshot.target.offsetTop);
        },
        expectedGeneration
      );
      return;
    }

    if (snapshot.target?.type === "anchorBoundary") {
      // Put the surviving node edge at the deleted node's former boundary.
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

    // Choose the first saved witness that already exists or has a known lazy
    // chunk that can be loaded.
    const candidate = snapshot.candidates.find((item) => {
      const frame = chunkFrameForAnchor(item.id);
      return document.getElementById(item.id) || frame;
    });
    // If every node and anchor saved before the replacement has disappeared,
    // leave the current scroll position unchanged.
    if (!candidate) return;

    // Put the chosen witness back at its saved viewport coordinate.
    ensureAnchorLoaded(candidate.id, (target) => {
      if (!isCurrentGeneration(expectedGeneration)) return;
      restoreElementTop(
        targetForCandidate(candidate, target),
        candidate.offsetTop
      );
    }, expectedGeneration);
  }

  // --- Keeping the viewport stable while loaded content changes size ---

  // Watch every document node in a loaded chunk for later outer-size changes.
  // For example, an image or formula above the visible content can acquire its
  // final height later and push that content down. Compensate after layout and
  // before paint so the saved content never appears at the displaced
  // coordinate. A change below the witness produces no displacement and
  // therefore no scroll.
  function observeChunkGeometry(frame, viewportLock) {
    if (!window.ResizeObserver) return;

    if (!geometryResizeObserver) {
      // Convert all size notifications in one observer delivery into one
      // correction using the applicable current viewport lock.
      geometryResizeObserver = new ResizeObserver((entries) => {
        // Select a current lock associated with any node that changed size.
        entries.forEach((entry) => {
          const entryLock = geometryLocks.get(entry.target);
          if (entryLock?.generation === generation) {
            pendingResizeLock =
              activeViewportLock?.generation === generation
                ? activeViewportLock
                : entryLock;
          }
        });
        const viewportLockToRestore = pendingResizeLock;
        pendingResizeLock = null;
        if (!viewportLockToRestore) return;
        // ResizeObserver runs after layout but before paint. Compensate here so
        // the changed geometry is never painted at an intermediate position.
        if (viewportLockToRestore.followsActiveViewportLock) {
          restoreViewportAnchor(
            viewportLockToRestore.snapshot,
            viewportLockToRestore.generation
          );
        } else {
          compensatePassiveGeometry(
            viewportLockToRestore.snapshot,
            viewportLockToRestore.generation
          );
        }
      });
    }

    // Associate every node with the saved position to restore if that node's
    // outer size changes. Watching all nodes is necessary because any node
    // above the witness can change the amount of space before it.
    frame.querySelectorAll("sdoc-node").forEach((node) => {
      // If this node changes size, restore the saved node or anchor to the
      // saved place in the viewport.
      geometryLocks.set(node, viewportLock);
      observedGeometryElements.add(node);
      // Watch the outer box too. A padding or border change can push every node
      // below this one even when the content inside it keeps the same size.
      geometryResizeObserver.observe(node, { box: "border-box" });
    });
  }

  // --- Detecting a full document-content replacement ---

  // Return true only for the stream that replaces the complete document
  // content. Other Turbo streams do not remove the saved document nodes and
  // need no viewport capture.
  function isFullContentFrameReplace(streamElement) {
    return (
      streamElement?.tagName === "TURBO-STREAM" &&
      streamElement.getAttribute("action") === "replace" &&
      streamElement.getAttribute("target") === CONTENT_FRAME_ID
    );
  }

  // --- Remembering the result of a delete operation ---

  // Save the top of a visible node before deletion. After the server removes
  // it, the next node should take that place; if there is no next node, the
  // previous node's bottom should take it.
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
    // Find the deleted node's place in document order as represented by TOC.
    const deletedItemIndex = tocItems.findIndex(
      (item) => item.getAttribute("data-nodeid") === nodeId
    );
    if (deletedItemIndex < 0) return null;

    const nextLink = tocItems[deletedItemIndex + 1]?.querySelector("a[anchor]");
    const previousLink =
      tocItems[deletedItemIndex - 1]?.querySelector("a[anchor]");
    const nodeRect = node.getBoundingClientRect();
    const boundaryOffset = nodeRect.top - rootRect.top;

    // Keep the deleted node's top position.
    // If a next node exists, put its top at that position.
    // If the deleted node was last, put the previous node's bottom at the same
    // position.
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

  // --- Invalidating delayed work after user navigation ---

  // Mark a chunk navigation as intentional. Its response belongs to the new
  // viewport state and must not restore a position from the previous state.
  function beginExplicitNavigation(frameId) {
    pendingDeleteBoundary = null;
    const navigationGeneration = advanceGeneration();
    const frame = frameId ? document.getElementById(frameId) : null;
    if (frame) {
      explicitNavigationFrames.set(frame, navigationGeneration);
    }
    return navigationGeneration;
  }

  // Start a viewport state chosen by direct scrolling. Keep passive chunk
  // responses in the new state because their geometry changes still belong to
  // the content the user is approaching. Keep passive resize observation for
  // chunks that are already loaded, but discard operation-specific locks.
  function advanceGenerationForUserScroll() {
    generation += 1;
    const userGeneration = generation;
    activeViewportLock = null;
    pendingResizeLock = null;

    // A later resize in passively loaded content still changes geometry above
    // the reader, so carry its lock into the new user-selected viewport state.
    // Stop watching nodes owned by an explicit operation that user input has
    // cancelled.
    observedGeometryElements.forEach((element) => {
      const viewportLock = geometryLocks.get(element);
      if (viewportLock && !viewportLock.followsActiveViewportLock) {
        viewportLock.generation = userGeneration;
      } else {
        geometryResizeObserver?.unobserve(element);
        observedGeometryElements.delete(element);
      }
    });

    pendingChunkFrames.forEach((frame) => {
      const pendingSnapshot = pendingChunkSnapshots.get(frame);
      if (
        pendingSnapshot !== undefined &&
        !pendingSnapshot.followsActiveViewportLock
      ) {
        pendingSnapshot.generation = userGeneration;
      }
    });
    return userGeneration;
  }

  // When the user scrolls through a pointer, wheel, or touch input, cancel an
  // operation-specific position from the previous viewport state. Keep pending
  // passive chunks so their later height changes can still be added to the
  // user's new scroll position.
  function invalidateForUserInput(event) {
    if (!event.target.closest?.(CONTENT_ROOT_SELECTOR)) return;
    pendingDeleteBoundary = null;
    advanceGenerationForUserScroll();
  }

  // Cancel a pending delete position and delayed restores from the previous
  // viewport state. The caller handles any user-scroll timing separately.
  function invalidateViewport() {
    pendingDeleteBoundary = null;
    return advanceGeneration();
  }

  // --- Lazy chunk state helpers ---

  // Remove a chunk from the waiting list and stop watching its content after
  // it loads, fails, or receives a newer saved state.
  function clearPendingChunkSnapshot(frame) {
    const pendingSnapshot = pendingChunkSnapshots.get(frame);
    pendingChunkSnapshots.delete(frame);
    pendingChunkFrames.delete(frame);
    pendingSnapshot?.renderObserver?.disconnect();
    return pendingSnapshot;
  }

  // --- Handling delete confirmation and full document-content replacement ---

  // Remember which create form the user submitted. Several create forms can be
  // open at once, so later code must not infer the target from DOM order.
  document.addEventListener("turbo:submit-start", (event) => {
    const target = createTargetForSubmittedForm(event.target);
    if (target) {
      submittedCreateTargets.set(event.target, target);
      pendingCreateTarget = target;
    }
  });

  // Forget the form-to-target association when its request ends. If creation
  // failed, also discard the pending target because no full document
  // replacement will consume it. A successful response keeps the target until
  // its Turbo stream starts replacing the document.
  document.addEventListener("turbo:submit-end", (event) => {
    const target = submittedCreateTargets.get(event.target);
    submittedCreateTargets.delete(event.target);
    if (!event.detail.success && pendingCreateTarget === target) {
      pendingCreateTarget = null;
    }
  });

  // Before a confirmed delete, save the visible node boundary that its nearest
  // surviving neighbour must occupy after replacement.
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

  // Immediately before a full content replacement, choose the semantic
  // position that must be restored after Turbo inserts the new document DOM.
  document.addEventListener("turbo:before-stream-render", (event) => {
    if (!isFullContentFrameReplace(event.target)) return;

    // Save what the user sees immediately before Turbo replaces the document
    // content.
    // The stream replaces frame_document_content after creating or deleting a
    // node, moving a node in the TOC, or saving grammar changes.
    // For a TOC move, draggable_list.js passes the fetch response to
    // Turbo.renderStreamMessage(), which causes Turbo to dispatch this event.
    const restoreGeneration = advanceGeneration();
    const createTarget = pendingCreateTarget;
    pendingCreateTarget = null;
    const snapshot =
      pendingDeleteBoundary || captureViewportAnchor(createTarget);
    pendingDeleteBoundary = null;
    if (!snapshot) return;
    activeViewportLock = {
      generation: restoreGeneration,
      snapshot,
    };

    // Wait until Turbo's replacement task has inserted the new DOM. The old
    // DOM is still present while this event runs.
    setTimeout(() => {
      // Restore on the next browser frame, when the replacement DOM can be
      // measured.
      requestAnimationFrame(() => {
        restoreViewportAnchor(snapshot, restoreGeneration);
      });
    }, 0);
  });

  // --- Lazy chunk event handlers ---

  // When a lazy chunk response arrives, save the current semantic position and
  // watch Turbo insert the content so geometry changes above the witness do not
  // move it in the viewport.
  document.addEventListener("turbo:before-fetch-response", (event) => {
    const frame = event.target;
    if (
      !frame?.id?.startsWith("document-chunk-") ||
      !frame.classList.contains(CHUNK_PLACEHOLDER_CLASS)
    ) {
      return;
    }

    // Save the visible position when the chunk response arrives. The user may
    // scroll while the network request is in progress.
    const navigationGeneration = explicitNavigationFrames.get(frame);
    if (navigationGeneration === generation) {
      return;
    }

    const followsActiveViewportLock =
      activeViewportLock?.generation === generation;
    // A chunk loaded as part of a full content replacement must use that
    // replacement's saved position. An independent chunk load captures the
    // position that the user sees when its response arrives.
    const snapshot = followsActiveViewportLock
      ? activeViewportLock.snapshot
      : captureViewportAnchor();
    if (!snapshot) return;
    clearPendingChunkSnapshot(frame);
    const pendingSnapshot = {
      generation,
      snapshot,
      followsActiveViewportLock,
      renderObserver: null,
    };
    // As Turbo inserts chunk DOM, compensate each geometry change above the
    // saved content. The saved document coordinate stays valid even if the
    // user scrolls at the same time.
    pendingSnapshot.renderObserver = new MutationObserver(() => {
      if (!pendingSnapshot.followsActiveViewportLock) {
        compensatePassiveGeometry(
          pendingSnapshot.snapshot,
          pendingSnapshot.generation
        );
      } else {
        // Restore soon after Turbo inserts the real chunk content. Restore once
        // more at frame-load, after the placeholder loses its estimated height.
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

  // After a lazy chunk finishes loading and loses its estimated height, apply
  // the final correction and start watching the loaded nodes for later resizes.
  document.addEventListener("turbo:frame-load", (event) => {
    const frame = event.target;
    if (!frame?.id?.startsWith("document-chunk-")) return;

    const pendingSnapshot = clearPendingChunkSnapshot(frame);
    explicitNavigationFrames.delete(frame);
    if (!pendingSnapshot) return;

    if (!pendingSnapshot.followsActiveViewportLock) {
      // Add only the final geometry difference produced when the placeholder
      // loses its estimated height. Any simultaneous user movement remains in
      // scrollTop and continues in the same direction.
      compensatePassiveGeometry(
        pendingSnapshot.snapshot,
        pendingSnapshot.generation
      );
      observeChunkGeometry(frame, pendingSnapshot);
      return;
    }

    // By frame-load, the placeholder's estimated height is gone. Apply the
    // final correction for the full change from placeholder to real content.
    restoreViewportAnchor(
      pendingSnapshot.snapshot,
      pendingSnapshot.generation
    );
    observeChunkGeometry(frame, pendingSnapshot);
    // Restore once more during the next rendering update. Turbo or related
    // frame-load work may finish changing geometry after this handler, and
    // that late change must not move an operation-specific target away from
    // its saved position. New user input starts another generation and makes
    // this delayed correction a no-op.
    requestAnimationFrame(() => {
      restoreViewportAnchor(
        pendingSnapshot.snapshot,
        pendingSnapshot.generation
      );
    });
  });

  // If a lazy chunk request fails, discard its saved position and navigation
  // marker because that response can no longer change the page geometry.
  document.addEventListener("turbo:fetch-request-error", (event) => {
    const frame = event.target;
    if (!frame?.id?.startsWith("document-chunk-")) return;
    clearPendingChunkSnapshot(frame);
    explicitNavigationFrames.delete(frame);
  });

  // Record ordinary movement of the content viewport in every passive
  // geometry lock. A later chunk change compares against this latest scrollTop
  // so wheel, keyboard, touch, and scrollbar movement are not mistaken for an
  // automatic clamp caused by changing document height.
  document.addEventListener(
    "scroll",
    (event) => {
      const root = contentRoot();
      if (event.target !== root) return;

      pendingChunkFrames.forEach((frame) => {
        const viewportLock = pendingChunkSnapshots.get(frame);
        if (
          viewportLock?.generation === generation &&
          !viewportLock.followsActiveViewportLock
        ) {
          viewportLock.snapshot.scrollTop = root.scrollTop;
        }
      });
      observedGeometryElements.forEach((element) => {
        const viewportLock = geometryLocks.get(element);
        if (
          viewportLock?.generation === generation &&
          !viewportLock.followsActiveViewportLock
        ) {
          viewportLock.snapshot.scrollTop = root.scrollTop;
        }
      });
    },
    { capture: true, passive: true }
  );

  // --- User input event handlers ---

  // Give this controller sole ownership of geometry compensation in the
  // content viewport. Otherwise native scroll anchoring and the controller can
  // both react to one chunk replacement in different rendering phases. Exclude
  // the viewport's descendants because anchor exclusion applies to candidate
  // subtrees, not to the scrolling box that owns them.
  function disableNativeScrollAnchoring() {
    const style = document.createElement("style");
    style.textContent = `${CONTENT_ROOT_SELECTOR}, ${CONTENT_ROOT_SELECTOR} * { overflow-anchor: none; }`;
    document.head.append(style);
  }

  disableNativeScrollAnchoring();

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

  // Treat a scrolling key outside editable controls as direct scrolling.
  // Cancel operation-specific positions, but keep pending passive geometry
  // corrections so they can be added to the keyboard's continuing movement.
  document.addEventListener("keydown", (event) => {
    if (!SCROLL_KEYS.has(event.key)) return;
    if (event.target.matches?.("input, textarea, [contenteditable='true']")) {
      return;
    }
    pendingDeleteBoundary = null;
    advanceGenerationForUserScroll();
  });

  // --- Hooks used by other document scripts ---

  // Other document scripts use these hooks to mark intentional navigation,
  // capture a position, restore it, or move an element to a saved offset.
  strictDoc.contentViewport = strictDoc.contentViewport || {};
  strictDoc.contentViewport.beginExplicitNavigation =
    beginExplicitNavigation;
  strictDoc.contentViewport.capture = captureViewportAnchor;
  strictDoc.contentViewport.invalidate = invalidateViewport;
  strictDoc.contentViewport.restore = restoreViewportAnchor;
  strictDoc.contentViewport.scrollElementToOffset = restoreElementTop;
})();
