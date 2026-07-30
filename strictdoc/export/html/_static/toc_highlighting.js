// TOC highlighting: map content <sdoc-anchor id> to TOC <a anchor>
// and toggle TOC states using IntersectionObserver.

(function () {
const strictDoc = window.StrictDoc;
if (!strictDoc || !strictDoc.events || !strictDoc.bus) {
  throw new Error('toc_highlighting.js requires app_core.js to be loaded first.');
}

const TOC_HIGHLIGHT_DEBUG = false;

const TOC_FRAME_SELECTOR = 'turbo-frame#frame-toc'; // updating
const TOC_LIST_SELECTOR = 'ul#toc';
const TOC_ELEMENT_SELECTOR = 'a';
const CONTENT_FRAME_SELECTOR = '[js-toc_highlighting-content_root]'; // stable container, never itself replaced by turbo
const CONTENT_ELEMENT_SELECTOR = 'sdoc-anchor';
const CONTENT_SCROLL_CONTAINER_SELECTOR = '.main';
const TOC_STATE_CHANGED_EVENT = strictDoc.events.TOC_STATE_CHANGED;
const TOC_FRAGMENT_RESOLVED_EVENT = strictDoc.events.TOC_FRAGMENT_RESOLVED;

// Virtual viewport for TOC section highlighting.
//
// `.main`, rather than `window`, owns document scrolling. Its top and bottom
// edges therefore define the real content viewport. The extra top inset closes
// the previous section shortly after its boundary crosses the visible edge,
// matching what users perceive as the current section.
//
// In the standard layout `.main` starts 48px below the window and ends 32px
// above its bottom. The historical window-relative bounds 64px..height-32px
// were consequently equivalent to `.main` plus this 16px top inset. Express
// that geometry directly so highlighting continues to follow `.main` if the
// surrounding header or footer layout changes.
const HIGHLIGHT_VIEWPORT_TOP_INSET_PX = 16;
const HIGHLIGHT_VIEWPORT_BOTTOM_INSET_PX = 0;

// * Runtime state;
// * anchorsCount/anchorsSig skip unnecessary re-observe on TOC mutations.
let tocHighlightingState = {
  data: {},
  links: null,
  anchors: null,
  anchorsCount: -1,
  anchorsSig: 0,
  contentFrameTop: undefined,
  contentFrameEl: null,
  linkedAnchors: [],
  visibleLinks: new Set(),
  closerForFolder: {},
  folderSet: new Set(),
};
let tocRefreshRaf = null;
let anchorUpdateRaf = null;
const pendingInsertedAnchors = new Set();

function resetState() {
  // * Keep anchorsCount/anchorsSig to detect changes across TOC mutations.
  tocHighlightingState.data = {};
  tocHighlightingState.links = null;
  tocHighlightingState.anchors = null;
  tocHighlightingState.contentFrameEl = null;
  tocHighlightingState.linkedAnchors = [];
  tocHighlightingState.visibleLinks = new Set();
  tocHighlightingState.closerForFolder = {};
  tocHighlightingState.folderSet = new Set();
}

window.addEventListener("hashchange", handleHashChange);
window.addEventListener("load",function(){

  // * Frames are stable and we define them once.
  const tocFrame = document.querySelector(TOC_FRAME_SELECTOR);
  const tocList = tocFrame ? tocFrame.querySelector(TOC_LIST_SELECTOR) : null;
  const contentFrame = document.querySelector(CONTENT_FRAME_SELECTOR);
  // Document view marks `.main` itself as the content root; table view marks
  // a descendant. closest() resolves the actual scroll owner in both cases.
  const scrollContainer = contentFrame
    ? contentFrame.closest(CONTENT_SCROLL_CONTAINER_SELECTOR)
    : null;

  if (!tocFrame || !contentFrame || !scrollContainer) { return }

  const anchorObserver = new IntersectionObserver(
    handleIntersect,
    {
      root: scrollContainer,
      rootMargin: "0px",
    });

  // * On TOC updates, rebuild mappings;
  // * processAnchorList decides whether to re‑observe anchors.
  const mutatingFrame = tocFrame;
  new MutationObserver(function (mutationsList, observer) {
    // * Use requestAnimationFrame to put highlightTOC
    // * at the end of the event queue and to ensure
    // * the code runs after all DOM changes have been applied.
    requestAnimationFrame(() => {
      highlightTOC(tocFrame, contentFrame, anchorObserver);
    })
  }).observe(
    mutatingFrame,
    {
      // * We're looking at an updatable frame (mutates its contents,
      // * and we don't care what mutations were made inside):
      childList: true,
      // attributes: true,
      // characterData: true,
      // subtree: true
    }
  );

  // * First init only if TOC already has items; otherwise MO will trigger later.
  if (tocList && tocList.querySelector(TOC_ELEMENT_SELECTOR)) {
    highlightTOC(tocFrame, contentFrame, anchorObserver);
  }

  // * Content can also change without the TOC frame mutating - e.g. a
  // * lazily-loaded document chunk inserting nodes whose anchors were not
  // * present at initial load. The TOC frame observer above does not see
  // * this case (see toc_highlighting.js task notes), so inserted anchors are
  // * registered via StrictDoc.onInsert, instead of a dedicated
  // * MutationObserver - see the onInsert contract in app_core.js.
  // * scheduleAnchorUpdate() coalesces via requestAnimationFrame, since
  // * onInsert calls back once per matched element, not once per batch.
  // *
  // * Fires only for CONTENT_ELEMENT_SELECTOR (sdoc-anchor) matches - the
  // * inserted node itself or a descendant of it, per the onInsert
  // * contract. Unaffected by mutations that don't insert an anchor:
  // * opening a node's edit form replaces it with form markup that has no
  // * sdoc-anchor at all, so this never fires while editing. It does fire
  // * when a node's read view (with its anchor) is re-inserted afterwards -
  // * both on save (already covered anyway by the TOC frame observer,
  // * since saving also updates frame-toc) and on Cancel (which does not
  // * touch frame-toc at all): this update is what keeps the
  // * IntersectionObserver correctly associated with the re-inserted
  // * anchor element in both cases.
  strictDoc.onInsert(CONTENT_ELEMENT_SELECTOR, function (anchor) {
    scheduleAnchorUpdate(contentFrame, anchorObserver, anchor);
  });

  // * Refresh TOC highlights when collapsible_toc.js changes branch visibility.
  strictDoc.bus.on(TOC_STATE_CHANGED_EVENT, () => {
    scheduleHighlightRefresh();
  });

},false);

function highlightTOC(tocFrame, contentFrame, anchorObserver) {
  // * Rebuild in order: links → anchors → hash highlight.
  resetState();
  processLinkList(tocFrame);
  processAnchorList(contentFrame, anchorObserver);
  handleHashChange();

  TOC_HIGHLIGHT_DEBUG && console.log(tocHighlightingState);
}

function handleHashChange() {
  // * May fire before links are collected; guard against early hashchange.
  const hash = window.location.hash;
  const fragment = hash ? decodeURIComponent(hash.slice(1)) : null;

  if (!tocHighlightingState.links || tocHighlightingState.links.length === 0) {
    return;
  }

  tocHighlightingState.links.forEach(link => {
    targetItem(link, false)
  });
  // * If there's a fragment and a mapped pair, highlight its link.
  if (fragment) {
    let pair = tocHighlightingState.data[fragment];
    if (!pair || !pair.link) {
      // Try to resolve moved/renumbered ids by suffix
      const resolved = resolveMovedFragment(fragment);
      if (resolved) {
        TOC_HIGHLIGHT_DEBUG && console.log('handleHashChange(): remapped fragment', fragment, '→', resolved);
        history.replaceState(null, '', '#' + encodeURIComponent(resolved));
        pair = tocHighlightingState.data[resolved];
        // * history.replaceState() does not fire `hashchange`, so
        // * collapsible_toc.js's own `hashchange` listener cannot rely on
        // * seeing this correction by itself - tell it explicitly. See
        // * app_core.js for the full bus contract.
        strictDoc.bus.emit(TOC_FRAGMENT_RESOLVED_EVENT, { anchor: resolved });
      }
    }
    if (pair && pair.link) {
      targetItem(resolveVisibleTocLink(pair.link));
    } else {
      // No mapping found — keep URL as-is and move on silently
      // TOC_HIGHLIGHT_DEBUG &&
      console.warn('handleHashChange(): no mapping for fragment', fragment);
      return;
    }
  }
}

function processLinkList(tocFrame) {
  // * Collect TOC links; NodeList is never null. Skip if empty.
  tocHighlightingState.links = tocFrame.querySelectorAll(TOC_ELEMENT_SELECTOR);
  if (tocHighlightingState.links.length === 0) {
    return;
  }
  tocHighlightingState.links.length
    && tocHighlightingState.links.forEach(link => {
    // * Map only links that have an "anchor" attribute.
    const id = link.getAttribute('anchor');
    if (!id) return; // Skip links without an anchor attribute
    tocHighlightingState.data[id] = {
      'link': link,
      ...tocHighlightingState.data[id]
    }

    // * If a link precedes a nested <ul>, register the folder and its "closer" anchors.
    const ul = link.nextElementSibling;

    if (ul && ul.nodeName === 'UL') {
      // register folder
      tocHighlightingState.folderSet.add(id);

      // register closer
      const lastLink = findDeepestLastChild(ul);
      const lastAnchor = lastLink?.getAttribute('anchor');
      if (!lastAnchor) return;

      if (!tocHighlightingState.closerForFolder[lastAnchor]) {
        tocHighlightingState.closerForFolder[lastAnchor] = [];
      }
      tocHighlightingState.closerForFolder[lastAnchor].push(id);
    }
  });
}

function processAnchorList(contentFrame, anchorObserver) {
  // * Re-scan content anchors;
  // * detect cheap changes via count + order-sensitive signature.

  // * Collects all anchors in the document
  const newAnchors = Array.from(
    contentFrame.querySelectorAll(CONTENT_ELEMENT_SELECTOR)
  );
  tocHighlightingState.contentFrameEl = contentFrame;

  // * Build order-sensitive signature to detect renames/reorders without full re-subscribe.
  let sig = 0;
  for (let i = 0; i < newAnchors.length; i++) {
    const id = newAnchors[i].id || "";
    // djb2-like rolling hash with index mix; kept in 32-bit int space
    let h = 5381;
    for (let j = 0; j < id.length; j++) {
      h = ((h << 5) + h) ^ id.charCodeAt(j);
    }
    // mix position to make reorders detectable
    sig = (sig ^ ((h + i * 2654435761) | 0)) | 0;
  }

  // * Set unchanged → keep IO subscriptions; rebuild data[id].anchor after resetState().
  const unchanged = (
    tocHighlightingState.anchorsCount === newAnchors.length &&
    tocHighlightingState.anchorsSig === sig
  );

  if (unchanged) {
    // * After resetState(), mapping in data[] is empty.
    // We must rebuild anchor→data mapping even if the set is unchanged,
    // otherwise IntersectionObserver events may hit undefined.
    tocHighlightingState.anchors = newAnchors;
    newAnchors.forEach(anchor => {
      const id = anchor.id;
      tocHighlightingState.data[id] = {
        ...tocHighlightingState.data[id],
        'anchor': anchor
      };
    });
    rebuildLinkedAnchors();
    return;
  }

  // * Set changed → drop old IO targets and re‑subscribe.
  anchorObserver.disconnect(); // ** Re-subscribe anchors only when content changed

  tocHighlightingState.anchors = newAnchors;
  tocHighlightingState.anchorsCount = newAnchors.length;
  tocHighlightingState.anchorsSig = sig;

  newAnchors.forEach(anchor => {
    const id = anchor.id;
    tocHighlightingState.data[id] = {
      ...tocHighlightingState.data[id],
      'anchor': anchor
    };
    // * Adds an observer for the position of the anchor
    anchorObserver.observe(anchor);
  });
  rebuildLinkedAnchors();
}

function rebuildLinkedAnchors() {
  const linkedAnchors = [];
  tocHighlightingState.anchors.forEach(anchor => {
    const id = anchor.id;
    const pair = tocHighlightingState.data[id];
    if (!pair || !pair.anchor || !pair.link) {
      return;
    }
    linkedAnchors.push({
      anchor: pair.anchor,
      link: pair.link,
    });
  });
  tocHighlightingState.linkedAnchors = linkedAnchors;
}

function handleIntersect(entries, observer) {
  // IntersectionObserver drives events, but the actual "which sections are
  // visible" decision is done by range geometry in updateVisibleSectionItems().
  const viewportBounds = getHighlightViewportBounds(
    entries.length > 0 ? entries[0].rootBounds : null
  );
  if (!viewportBounds) {
    return;
  }
  const { topBound, bottomBound } = viewportBounds;

  entries.forEach((entry) => {

    const anchor = entry.target.id;

    // * IO may fire between resets; mapping may be missing — skip safely.
    const link = tocHighlightingState.data[anchor]?.link;

    // * if there is no menu item for the section in the TOC
    if(!link) {
      return
    }

    // ** Visible (any positive intersection). Highlight item and related folders.
    if (entry.isIntersecting) { //! entry.intersectionRatio > 0 -- it happens to be equal to zero at the intersection!

      TOC_HIGHLIGHT_DEBUG && console.group('🔶', entry.isIntersecting, entry.intersectionRatio, anchor, entry.intersectionRect.height);

      // * semi-highlights folder in the TOC,
      if (tocHighlightingState.folderSet.has(anchor)) {
        TOC_HIGHLIGHT_DEBUG && console.log('🔴', anchor, '(visible folder)', );
        fireFolder(link)
      }

      // * semi-highlights closer`s parent folder in the TOC,
      if (tocHighlightingState.closerForFolder[anchor]) {
        tocHighlightingState.closerForFolder[anchor].forEach(id => {
          TOC_HIGHLIGHT_DEBUG && console.log(`🔴`, id, `(from ${anchor})`);
          const pair2 = tocHighlightingState.data[id];
          console.assert(pair2 && pair2.link, 'handleIntersect(): missing folder link for', id);
          if (pair2 && pair2.link) {
            fireFolder(pair2.link);
          }
        })
      }
      TOC_HIGHLIGHT_DEBUG && console.groupEnd();

    // ** Not visible. Remove item highlight and conditionally de-highlight folders.
    } else {
      TOC_HIGHLIGHT_DEBUG && console.group('🔹', entry.isIntersecting, entry.intersectionRatio, anchor);

      if(
        // * If the node goes down ⬇️ off the screen
        entry.boundingClientRect.bottom >= bottomBound
        // *  and it's a folder
        && tocHighlightingState.folderSet.has(anchor)
      ) {
        // ** remove highlights from folder in the TOC
        TOC_HIGHLIGHT_DEBUG && console.log(`⚫ ⬇️`, anchor);
        fireFolder(link, false)
      }

      if(
        // * If the node goes up ⬆️ off the screen
        entry.boundingClientRect.top <= topBound
        // * and this is the last child of the section
        && tocHighlightingState.closerForFolder[anchor]
      ) {
        // * When the LAST CHILD of the section disappears
        // * over the upper boundary (<= topBound),
        // * strictly speaking, this occurs when the lower bound disappears:
        // * entry.boundingClientRect.bottom.
        // * But we will use the upper bound, entry.boundingClientRect.top
        // * which will be less than or equal to the lower bound.

        // ** remove highlights from closer`s parent folder in the TOC
        tocHighlightingState.closerForFolder[anchor].forEach(id => {
          TOC_HIGHLIGHT_DEBUG && console.log(`⚫ ⬆️`, id,);
          const pair3 = tocHighlightingState.data[id];
          console.assert(pair3 && pair3.link, 'handleIntersect(): missing folder link for', id);
          if (pair3 && pair3.link) {
            fireFolder(pair3.link, false);
          }
        });
      }

      TOC_HIGHLIGHT_DEBUG && console.groupEnd();
    }
  });

  updateVisibleSectionItems(topBound, bottomBound);
}

// Coalesce multiple content-frame mutations (e.g. all nodes inserted by one
// lazily-loaded chunk) into a single anchor-cache update.
function scheduleAnchorUpdate(contentFrame, anchorObserver, insertedAnchor) {
  pendingInsertedAnchors.add(insertedAnchor);
  if (anchorUpdateRaf !== null) {
    return;
  }
  anchorUpdateRaf = requestAnimationFrame(() => {
    anchorUpdateRaf = null;
    const insertedAnchors = Array.from(pendingInsertedAnchors);
    pendingInsertedAnchors.clear();
    // * Deliberately not resetState()+processLinkList(): the TOC link for
    // * every node id was already captured by the initial full scan, so
    // * merging newly found anchors into the existing data[id] entries is
    // * enough - see toc_highlighting.js task notes.
    if (
      !processContiguousInsertedAnchors(
        contentFrame,
        anchorObserver,
        insertedAnchors
      )
    ) {
      // Replacements of an existing ID or several disjoint insertion ranges
      // are uncommon and structurally more complex. Preserve the established
      // full reconciliation path for those cases.
      processAnchorList(contentFrame, anchorObserver);
    }
    refreshHighlightFromCurrentState();
  });
}

function processContiguousInsertedAnchors(
  contentFrame,
  anchorObserver,
  insertedAnchors
) {
  const newAnchors = insertedAnchors.filter(anchor => {
    return anchor.isConnected && contentFrame.contains(anchor);
  });
  if (newAnchors.length === 0) {
    return true;
  }

  // onInsert also reports elements that already existed when the handler was
  // registered. Ignore those exact elements. A different element with the
  // same ID is a replacement (edit/save/cancel) and uses full reconciliation.
  const uniqueNewAnchors = [];
  const seenAnchorIds = new Set();
  for (const anchor of newAnchors) {
    if (seenAnchorIds.has(anchor.id)) {
      return false;
    }
    seenAnchorIds.add(anchor.id);

    const existingAnchor = tocHighlightingState.data[anchor.id]?.anchor;
    if (existingAnchor === anchor) {
      continue;
    }
    if (existingAnchor !== undefined) {
      return false;
    }
    uniqueNewAnchors.push(anchor);
  }
  if (uniqueNewAnchors.length === 0) {
    return true;
  }

  uniqueNewAnchors.sort(compareAnchorsByDomOrder);
  const currentAnchors = tocHighlightingState.anchors ?? [];
  if (currentAnchors.some(anchor => !anchor.isConnected)) {
    // A pure insertion leaves every tracked anchor connected. A disconnected
    // element means this batch also replaced or removed content, possibly
    // under a different ID, so reconcile the complete current DOM.
    return false;
  }
  const anchorInsertionIndex = findAnchorInsertionIndex(
    currentAnchors,
    uniqueNewAnchors[0],
    anchor => anchor
  );
  const nextCurrentAnchor = currentAnchors[anchorInsertionIndex];
  if (
    nextCurrentAnchor !== undefined &&
    !isBeforeInDom(
      uniqueNewAnchors[uniqueNewAnchors.length - 1],
      nextCurrentAnchor
    )
  ) {
    // At least one existing anchor lies inside the inserted batch, so this is
    // not a single new contiguous range.
    return false;
  }

  uniqueNewAnchors.forEach(anchor => {
    tocHighlightingState.data[anchor.id] = {
      ...tocHighlightingState.data[anchor.id],
      'anchor': anchor
    };
    anchorObserver.observe(anchor);
  });
  currentAnchors.splice(
    anchorInsertionIndex,
    0,
    ...uniqueNewAnchors
  );
  tocHighlightingState.anchors = currentAnchors;

  const newLinkedAnchors = uniqueNewAnchors.flatMap(anchor => {
    const pair = tocHighlightingState.data[anchor.id];
    if (pair?.link === undefined) {
      return [];
    }
    return [{
      anchor,
      link: pair.link,
    }];
  });
  if (newLinkedAnchors.length > 0) {
    const linkedAnchorInsertionIndex = findAnchorInsertionIndex(
      tocHighlightingState.linkedAnchors,
      newLinkedAnchors[0].anchor,
      linkedAnchor => linkedAnchor.anchor
    );
    tocHighlightingState.linkedAnchors.splice(
      linkedAnchorInsertionIndex,
      0,
      ...newLinkedAnchors
    );
  }

  // The ordered signature is only needed to recognize a future full scan as
  // unchanged. Force that future scan to reconcile once; lazy insertions
  // themselves continue through this incremental path.
  tocHighlightingState.anchorsCount = -1;
  return true;
}

function compareAnchorsByDomOrder(leftAnchor, rightAnchor) {
  if (leftAnchor === rightAnchor) {
    return 0;
  }
  return isBeforeInDom(leftAnchor, rightAnchor) ? -1 : 1;
}

function isBeforeInDom(leftAnchor, rightAnchor) {
  return Boolean(
    leftAnchor.compareDocumentPosition(rightAnchor) &
    Node.DOCUMENT_POSITION_FOLLOWING
  );
}

function findAnchorInsertionIndex(items, insertedAnchor, getAnchor) {
  let lowerIndex = 0;
  let upperIndex = items.length;
  while (lowerIndex < upperIndex) {
    const middleIndex = Math.floor((lowerIndex + upperIndex) / 2);
    if (isBeforeInDom(getAnchor(items[middleIndex]), insertedAnchor)) {
      lowerIndex = middleIndex + 1;
    } else {
      upperIndex = middleIndex;
    }
  }
  return lowerIndex;
}

// Coalesce multiple TOC state changes into a single frame refresh.
function scheduleHighlightRefresh() {
  if (tocRefreshRaf !== null) {
    return;
  }
  tocRefreshRaf = requestAnimationFrame(() => {
    tocRefreshRaf = null;
    refreshHighlightFromCurrentState();
  });
}

// Recalculate highlights from current DOM state without waiting for new IO entries.
function refreshHighlightFromCurrentState() {
  if (!tocHighlightingState.contentFrameEl) {
    return;
  }

  const viewportBounds = getHighlightViewportBounds();
  if (!viewportBounds) {
    return;
  }
  const { topBound, bottomBound } = viewportBounds;

  updateVisibleSectionItems(topBound, bottomBound);
  handleHashChange();
}

function getHighlightViewportBounds(observerRootBounds = null) {
  // IntersectionObserver normally supplies the rectangle of its `.main`
  // root. Explicit refreshes (for example after collapsing a TOC branch) have
  // no observer entry, so measure the same scroll container directly.
  const scrollContainer = tocHighlightingState.contentFrameEl?.closest(
    CONTENT_SCROLL_CONTAINER_SELECTOR
  );
  const rootBounds = observerRootBounds
    ?? scrollContainer?.getBoundingClientRect();
  if (!rootBounds) {
    return null;
  }
  return {
    topBound: rootBounds.top + HIGHLIGHT_VIEWPORT_TOP_INSET_PX,
    bottomBound: (
      rootBounds.bottom - HIGHLIGHT_VIEWPORT_BOTTOM_INSET_PX
    ),
  };
}

function updateVisibleSectionItems(topBound, bottomBound) {
  // Section visibility is computed by intervals between anchors:
  // section_i := [anchor_i.top, anchor_{i+1}.top), and for the last section:
  // [anchor_last.top, contentFrame.bottom).
  // If this interval overlaps the virtual viewport [topBound, bottomBound],
  // the corresponding TOC item is marked as intersected.
  const linkedAnchors = tocHighlightingState.linkedAnchors;
  if (linkedAnchors.length === 0) {
    tocHighlightingState.visibleLinks.forEach(link => {
      fireItem(link, false);
    });
    tocHighlightingState.visibleLinks = new Set();
    return;
  }

  // Anchor positions follow DOM order. Locate the small interval overlapping
  // the viewport with logarithmic geometry reads instead of measuring every
  // loaded anchor on each IntersectionObserver callback.
  //
  // The section containing topBound starts at the last anchor whose top is
  // <= topBound. Anchors at bottomBound start outside the open lower edge and
  // are excluded. These bounds preserve the original interval definition:
  // [anchor_i.top, anchor_{i+1}.top).
  const firstAnchorBelowTop = findFirstAnchorTopGreaterThan(
    linkedAnchors,
    topBound
  );
  const firstAnchorAtOrBelowBottom = findFirstAnchorTopAtLeast(
    linkedAnchors,
    bottomBound
  );
  const firstVisibleSectionIndex = Math.max(0, firstAnchorBelowTop - 1);

  // If a TOC child is hidden by a collapsed branch, its first visible ancestor
  // owns the highlight. Several visible children can therefore resolve to the
  // same link, so collect the result in a Set.
  const nextVisibleLinks = new Set();
  for (
    let index = firstVisibleSectionIndex;
    index < firstAnchorAtOrBelowBottom;
    index += 1
  ) {
    const link = resolveVisibleTocLink(linkedAnchors[index].link);
    if (link) {
      nextVisibleLinks.add(link);
    }
  }

  // Attribute writes can trigger style recalculation. Touch only links whose
  // state actually changed instead of clearing and rebuilding all N links.
  tocHighlightingState.visibleLinks.forEach(link => {
    if (!nextVisibleLinks.has(link)) {
      fireItem(link, false);
    }
  });
  nextVisibleLinks.forEach(link => {
    if (!tocHighlightingState.visibleLinks.has(link)) {
      fireItem(link, true);
    }
  });
  tocHighlightingState.visibleLinks = nextVisibleLinks;
}

function findFirstAnchorTopGreaterThan(linkedAnchors, boundary) {
  let lowerIndex = 0;
  let upperIndex = linkedAnchors.length;
  while (lowerIndex < upperIndex) {
    const middleIndex = Math.floor((lowerIndex + upperIndex) / 2);
    const anchorTop =
      linkedAnchors[middleIndex].anchor.getBoundingClientRect().top;
    if (anchorTop <= boundary) {
      lowerIndex = middleIndex + 1;
    } else {
      upperIndex = middleIndex;
    }
  }
  return lowerIndex;
}

function findFirstAnchorTopAtLeast(linkedAnchors, boundary) {
  let lowerIndex = 0;
  let upperIndex = linkedAnchors.length;
  while (lowerIndex < upperIndex) {
    const middleIndex = Math.floor((lowerIndex + upperIndex) / 2);
    const anchorTop =
      linkedAnchors[middleIndex].anchor.getBoundingClientRect().top;
    if (anchorTop < boundary) {
      lowerIndex = middleIndex + 1;
    } else {
      upperIndex = middleIndex;
    }
  }
  return lowerIndex;
}

function isElementVisible(element) {
  return !!(element && element.getClientRects().length);
}

// The TOC link one branch level up from `link`: from its <li>, the parent
// <ul> is the list it sits in, and the nearest <li> ancestor of that <ul>
// is the branch one level up (markup pattern: <li><a/><ul>...</ul></li>).
function getParentTocLink(link) {
  const li = link?.closest('li');
  const parentUl = li?.parentElement;
  const parentLi = parentUl?.parentElement;
  if (!parentLi || parentLi.nodeName !== 'LI') {
    return null;
  }
  return parentLi.querySelector(':scope > a');
}

function resolveVisibleTocLink(link) {
  let candidate = link;
  while (candidate && !isElementVisible(candidate)) {
    candidate = getParentTocLink(candidate);
  }
  return candidate || link;
}

function findDeepestLastChild(element) {
  // * Walk down the last-child chain to find the last <a> inside a nested list

  // ! depends on TOC markup
  // ul > li > div + a + ul > ...
  // ul > li > a
  //    > li > a <---------------***

  // Return the last <a> in the subtree or null if none exists.
  // This avoids returning container elements (UL/LI/DIV) that lack the 'anchor' attribute.
  if (!element) return null;
  if (element.nodeName === 'A') {
    return element;
  }
  const children = element.children;
  if (children && children.length > 0) {
    // Walk from the end toward the start; return the first <a> found in the deepest/rightmost branch.
    for (let i = children.length - 1; i >= 0; i--) {
      const found = findDeepestLastChild(children[i]);
      if (found) return found;
    }
  }
  return null;
}

function targetItem(element, on = true) {
  // * Toggle "targeted" attribute for direct hash navigation.
  console.assert(element, 'targetItem(): expected a valid element');
  if(on) {
    element.setAttribute('targeted', '');
  } else {
    element.removeAttribute('targeted');
  }
}

function fireItem(element, on = true) {
  // * Toggle "intersected" attribute for visible anchors.
  console.assert(element, 'fireItem(): expected a valid element');
  if(on) {
    element.setAttribute('intersected', '');
  } else {
    element.removeAttribute('intersected');
  }
}

function fireFolder(element, on = true) {
  // * Toggle "parented" attribute for section folders.
  console.assert(element, 'fireFolder(): expected a valid element');
  if(on) {
    element.setAttribute('parented', '');
  } else {
    element.removeAttribute('parented');
  }
}

function resolveMovedFragment(oldId) {
  // Heuristic: many ids look like "<numbering>-<slug>", where numbering changes on reorder.
  // Try to map by the slug suffix after the first '-' if the exact id is missing.
  const dash = oldId.indexOf('-');
  if (dash === -1) return null; // no recognizable pattern
  const suffix = oldId.slice(dash + 1);
  if (!suffix) return null;

  const keys = Object.keys(tocHighlightingState.data);
  const candidates = keys.filter(k => k.endsWith(suffix));
  if (candidates.length === 1) {
    return candidates[0];
  }
  // If multiple candidates, don't guess.
  return null;
}
})();
