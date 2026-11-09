// Relation preview: hovering or focusing a Parent/Child relation link on a
// DOCUMENT page shows a small card with the linked node's UID, title and
// STATEMENT, so the reader can read it without leaving the page.
//
// Where the STATEMENT comes from:
// 1. The linked node is on this page: its rendered STATEMENT is copied from
//    the page. Nothing extra is downloaded.
// 2. Otherwise (another document, or a chunk of this document that has not
//    loaded yet): "<document>-relation-previews.js" next to the linked
//    document's HTML is loaded once as a <script> and cached. The static
//    export writes that file, the server renders it on request (see
//    relation_previews.py). A <script> is used instead of fetch() because
//    fetch() of a sibling file is blocked under file://, the same reason
//    toc_chunk_navigation.js delivers static chunks as scripts.
//
// The card's header text comes from the link itself (textContent only). The
// STATEMENT is the HTML StrictDoc rendered for that node, the same markup the
// linked page shows. Scripts and ids are dropped from the copy.

(() => {
  if (window.__sdocRelationPreviewWired) return;
  window.__sdocRelationPreviewWired = true;

  const LINK_SELECTOR = 'a.requirement__link-parent, a.requirement__link-child';
  const UID_SELECTOR = '.requirement__parent-uid, .requirement__child-uid';
  const STATEMENT_SELECTOR =
    'sdoc-node-field[data-field-label="statement"] sdoc-field-content';
  const PREVIEWS_SUFFIX = '-relation-previews.js';
  const PREVIEW_ID = 'sdoc-relation-preview';
  const SHOW_DELAY_MS = 250;
  const HIDE_DELAY_MS = 150;
  const GAP_PX = 6;
  const MARGIN_PX = 8;

  // previews file URL -> Promise of { anchor: statement HTML } or null.
  const previewsByUrl = new Map();

  let card = null;
  let activeLink = null;
  let showTimer = null;
  let hideTimer = null;

  function loadPreviews(url) {
    if (!previewsByUrl.has(url)) {
      previewsByUrl.set(url, new Promise((resolve) => {
        const script = document.createElement('script');
        script.src = url;
        // The previews file stores its map under its own
        // document.currentScript.src, which is this script.src.
        script.onload = () => {
          resolve(window.StrictDoc?.relationPreviews?.[script.src] ?? null);
        };
        script.onerror = () => resolve(null);
        document.head.appendChild(script);
      }));
    }
    return previewsByUrl.get(url);
  }

  function sanitize(root) {
    root.querySelectorAll('script').forEach((element) => element.remove());
    root.querySelectorAll('[id]').forEach((element) => element.removeAttribute('id'));
  }

  // Statement HTML from another page has links relative to that page.
  function rebaseUrls(root, pageUrl) {
    root.querySelectorAll('[href], [src]').forEach((element) => {
      for (const attribute of ['href', 'src']) {
        const value = element.getAttribute(attribute);
        if (value) {
          element.setAttribute(attribute, new URL(value, pageUrl).href);
        }
      }
    });
  }

  async function findStatement(link) {
    const url = new URL(link.getAttribute('href'), window.location.href);
    const anchor = decodeURIComponent(url.hash.slice(1));
    if (!anchor) return null;

    const isSamePage = url.origin === window.location.origin &&
      url.pathname === window.location.pathname;
    if (isSamePage) {
      const statement = document.getElementById(anchor)
        ?.closest('sdoc-node')
        ?.querySelector(STATEMENT_SELECTOR);
      if (statement) {
        const copy = document.createDocumentFragment();
        copy.append(...Array.from(statement.childNodes, (node) => node.cloneNode(true)));
        return copy;
      }
    }

    const pageUrl = new URL(url.pathname, url).href;
    const previewsUrl = pageUrl.replace(/\.html$/, PREVIEWS_SUFFIX);
    const previews = await loadPreviews(previewsUrl);
    const html = previews?.[anchor];
    if (typeof html !== 'string') return null;

    const template = document.createElement('template');
    template.innerHTML = html;
    rebaseUrls(template.content, pageUrl);
    // Same wrapper as on the linked page, so autogen.css styles it the same.
    const autogen = document.createElement('sdoc-autogen');
    autogen.append(template.content);
    return autogen;
  }

  function renderHeader(link) {
    const header = document.createElement('div');
    header.className = 'relation_preview-header';

    const uid = link.querySelector(UID_SELECTOR)?.textContent.trim();
    if (uid) {
      const uidElement = document.createElement('span');
      uidElement.className = 'relation_preview-uid';
      uidElement.textContent = uid;
      header.append(uidElement);
    }

    // The title is the link's own text, without the UID and role tags.
    const title = Array.from(link.childNodes)
      .filter((node) => node.nodeType === Node.TEXT_NODE)
      .map((node) => node.textContent)
      .join(' ')
      .trim();
    if (title) {
      const titleElement = document.createElement('span');
      titleElement.className = 'relation_preview-title';
      titleElement.textContent = title;
      header.append(titleElement);
    }
    return header;
  }

  function getCard() {
    // Turbo can replace <body> on the server, which drops the old card.
    if (card?.isConnected) return card;
    card = document.createElement('div');
    card.id = PREVIEW_ID;
    card.className = 'relation_preview';
    card.setAttribute('role', 'tooltip');
    card.setAttribute('data-testid', 'relation-preview');
    card.hidden = true;
    // Let the pointer move into the card, e.g. to select text.
    card.addEventListener('mouseenter', () => clearTimeout(hideTimer));
    card.addEventListener('mouseleave', scheduleHide);
    document.body.append(card);
    return card;
  }

  function place(element, link) {
    // Measure at the top-left corner, where nothing limits the card's width.
    element.style.left = '0px';
    element.style.top = '0px';
    const linkRect = link.getBoundingClientRect();
    const width = element.offsetWidth;
    const height = element.offsetHeight;

    const maxLeft = window.innerWidth - width - MARGIN_PX;
    const left = Math.max(MARGIN_PX, Math.min(linkRect.left, maxLeft));

    let top = linkRect.bottom + GAP_PX;
    const fitsBelow = top + height <= window.innerHeight - MARGIN_PX;
    const fitsAbove = linkRect.top - GAP_PX - height >= MARGIN_PX;
    if (!fitsBelow && fitsAbove) {
      top = linkRect.top - GAP_PX - height;
    }

    element.style.left = `${left}px`;
    element.style.top = `${top}px`;
  }

  async function show(link) {
    activeLink = link;
    let statement = null;
    try {
      statement = await findStatement(link);
    } catch {
      statement = null;
    }
    // The pointer or focus may have moved on while the previews loaded.
    if (activeLink !== link || !statement) return;

    sanitize(statement);
    const body = document.createElement('div');
    body.className = 'relation_preview-statement';
    body.append(statement);

    const element = getCard();
    element.replaceChildren(renderHeader(link), body);
    element.hidden = false;
    place(element, link);
    link.setAttribute('aria-describedby', PREVIEW_ID);
  }

  function hideNow() {
    clearTimeout(showTimer);
    clearTimeout(hideTimer);
    activeLink?.removeAttribute('aria-describedby');
    activeLink = null;
    if (card) card.hidden = true;
  }

  function scheduleShow(link, delay) {
    clearTimeout(hideTimer);
    if (link === activeLink) return;
    clearTimeout(showTimer);
    showTimer = setTimeout(() => show(link), delay);
  }

  function scheduleHide() {
    clearTimeout(showTimer);
    clearTimeout(hideTimer);
    hideTimer = setTimeout(hideNow, HIDE_DELAY_MS);
  }

  function linkFrom(event) {
    return event.target instanceof Element ?
      event.target.closest(LINK_SELECTOR) :
      null;
  }

  document.addEventListener('mouseover', (event) => {
    const link = linkFrom(event);
    if (link) scheduleShow(link, SHOW_DELAY_MS);
  });
  document.addEventListener('mouseout', (event) => {
    const link = linkFrom(event);
    if (link && !link.contains(event.relatedTarget)) scheduleHide();
  });
  document.addEventListener('focusin', (event) => {
    const link = linkFrom(event);
    if (link) scheduleShow(link, 0);
  });
  document.addEventListener('focusout', (event) => {
    if (linkFrom(event)) scheduleHide();
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && activeLink) hideNow();
  });
  // A fixed card would drift away from its link while the content scrolls.
  // Scrolling inside the card itself keeps it open.
  document.addEventListener('scroll', (event) => {
    if (activeLink && !card?.contains(event.target)) hideNow();
  }, true);
})();
