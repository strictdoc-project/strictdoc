// Keep the document content that the user is reading visually stable while
// lazy chunks and server operations change the document around it. A raw
// scrollTop cannot provide this guarantee: when content above the viewport
// changes height, the same scrollTop points to different document content.
//
// For ordinary reading, remember where several visible document nodes or
// anchors sit. Each saved witness records an anchor ID, the `article-<MID>`
// identity of its containing node, its position inside the viewport, and its
// coordinate inside the whole scrollable document. The node MID locates an
// unloaded lazy chunk through the chunk's complete `data-node-mids` index;
// this controller does not use TOC as a document index because valid nodes
// such as untitled TEXT may be absent from TOC.
//
// A lazy chunk changes geometry in two separate loading stages: Turbo
// inserts the real nodes, then `turbo:frame-load` removes the placeholder's
// estimated min-height. A MutationObserver compensates the insertion before an
// intermediate position can be painted; the frame-load handler compensates
// the remaining height difference. ResizeObserver continues watching the
// rendered nodes for later border-box changes caused by images, widgets, fonts,
// padding, or similar content.
//
// Passive compensation preserves the user's movement, not an old viewport
// coordinate. It measures how much the witness's document coordinate changed
// and adds only that geometry delta to the current scrollTop. Wheel, keyboard,
// touch, and scrollbar movement therefore continues while layout corrections
// are composed with it. Native scroll anchoring is disabled inside this
// viewport so the browser and this controller cannot compensate the same
// geometry change twice.
//
// Server operations that replace the full content frame either select an exact
// result or preserve the current reading position. Creation puts the node
// produced by the submitted form at the viewport top. Deletion puts the actual
// next node's top at the removed node's former top, or the previous node's
// bottom there when the last node was removed. Other replacements restore the
// first surviving witness in saved priority order. An exact target remains
// active through related lazy loads and delayed resizes until a newer viewport
// generation supersedes that active lock.
//
// Every delayed callback carries the generation in which its snapshot was
// created. Navigation, another replacement, or direct user input advances the
// generation so callbacks from an older viewport state cannot move the user
// back later. Pending passive locks follow user-scroll generations because the
// geometry they protect still has to be composed with the new reading position.
(() => {

  const strictDoc = window.StrictDoc;
  if (!strictDoc) {
    throw new Error(
      "content_viewport_restoration.js requires app_core.js to be loaded first."
    );
  }

  // --- Configuration and viewport state ---

  // The server replaces the content frame, while the content root is the
  // independently scrollable viewport whose visible document geometry must
  // remain stable.
  const CONTENT_FRAME_ID = "frame_document_content";
  const CONTENT_ROOT_SELECTOR = "[js-toc_highlighting-content_root]";
  const CHUNK_PLACEHOLDER_CLASS = "document-chunk-placeholder";
  const CREATE_REQUIREMENT_ACTION = "/actions/document/create_requirement";
  // These keys can move the content viewport when focus is not inside an
  // editable control. Their movement may continue after keydown, so they must
  // cancel exact operation positioning before the browser starts scrolling.
  const SCROLL_KEYS = new Set([
    "ArrowDown",
    "ArrowUp",
    "End",
    "Home",
    "PageDown",
    "PageUp",
    " ",
  ]);
  // Browser layout can place a zero-height anchor a fraction of a pixel across
  // the viewport edge. Treat positions within two pixels as the edge so the
  // controller does not lose an otherwise valid semantic witness to rounding.
  const VIEWPORT_EDGE_TOLERANCE = 2;
  // Keep the semantic snapshot and insertion watcher for every chunk whose
  // response has arrived but whose rendering lifecycle has not finished. The
  // same record handles two separate geometry changes: Turbo inserts the real
  // nodes, then frame-load removes the placeholder's estimated height.
  const pendingChunkSnapshots = new WeakMap();
  // WeakMap alone cannot be enumerated. Keep the same pending frames in a Set
  // so user input and one chunk's correction can update every still-relevant
  // passive snapshot. Removing a frame from this Set ends that shared work.
  const pendingChunkFrames = new Set();
  // Remember chunks loaded for an explicit TOC or fragment destination. Their
  // response must not capture the reading position and pull the viewport away
  // from the requested target; the navigation code owns their final position.
  const explicitNavigationFrames = new WeakMap();
  // Associate each submitted create form with the frame ID derived from that
  // form's `requirement_mid`. The rendered node frame uses
  // `article-<requirement_mid>` as well, so this ID identifies the result of
  // this particular submission when several create forms are open.
  const submittedCreateTargets = new WeakMap();

  // Associate loaded nodes with the passive or operation-specific position
  // that later size changes must preserve. The Set makes these WeakMap entries
  // iterable when a generation changes or all passive baselines must be
  // synchronized after one correction.
  const geometryLocks = new WeakMap();
  const observedGeometryElements = new Set();
  // An active lock is an exact position selected by a full document operation.
  // It has priority over passive reading snapshots until user input or another
  // operation starts a newer viewport state.
  let activeViewportLock = null;
  // A single ResizeObserver serves all loaded chunks; geometryLocks maps each
  // reported node back to the viewport position that its resize must protect.
  let geometryResizeObserver = null;
  // A successful create request ends before its full-replacement stream is
  // rendered, so retain the exact future-node target across that event gap.
  let pendingCreateTarget = null;
  // Delete confirmation happens before the server response. Retain the chosen
  // surviving boundary until the replacement stream captures it.
  let pendingDeleteBoundary = null;
  // ResizeObserver can report several nodes in one delivery. This temporarily
  // holds the one current lock that will compensate the combined layout pass.
  let pendingResizeLock = null;
  // Every delayed callback carries this viewport-state version. Work from an
  // older version becomes harmless instead of restoring obsolete content.
  let generation = 0;

  // --- Measuring the content viewport ---

  // Return the scrollable content area in which the document is displayed.
  function contentRoot() {
    return document.querySelector(CONTENT_ROOT_SELECTOR);
  }

  // Decide whether an element's position lies inside the content viewport and
  // can be saved as a witness coordinate. Inclusive comparisons retain a
  // zero-height anchor on either edge: the anchor itself has no visible area,
  // but its semantic ID and edge coordinate are still usable after replacement.
  function isInContentViewport(element, rootRect) {
    const rect = element.getBoundingClientRect();
    return (
      rect.bottom >= rootRect.top - VIEWPORT_EDGE_TOLERANCE &&
      rect.top <= rootRect.bottom + VIEWPORT_EDGE_TOLERANCE
    );
  }

  // Decide whether a document node has visible area inside the content
  // viewport. Unlike an anchor, a node touching only the edge is not visible
  // content, so this check requires a real overlap beyond the tolerance.
  function isNodeInContentViewport(node, rootRect) {
    const rect = node.getBoundingClientRect();
    return (
      rect.bottom > rootRect.top + VIEWPORT_EDGE_TOLERANCE &&
      rect.top < rootRect.bottom - VIEWPORT_EDGE_TOLERANCE
    );
  }

  // Distinguish a create request from other forms that can live in the same
  // Turbo frames. Only create requests give their frame ID to a future node.
  function isCreateRequirementForm(form) {
    return (
      form?.getAttribute("action") === CREATE_REQUIREMENT_ACTION ||
      form?.action.endsWith(CREATE_REQUIREMENT_ACTION)
    );
  }

  // Tell whether a frame with the future node's ID still represents the open
  // create form. The target is ready only after replacement removes that form.
  function isPendingCreateFrame(frame) {
    return isCreateRequirementForm(frame.querySelector("form"));
  }

  // Use the rendered semantic node as the visible create target. Fall back to
  // its frame so positioning still works for markup that has no sdoc-node
  // wrapper.
  function contentTargetForNodeFrame(frame) {
    return frame.querySelector("sdoc-node") || frame;
  }

  // Start a completely new viewport state for navigation or content
  // replacement. Clear the previous exact target and its resize observations.
  // Delayed callbacks retain their old generation number and become no-ops, so
  // they cannot reposition the viewport after the new state starts.
  function advanceGeneration() {
    generation += 1;
    activeViewportLock = null;
    clearGeometryObservation();
    return generation;
  }

  // Accept delayed work only while it still belongs to the current viewport
  // state. This small check is the guard used by frame-load, polling, and
  // animation-frame callbacks that may run after their initiating operation.
  function isCurrentGeneration(expectedGeneration) {
    return expectedGeneration === generation;
  }

  // Stop observing nodes owned by the previous viewport state. The DOM nodes
  // may remain and resize later, but their saved witness may describe content
  // or an operation target that the user has already left.
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

  // Turn the form that was actually submitted into an exact create target. A
  // new-form frame has ID `article-<requirement_mid>`, and the created node is
  // rendered in a frame with the same `article-<reserved_mid>` value because
  // `reserved_mid` is that submitted `requirement_mid`. Save the full frame ID
  // now so the controller can find this form's result after replacement and
  // put it at the viewport top, even when other create forms are also open.
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

  // Return the stable `article-<MID>` identity of the document node containing
  // an element. A snapshot stores this beside its anchor ID: the frame ID finds
  // the lazy chunk, while the anchor ID identifies the exact place inside the
  // rendered node.
  function nodeFrameIdForElement(element) {
    return element.closest("turbo-frame[id^='article-']")?.id || null;
  }

  // Describe the current reading position with semantic identities rather
  // than a raw scrollTop. Save an exact operation target when one exists, plus
  // several visible nodes and anchors as fallbacks for DOM replacement. Each
  // candidate records both its viewport offset, used for exact restoration,
  // and its coordinate inside the scrollable document, used to measure only
  // later geometry changes while the user continues scrolling.
  function captureViewportAnchor(target = null) {
    const root = contentRoot();
    if (!root) return null;

    const rootRect = root.getBoundingClientRect();

    // Store several possible witnesses because a server operation can remove
    // or move any one of them. Every witness uses a stable anchor ID for its
    // exact position and its containing node's frame ID for finding the lazy
    // chunk if replacement leaves that content outside the DOM.
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
        nodeFrameId: nodeFrameIdForElement(node),
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
        nodeFrameId: nodeFrameIdForElement(anchor),
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

  // Find the lazy chunk that contains the node MID encoded in an
  // `article-<MID>` frame ID. Every lazy placeholder indexes all nodes in the
  // chunk through `data-node-mids`, including TEXT nodes without titles. The
  // viewport controller therefore does not depend on TOC, which intentionally
  // represents only the subset of nodes that can appear in navigation.
  function chunkFrameForNodeFrame(frameId) {
    const nodeId = frameId?.startsWith("article-")
      ? frameId.slice("article-".length)
      : null;
    if (!nodeId) return null;

    // Use the node IDs stored on each placeholder to find the chunk even when
    // the node content is not loaded and has no navigation entry.
    return contentRoot()?.querySelector(
      `turbo-frame[data-node-mids~="${CSS.escape(nodeId)}"]`
    ) || null;
  }

  // --- Applying a saved position ---

  // Put an exact semantic edge at a requested viewport coordinate. This is for
  // operation results and explicit restoration, not passive reading during
  // scrolling: it intentionally overrides the current scroll position so a
  // created node or deletion boundary appears at the defined place.
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

    // Move by the measured error rather than assigning a document coordinate:
    // the target may have moved while surrounding chunks rendered. Disable
    // smooth scrolling because an animation would expose intermediate content
    // and chase geometry that can change again before the animation finishes.
    const previousScrollBehavior = root.style.scrollBehavior;
    root.style.scrollBehavior = "auto";

    root.scrollTop += delta;

    // Measure once more after the write. Scroll clamping, fractional layout,
    // or synchronous geometry work can prevent the first delta from reaching
    // the exact requested edge; apply only the remaining measurable error.
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

  // Add a passive geometry correction to the viewport position that exists
  // now. If content above the witness gained 200 pixels, add 200 pixels; do
  // not assign the scrollTop saved before the user moved. Wheel, keyboard,
  // touch, and scrollbar movement therefore remains intact. As with exact
  // positioning, apply the correction immediately rather than animating it.
  function compensateScrollTopBy(delta) {
    const root = contentRoot();
    if (!root || Math.abs(delta) <= 1) return;

    const previousScrollBehavior = root.style.scrollBehavior;
    root.style.scrollBehavior = "auto";
    root.scrollTop += delta;
    root.style.scrollBehavior = previousScrollBehavior || "";
  }

  // Record the post-correction document geometry in every current passive
  // lock, not only in the lock whose observer happened to run first. Two
  // chunks can both finish before either observer callback runs. The first
  // callback then measures and compensates their combined effect. If the
  // second lock kept its older baseline, its callback would interpret part of
  // that already handled movement as new and move the viewport twice.
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

  // Preserve passive reading by measuring geometry independently of user
  // movement. For a witness, `viewportTop + scrollTop` is its coordinate
  // inside the scrollable document. User scrolling changes those two terms in
  // opposite directions, leaving their sum unchanged; inserting or resizing
  // content above the witness changes the sum. Add only that change to the
  // current scrollTop, so the correction composes with simultaneous input
  // instead of pulling toward an older viewport coordinate.
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

    // The scroll listener normally keeps snapshot.scrollTop equal to the
    // user's latest position. One exception happens synchronously when content
    // shrinks near the document end: the browser must clamp scrollTop to the
    // new maximum before a scroll event can update the baseline. Subtract this
    // already applied movement from the geometry delta, or the controller
    // would compensate the same lost height a second time.
    const automaticScrollDelta = root.scrollTop - snapshot.scrollTop;
    compensateScrollTopBy(geometryDelta - automaticScrollDelta);
    // Give every passive lock the new document geometry. Another chunk may
    // already have changed before its own observer runs; leaving its old
    // baseline would make it apply this same delta a second time.
    synchronizePassiveGeometryBaselines(root, snapshot);
  }

  // --- Waiting for a saved node or anchor to appear ---

  // Make an exact anchor target available after full DOM replacement. The
  // replacement may leave only a lazy placeholder where the saved anchor used
  // to be, so eagerly load its known chunk and check for a bounded number of
  // browser frames. Stop as soon as the anchor appears or a newer generation
  // makes the requested position obsolete.
  function ensureAnchorLoaded(
    anchorId,
    nodeFrameId,
    callback,
    expectedGeneration
  ) {
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

    const frame = chunkFrameForNodeFrame(nodeFrameId);
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

  // Make an operation target available when full replacement puts its node in
  // an unloaded chunk. The target can be the result of a submitted create form
  // or the node next to a deletion. Find its chunk from the complete MID index;
  // saved visible witnesses provide additional known chunks. A create form
  // temporarily has the future node's frame ID, so accept the frame only after
  // it contains rendered node content instead.
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

    // Find the rendered node frame with the requested MID. If the same frame
    // still contains a create form, keep waiting for the replacement. Stop
    // when the node appears or a newer viewport state supersedes this target.
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

    // The requested node may be inside a lazy chunk that is not loaded yet.
    // While possible chunks load, keep checking whether its frame has appeared
    // in the DOM.
    // Stop checking when the frame appears, the viewport state changes, or no
    // attempts remain.
    function waitForTarget(attempts) {
      if (completed || finishIfTargetExists() || attempts === 0) {
        if (attempts === 0) stop();
        return;
      }
      // Repeat on the next browser frame to give the chunks time to add the
      // requested operation target, and stop after the bounded number of
      // attempts.
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
    // If direct MID lookup did not make the target appear, also load chunks
    // associated with saved witnesses. Each completed load rechecks the whole
    // DOM for frameId; a witness does not have to be the operation target.
    candidates.forEach((candidate) => {
      addFrame(chunkFrameForNodeFrame(candidate.nodeFrameId));
    });

    // When any possible chunk finishes loading, check whether the requested
    // node frame has appeared in the DOM.
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

  // Resolve an exact semantic position after full content replacement. A
  // create target puts the submitted form's resulting node at the viewport
  // top. A delete target puts the next node's top, or the previous node's
  // bottom, at the deleted node's former boundary. Other replacements try the
  // saved visible witnesses in priority order. A missing witness may require
  // loading its chunk before its viewport edge can be measured.
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

    if (snapshot.target?.type === "nodeBoundary") {
      ensureNodeFrameLoaded(
        snapshot.target.frameId,
        snapshot.candidates,
        // Put the surviving node edge at the deleted node's former boundary.
        (target) => {
          if (!isCurrentGeneration(expectedGeneration)) return;
          restoreElementEdge(
            target,
            snapshot.target.edge,
            snapshot.target.offsetTop
          );
        },
        expectedGeneration
      );
      return;
    }

    // Choose the first saved witness that already exists or has a known lazy
    // chunk that can be loaded.
    const candidate = snapshot.candidates.find((item) => {
      const frame = chunkFrameForNodeFrame(item.nodeFrameId);
      return document.getElementById(item.id) || frame;
    });
    // If every node and anchor saved before the replacement has disappeared,
    // leave the current scroll position unchanged.
    if (!candidate) return;

    // Put the chosen witness back at its saved viewport coordinate.
    ensureAnchorLoaded(
      candidate.id,
      candidate.nodeFrameId,
      (target) => {
        if (!isCurrentGeneration(expectedGeneration)) return;
        restoreElementTop(
          targetForCandidate(candidate, target),
          candidate.offsetTop
        );
      },
      expectedGeneration
    );
  }

  // --- Keeping the viewport stable while loaded content changes size ---

  // Keep protecting the viewport after Turbo declares a chunk loaded. Images,
  // formulas, fonts, or widgets inside its nodes can acquire their final size
  // later and change all geometry below them. ResizeObserver reports after
  // layout and before paint, allowing passive geometry compensation or exact
  // operation restoration before the displaced content is shown. A change
  // below the witness yields a zero witness delta and therefore no scroll.
  function observeChunkGeometry(frame, viewportLock) {
    if (!window.ResizeObserver) return;

    if (!geometryResizeObserver) {
      // One layout pass can resize several observed nodes. Use one applicable
      // current lock for the whole observer delivery so their combined effect
      // is measured once instead of issuing competing per-node corrections.
      geometryResizeObserver = new ResizeObserver((entries) => {
        // Prefer the active exact operation target when one exists; otherwise
        // use a passive lock associated with a node that changed size. Stale
        // node locks are ignored by their generation number.
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

    // Associate every rendered node with the lock current when its chunk
    // loaded. Watching every node is necessary because any one above the
    // witness can later add or remove space before the visible content.
    frame.querySelectorAll("sdoc-node").forEach((node) => {
      // The callback will use this association to choose passive additive
      // compensation or exact operation restoration for the resize.
      geometryLocks.set(node, viewportLock);
      observedGeometryElements.add(node);
      // Watch the outer box too. A padding or border change can push every node
      // below this one even when the content inside it keeps the same size.
      geometryResizeObserver.observe(node, { box: "border-box" });
    });
  }

  // --- Detecting a full document-content replacement ---

  // Recognize the one Turbo stream handled as a full document replacement.
  // Only this stream removes `frame_document_content` and therefore activates
  // the exact create/delete target or the full-replacement witness capture in
  // the listener below.
  function isFullContentFrameReplace(streamElement) {
    return (
      streamElement?.tagName === "TURBO-STREAM" &&
      streamElement.getAttribute("action") === "replace" &&
      streamElement.getAttribute("target") === CONTENT_FRAME_ID
    );
  }

  // --- Remembering the result of a delete operation ---

  // Return the MIDs of all document nodes in semantic order, including TEXT
  // nodes without titles. An unloaded lazy chunk contributes its complete
  // `data-node-mids` index. The inline first chunk and a non-chunked document
  // contribute the rendered `article-<MID>` frames in DOM order. Loaded lazy
  // frames normally retain their MID index; if one does not, its rendered node
  // frames provide the same local order.
  function nodeIdsInDocumentOrder() {
    const root = contentRoot();
    if (!root) return [];

    // Read only frames that contain a document node directly. Forms and other
    // nested Turbo frames can also have `article-` IDs but are not positions in
    // the document's semantic node sequence.
    function renderedNodeIds(container) {
      return Array.from(
        container.querySelectorAll("turbo-frame[id^='article-']")
      )
        .filter((frame) => frame.querySelector(":scope > sdoc-node"))
        .map((frame) => frame.id.slice("article-".length));
    }

    const chunkFrames = Array.from(
      root.querySelectorAll("turbo-frame[id^='document-chunk-']")
    );
    if (chunkFrames.length === 0) return renderedNodeIds(root);

    return chunkFrames.flatMap((frame) => {
      const indexedNodeIds = frame.dataset.nodeMids?.trim().split(/\s+/);
      return indexedNodeIds?.length
        ? indexedNodeIds
        : renderedNodeIds(frame);
    });
  }

  // Preserve the place from which a visible node is about to disappear. Find
  // its real neighbors in the complete document order, not in TOC: untitled
  // TEXT nodes and any other nodes omitted from TOC must behave identically.
  // After deletion, put the next node's top at the deleted node's former top.
  // If the deleted node was last, put the previous node's bottom there instead.
  function captureDeleteBoundary(nodeId) {
    const root = contentRoot();
    const frame = document.getElementById(`article-${nodeId}`);
    const node = frame?.querySelector("sdoc-node");
    if (!root || !node) return null;

    const rootRect = root.getBoundingClientRect();
    if (!isNodeInContentViewport(node, rootRect)) return null;

    const nodeIds = nodeIdsInDocumentOrder();
    const deletedNodeIndex = nodeIds.indexOf(nodeId);
    if (deletedNodeIndex < 0) return null;

    const nextNodeId = nodeIds[deletedNodeIndex + 1];
    const previousNodeId = nodeIds[deletedNodeIndex - 1];
    const nodeRect = node.getBoundingClientRect();
    const boundaryOffset = nodeRect.top - rootRect.top;

    if (nextNodeId) {
      return {
        target: {
          type: "nodeBoundary",
          frameId: `article-${nextNodeId}`,
          edge: "top",
          offsetTop: boundaryOffset,
        },
        candidates: [],
      };
    }
    if (previousNodeId) {
      return {
        target: {
          type: "nodeBoundary",
          frameId: `article-${previousNodeId}`,
          edge: "bottom",
          offsetTop: boundaryOffset,
        },
        candidates: [],
      };
    }
    return null;
  }

  // --- Invalidating delayed work after user navigation ---

  // Give an explicit TOC or fragment navigation ownership of its destination.
  // Start a new generation so older restores cannot win later, and mark the
  // destination chunk so its response is not mistaken for an ordinary passive
  // load. The navigation code, not the reading-position controller, will place
  // the requested anchor.
  function beginExplicitNavigation(frameId) {
    pendingDeleteBoundary = null;
    const navigationGeneration = advanceGeneration();
    const frame = frameId ? document.getElementById(frameId) : null;
    if (frame) {
      explicitNavigationFrames.set(frame, navigationGeneration);
    }
    return navigationGeneration;
  }

  // Start a viewport state chosen by direct user scrolling without discarding
  // passive geometry protection. Advancing the generation cancels the active
  // exact lock: keeping it would pull the viewport back against the user's
  // choice. Pending passive chunks and passive resize observations are
  // different—their future height changes still affect whatever content the
  // user is approaching—so carry those locks into the new generation.
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

  // Treat pointer, wheel, or touch interaction inside the content viewport as
  // newer user intent. Cancel an active exact lock and a delete target waiting
  // for its response, but keep passive chunks so any height they later add
  // above the reader is composed with the new user-selected position. The
  // event need not have produced a scroll yet; invalidating before browser
  // movement prevents an already scheduled exact callback from winning the
  // same interaction.
  function invalidateForUserInput(event) {
    if (!event.target.closest?.(CONTENT_ROOT_SELECTOR)) return;
    pendingDeleteBoundary = null;
    advanceGenerationForUserScroll();
  }

  // Cancel every saved position from the previous viewport state. Other
  // document scripts call this before an action whose own positioning must not
  // be followed by an older exact restore or passive geometry callback.
  function invalidateViewport() {
    pendingDeleteBoundary = null;
    return advanceGeneration();
  }

  // --- Lazy chunk state helpers ---

  // Finish or replace a chunk's pre-render lifecycle in one place. Remove it
  // from shared passive-state iteration and disconnect the MutationObserver so
  // later DOM work cannot apply the same insertion-stage correction again.
  function clearPendingChunkSnapshot(frame) {
    const pendingSnapshot = pendingChunkSnapshots.get(frame);
    pendingChunkSnapshots.delete(frame);
    pendingChunkFrames.delete(frame);
    pendingSnapshot?.renderObserver?.disconnect();
    return pendingSnapshot;
  }

  // --- Handling delete confirmation and full document-content replacement ---

  // Capture the identity of the form that actually started the create request.
  // Several forms can be open at once; choosing the first visible form would
  // associate the server response with the wrong future node.
  document.addEventListener("turbo:submit-start", (event) => {
    const target = createTargetForSubmittedForm(event.target);
    if (target) {
      submittedCreateTargets.set(event.target, target);
      pendingCreateTarget = target;
    }
  });

  // Remove the per-form association when its request ends. On failure, also
  // discard the pending exact target because no created node or replacement
  // will consume it. On success, keep the target across submit-end: the Turbo
  // stream that replaces the document is processed afterward and still needs
  // to know which node must appear at the viewport top.
  document.addEventListener("turbo:submit-end", (event) => {
    const target = submittedCreateTargets.get(event.target);
    submittedCreateTargets.delete(event.target);
    if (!event.detail.success && pendingCreateTarget === target) {
      pendingCreateTarget = null;
    }
  });

  // Before a confirmed delete, save the visible node's boundary together with
  // the MID of its actual next or previous document node. If the node is not
  // visible or its position cannot be determined, leave no special delete
  // target; full replacement will preserve an ordinary visible witness.
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

  // Immediately before Turbo removes the current document DOM, choose the one
  // semantic result that owns the replacement. A visible delete boundary has
  // priority; otherwise creation supplies an exact new-node target, and other
  // operations preserve the current reading witnesses. Capturing at this last
  // pre-render event avoids saving a position that became stale while the
  // server request was in flight.
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

  // Begin protecting the viewport when a lazy response has arrived but before
  // Turbo inserts it. Capturing at request start would be too early because the
  // user can scroll during the network wait. A frame-local MutationObserver
  // then catches insertion before the later frame-load stage removes the
  // placeholder's estimated height; both stages can independently move lower
  // content and both must be compensated.
  document.addEventListener("turbo:before-fetch-response", (event) => {
    const frame = event.target;
    if (
      !frame?.id?.startsWith("document-chunk-") ||
      !frame.classList.contains(CHUNK_PLACEHOLDER_CLASS)
    ) {
      return;
    }

    // Explicit navigation deliberately skips passive capture for its own
    // destination chunk. Saving the current reading witness here would let the
    // chunk response compete with the anchor that navigation is trying to show.
    const navigationGeneration = explicitNavigationFrames.get(frame);
    if (navigationGeneration === generation) {
      return;
    }

    const followsActiveViewportLock =
      activeViewportLock?.generation === generation;
    // A chunk loaded while a full-replacement operation target is active must
    // keep that exact target authoritative. An independent lazy load instead
    // captures passive document coordinates for the content visible at response
    // time; subsequent user scrolling changes scrollTop, not those coordinates.
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
    // Turbo can insert real nodes one paint opportunity before frame-load.
    // Correct this insertion-stage geometry in the mutation microtask so the
    // browser does not paint an intermediate jump. Passive loads add the
    // measured document delta to current scrolling; operation-owned loads put
    // their exact target back because that target, not reading motion, defines
    // the requested result.
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

  // Finish the placeholder-to-content transition at frame-load. Another script
  // has now removed the estimated min-height, which can create a second geometry
  // delta after node insertion. Correct only this remaining delta, then observe
  // the rendered nodes because images or other content can change their height
  // after the loading lifecycle itself is complete.
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
    // Measure the exact target again on the next rendering update. If its edge
    // differs from the requested coordinate after all frame-load handlers have
    // returned, correct that remaining difference. New user input starts
    // another generation and makes this delayed measurement a no-op.
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

  // Keep every passive lock's scroll baseline aligned with ordinary viewport
  // movement. The witness's document coordinate does not need rebasing when the
  // user scrolls, but snapshot.scrollTop does: a later correction uses its
  // difference from the current value to recognize the exceptional synchronous
  // clamp caused by a shorter document. Updating only passive locks avoids
  // weakening an exact operation target.
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
  // content viewport. If native scroll anchoring remains eligible, the browser
  // can move scrollTop in one rendering phase and this controller can apply the
  // same measured chunk delta in another, producing a double correction or a
  // small reverse step. Exclude both the scrolling root and every candidate
  // descendant so no native anchor remains inside this viewport. Mandatory
  // scroll-range clamping still occurs when the document becomes too short and
  // is handled separately by compensatePassiveGeometry().
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

  // Treat a scrolling key outside editable controls as direct user intent.
  // Browser keyboard scrolling can continue over several animation frames
  // after keydown. Cancel an active exact lock and a pending delete target
  // immediately, but keep passive document coordinates: later chunk deltas are
  // added to the keyboard's continuing movement instead of restoring an
  // earlier frame.
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
