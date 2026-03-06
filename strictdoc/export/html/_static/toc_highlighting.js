// TOC highlighting: map content <sdoc-anchor id> to TOC <a anchor>
// and toggle TOC states using IntersectionObserver.

const TOC_HIGHLIGHT_DEBUG = false;

const TOC_FRAME_SELECTOR = 'turbo-frame#frame-toc'; // updating
const TOC_LIST_SELECTOR = 'ul#toc';
const TOC_ELEMENT_SELECTOR = 'a';
const CONTENT_FRAME_SELECTOR = 'turbo-frame#frame_document_content'; // action="replace" => parentNode is needed
const CONTENT_ELEMENT_SELECTOR = 'sdoc-anchor';

// Virtual viewport for TOC section highlighting.
// We do not use the raw screen edges (0..innerHeight): we shrink the effective
// area to [top+offset, bottom-offset]. This keeps the active range aligned with
// what users perceive as "currently visible content" (header space, early closing of the previous node).
const VIEWPORT_TOP_OFFSET_PX = 64;
const VIEWPORT_BOTTOM_OFFSET_PX = 32;

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
  closerForFolder: {},
  folderSet: new Set(),
};
let tocRefreshRaf = null;

function resetState() {
  // * Keep anchorsCount/anchorsSig to detect changes across TOC mutations.
  tocHighlightingState.data = {};
  tocHighlightingState.links = null;
  tocHighlightingState.anchors = null;
  tocHighlightingState.contentFrameEl = null;
  tocHighlightingState.closerForFolder = {};
  tocHighlightingState.folderSet = new Set();
}

window.addEventListener("hashchange", handleHashChange);
window.addEventListener("load",function(){

  // * Frames are stable and we define them once.
  const tocFrame = document.querySelector(TOC_FRAME_SELECTOR);
  const tocList = tocFrame ? tocFrame.querySelector(TOC_LIST_SELECTOR) : null;
  const contentFrame = document.querySelector(CONTENT_FRAME_SELECTOR)?.parentNode;

  if (!tocFrame || !contentFrame) { return }

  const anchorObserver = new IntersectionObserver(
    handleIntersect,
    {
      root: null,
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

  // * Refresh TOC highlights when collapsible_toc.js changes branch visibility.
  document.addEventListener('toc:state-changed', () => {
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
  const newAnchors = contentFrame.querySelectorAll(CONTENT_ELEMENT_SELECTOR);
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
        'anchor': anchor,
        ...tocHighlightingState.data[id]
      };
    });
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
      'anchor': anchor,
      ...tocHighlightingState.data[id]
    };
    // * Adds an observer for the position of the anchor
    anchorObserver.observe(anchor);
  });
}

function handleIntersect(entries, observer) {
  // IntersectionObserver drives events, but the actual "which sections are
  // visible" decision is done by range geometry in updateVisibleSectionItems().
  let topBound = VIEWPORT_TOP_OFFSET_PX;
  let bottomBound = window.innerHeight - VIEWPORT_BOTTOM_OFFSET_PX;
  if (entries.length > 0 && entries[0].rootBounds) {
    topBound = entries[0].rootBounds.top + VIEWPORT_TOP_OFFSET_PX;
    bottomBound = entries[0].rootBounds.bottom - VIEWPORT_BOTTOM_OFFSET_PX;
  }

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

  const topBound = VIEWPORT_TOP_OFFSET_PX;
  const bottomBound = window.innerHeight - VIEWPORT_BOTTOM_OFFSET_PX;

  updateVisibleSectionItems(topBound, bottomBound);
  handleHashChange();
}

function updateVisibleSectionItems(topBound, bottomBound) {
  // Section visibility is computed by intervals between anchors:
  // section_i := [anchor_i.top, anchor_{i+1}.top), and for the last section:
  // [anchor_last.top, contentFrame.bottom).
  // If this interval overlaps the virtual viewport [topBound, bottomBound],
  // the corresponding TOC item is marked as intersected.
  if (!tocHighlightingState.anchors || tocHighlightingState.anchors.length === 0) {
    return;
  }

  const linkedAnchors = [];
  tocHighlightingState.anchors.forEach(anchor => {
    const id = anchor.id;
    const pair = tocHighlightingState.data[id];
    if (!pair || !pair.anchor || !pair.link) {
      return;
    }
    linkedAnchors.push({ id, anchor: pair.anchor, link: pair.link });
  });

  if (linkedAnchors.length === 0) {
    return;
  }

  const visibleIds = new Set();
  for (let i = 0; i < linkedAnchors.length; i++) {
    const current = linkedAnchors[i];
    const next = linkedAnchors[i + 1];

    // Section i is the interval [anchor_i, anchor_{i+1}).
    const sectionTop = current.anchor.getBoundingClientRect().top;
    const sectionBottom = next
      ? next.anchor.getBoundingClientRect().top
      : (tocHighlightingState.contentFrameEl?.getBoundingClientRect().bottom ?? bottomBound);

    const sectionOverlapsViewport =
      sectionBottom > topBound && sectionTop < bottomBound;

    if (sectionOverlapsViewport) {
      visibleIds.add(current.id);
    }
  }

  // Reset previous "intersected" states.
  linkedAnchors.forEach(item => {
    fireItem(item.link, false);
  });

  // Highlight visible links. If a link is hidden under collapsed parents,
  // move highlight up to the first visible ancestor link.
  const visibleLinks = new Set();
  linkedAnchors.forEach(item => {
    if (visibleIds.has(item.id)) {
      const link = resolveVisibleTocLink(item.link);
      if (link) {
        visibleLinks.add(link);
      }
    }
  });

  visibleLinks.forEach(link => {
    fireItem(link, true);
  });
}

function isElementVisible(element) {
  return !!(element && element.getClientRects().length);
}

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
