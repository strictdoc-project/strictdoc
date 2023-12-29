const TOC_FRAME_SELECTOR = 'turbo-frame#frame-toc';
const TOC_ELEMENT_SELECTOR = 'a';
const CONTENT_FRAME_SELECTOR = 'main';
const CONTENT_ELEMENT_SELECTOR = 'sdoc-anchor';

let tocHighlightingState = {
  data: {},
  links: null,
  anchors: null,
};

window.addEventListener("hashchange", handleHashChange);
window.addEventListener("load",function(){

  // * Frames are stable and we define them once.
  const tocFrame = document.querySelector(TOC_FRAME_SELECTOR);
  const contentFrame = document.querySelector(CONTENT_FRAME_SELECTOR);

  // * Call for the first time.
  highlightTOC(tocFrame, contentFrame);

  // * Then we will refresh when the TOC tree is updated&
  // * The content in the tocFrame frame will mutate:
  const mutatingFrame = tocFrame;
  new MutationObserver(function (mutationsList, observer) {
    // * Use requestAnimationFrame to put highlightTOC
    // * at the end of the event queue and to ensure
    // * the code runs after all DOM changes have been applied.
    requestAnimationFrame(() => {
      highlightTOC(tocFrame, contentFrame);
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

},false);

function highlightTOC(tocFrame, contentFrame) {
  tocHighlightingState = {
    data: {},
    links: null,
    anchors: null,
  };
  processLinkList(tocFrame);
  processAnchorList(contentFrame);
  handleHashChange();
}

function processLinkList(tocFrame) {
  // * Collects all links in the TOC
  tocHighlightingState.links = null;
  tocHighlightingState.links = tocFrame.querySelectorAll(TOC_ELEMENT_SELECTOR);
  tocHighlightingState.links.forEach(link => {
    const id = link.getAttribute('anchor');
    tocHighlightingState.data[id] = {
      'link': link,
      ...tocHighlightingState.data[id]
    }
  });
}
function processAnchorList(contentFrame) {
  // * Collects all anchors in the document
  tocHighlightingState.anchors = null;
  tocHighlightingState.anchors = contentFrame.querySelectorAll(CONTENT_ELEMENT_SELECTOR);
  tocHighlightingState.anchors.forEach(anchor => {
    const id = anchor.id;
    tocHighlightingState.data[id] = {
      'anchor': anchor,
      ...tocHighlightingState.data[id]
    };
    // * Adds an observer for the position of the anchor
    createIntersectObserver(anchor);
  });
}

function handleHashChange() {
  const hash = window.location.hash;
  const match = hash.match(/#(.*)/);
  const fragment = match ? match[1] : null;

  tocHighlightingState.links.forEach(link => {
    link.removeAttribute('targeted');
  });
  // * When updating the hash
  // * and there's a fragment,
  fragment
    // * and the corresponding link-anchor pair is registered,
    && tocHighlightingState.data[fragment]
    // * highlight the corresponding link.
    && tocHighlightingState.data[fragment].link.setAttribute('targeted', '');
}

function createIntersectObserver(observedElement) {
  // * Adds an observer for the position of the anchor
  // * relative to the viewport
  let observer;

  let options = {
    root: null,
    rootMargin: "0px",
  };

  observer = new IntersectionObserver(handleIntersect, options);
  observer.observe(observedElement);
}

function handleIntersect(entries, observer) {
  entries.forEach((entry) => {
    const anchor = entry.target.id;
    // * For anchors that go into the viewport,
    if (entry.intersectionRatio > 0) {
      // * finds the corresponding links in the TOC and highlights them,
      tocHighlightingState.data[anchor].link.setAttribute('intersected', '');
    } else {
      // * and cancels highlighting for the rest of the links.
      tocHighlightingState.data[anchor].link.removeAttribute('intersected');
    }
  });
}
