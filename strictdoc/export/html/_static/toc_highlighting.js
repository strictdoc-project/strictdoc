const TOC_HIGHLIGHT_DEBUG = false;

const TOC_FRAME_SELECTOR = 'turbo-frame#frame-toc'; // updating
const TOC_ELEMENT_SELECTOR = 'a';
const CONTENT_FRAME_SELECTOR = 'turbo-frame#frame_document_content'; // replacing => parentNode is needed
const CONTENT_ELEMENT_SELECTOR = 'sdoc-anchor';

let tocHighlightingState = {
  data: {},
  links: null,
  anchors: null,
  contentFrameTop: undefined,
  closerForFolder: {},
  folderSet: new Set(),
};

function resetState() {
  tocHighlightingState.data = {};
  tocHighlightingState.links = null;
  tocHighlightingState.anchors = null;
  tocHighlightingState.closerForFolder = {};
  tocHighlightingState.folderSet = new Set();
}

window.addEventListener("hashchange", handleHashChange);
window.addEventListener("load",function(){

  // * Frames are stable and we define them once.
  const tocFrame = document.querySelector(TOC_FRAME_SELECTOR);
  const contentFrame = document.querySelector(CONTENT_FRAME_SELECTOR)?.parentNode;

  if(!tocFrame || !contentFrame) { return }

  // ! depends on TOC markup
  tocHighlightingState.contentFrameTop = contentFrame.offsetParent
                        ? contentFrame.offsetTop
                        : contentFrame.parentNode.offsetTop;

  const anchorObserver = new IntersectionObserver(
    handleIntersect,
    {
      root: null,
      rootMargin: "0px",
    });

  // * Then we will refresh when the TOC tree is updated&
  // * The content in the tocFrame frame will mutate:
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

  // * Call for the first time.
  highlightTOC(tocFrame, contentFrame, anchorObserver);

},false);

function highlightTOC(tocFrame, contentFrame, anchorObserver) {

  resetState();
  processLinkList(tocFrame);
  processAnchorList(contentFrame, anchorObserver);
  handleHashChange();

  TOC_HIGHLIGHT_DEBUG && console.log(tocHighlightingState);
}

function handleHashChange() {
  const hash = window.location.hash;
  const match = hash.match(/#(.*)/);
  const fragment = match ? match[1] : null;

  tocHighlightingState.links.forEach(link => {
    targetItem(link, false)
  });
  // * When updating the hash
  // * and there's a fragment,
  fragment
    // * and the corresponding link-anchor pair is registered,
    && tocHighlightingState.data[fragment]
    // * highlight the corresponding link.
    && targetItem(tocHighlightingState.data[fragment].link)
}

function processLinkList(tocFrame) {
  // * Collects all links in the TOC
  tocHighlightingState.links = null;
  tocHighlightingState.links = tocFrame.querySelectorAll(TOC_ELEMENT_SELECTOR);
  tocHighlightingState.links.length
    && tocHighlightingState.links.forEach(link => {
    const id = link.getAttribute('anchor');
    tocHighlightingState.data[id] = {
      'link': link,
      ...tocHighlightingState.data[id]
    }

    // ! depends on TOC markup
    // is link in collapsible node and precedes the UL
    // ! expected UL or null
    const ul = link.nextSibling;

    if (ul && ul.nodeName === 'UL') {
      // register folder
      tocHighlightingState.folderSet.add(id);

      // register closer
      const lastLink = findDeepestLastChild(ul);
      const lastAnchor = lastLink.getAttribute('anchor');


      if (!tocHighlightingState.closerForFolder[lastAnchor]) {
        tocHighlightingState.closerForFolder[lastAnchor] = [];
      }
      tocHighlightingState.closerForFolder[lastAnchor].push(id);
    }
  });
}

function processAnchorList(contentFrame, anchorObserver) {
  anchorObserver.disconnect(); // FIXME don`t work: have to hack at #rootBounds_null

  // * Collects all anchors in the document
  tocHighlightingState.anchors = null;
  tocHighlightingState.anchors = contentFrame.querySelectorAll(CONTENT_ELEMENT_SELECTOR);
  tocHighlightingState.anchors.length
    && tocHighlightingState.anchors.forEach(anchor => {
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

  entries.forEach((entry) => {

    // #rootBounds_null
    // rootBounds: null
    // after frame reload and before init
    if(!entry.rootBounds) {
      return
    }

    const anchor = entry.target.id;
    // * For anchors that go into the viewport,
    // * finds the corresponding links
    const link = tocHighlightingState.data[anchor].link;

    // * if there is no menu item for the section in the TOC
    if(!link) {
      return
    }

    if (entry.isIntersecting) { //! entry.intersectionRatio > 0 -- it happens to be equal to zero at the intersection!

      TOC_HIGHLIGHT_DEBUG && console.group('🔶', entry.isIntersecting, entry.intersectionRatio, anchor, entry.intersectionRect.height);
      // * and highlights them in the TOC,
      fireItem(link)

      // * semi-highlights folder in the TOC,
      if (tocHighlightingState.folderSet.has(anchor)) {
        TOC_HIGHLIGHT_DEBUG && console.log('🔴', anchor, '(visible folder)', );
        fireFolder(link)
      }

      // * semi-highlights closer`s parent folder in the TOC,
      if (tocHighlightingState.closerForFolder[anchor]) {
        tocHighlightingState.closerForFolder[anchor].forEach(id => {
          TOC_HIGHLIGHT_DEBUG && console.log(`🔴`, id, `(from ${anchor})`);
          fireFolder(tocHighlightingState.data[id].link)
        })
      }
      TOC_HIGHLIGHT_DEBUG && console.groupEnd();

    } else {

      TOC_HIGHLIGHT_DEBUG && console.group('🔹', entry.isIntersecting, entry.intersectionRatio, anchor);
      // * or cancels highlighting for the rest of the links.
      fireItem(link, false);

      if(
        // * If the node goes down ⬇️ off the screen
        entry.boundingClientRect.bottom >= entry.rootBounds.bottom
        // *  and it's a folder
        && tocHighlightingState.folderSet.has(anchor)
      ) {
        // ** remove highlights from folder in the TOC
        TOC_HIGHLIGHT_DEBUG && console.log(`⚫ ⬇️`, anchor);
        fireFolder(link, false)
      }

      if(
        // * If the node goes up ⬆️ off the screen
        entry.boundingClientRect.y < tocHighlightingState.contentFrameTop
        // * and this is the last child of the section
        && tocHighlightingState.closerForFolder[anchor]
      ) {
        // * When the LAST CHILD of the section disappears
        // * over the upper boundary ( < tocHighlightingState.contentFrameTop),
        // * strictly speaking, this occurs when the lower bound disappears:
        // * entry.boundingClientRect.bottom.
        // * But we will use the upper bound, entry.boundingClientRect.y
        // * which will be less than or equal to the lower bound.

        // ** remove highlights from closer`s parent folder in the TOC
        tocHighlightingState.closerForFolder[anchor].forEach(id => {
          TOC_HIGHLIGHT_DEBUG && console.log(`⚫ ⬆️`, id,);
          fireFolder(tocHighlightingState.data[id].link, false)
        });
      }

      TOC_HIGHLIGHT_DEBUG && console.groupEnd();
    }
  });

}

function findDeepestLastChild(element) {
  // ! depends on TOC markup
  // ul > li > div + a + ul > ...
  // ul > li > a
  //    > li > a <---------------***
  if (element.nodeName === 'A') {
    return element;
  }
  const children = element.children;
  if (children && children.length > 0) {
    return findDeepestLastChild([...children].at(-1))
  } else {
    return element;
  }
}

function targetItem(element, on = true) {
  if(on) {
    element.setAttribute('targeted', '');
  } else {
    element.removeAttribute('targeted');
  }
}

function fireItem(element, on = true) {
  if(on) {
    element.setAttribute('intersected', '');
  } else {
    element.removeAttribute('intersected');
  }
}

function fireFolder(element, on = true) {
  if(on) {
    element.setAttribute('parented', '');
  } else {
    element.removeAttribute('parented');
  }
}
