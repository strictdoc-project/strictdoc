// Relation preview: hovering or focusing a relation link of a node on a
// DOCUMENT or TRACE page shows a small card about the link target, so the
// reader can read it without leaving the page.
//
// - A Parent or Child link, with or without a role: the linked node's UID,
//   title and STATEMENT.
// - A File link: the file path and the first lines of the linked range,
//   highlighted the same way as the source file page.
//
// Where the card's content comes from:
// 1. A linked node on this page: its rendered STATEMENT is copied from the
//    page. Nothing extra is downloaded.
// 2. Otherwise (another document, or a chunk of this document that has not
//    loaded yet, or a source file): "<page>-relation-previews.js" next to the
//    linked page's HTML is loaded once as a <script> and cached. The static
//    export writes that file, the server renders it on request (see
//    relation_previews.py). A <script> is used instead of fetch() because
//    fetch() of a sibling file is blocked under file://, the same reason
//    toc_chunk_navigation.js delivers static chunks as scripts.
//
// The card's header text comes from the link itself (textContent only). The
// STATEMENT and the code lines are the HTML StrictDoc rendered, the same
// markup the linked page shows. Scripts and ids are dropped from the copy.
// When there is nothing to show beyond the header, the card shows the header.

(() => {
  if (window.__sdocRelationPreviewWired) return;
  window.__sdocRelationPreviewWired = true;

  const NODE_LINK_SELECTOR = 'a.requirement__link-parent, a.requirement__link-child';
  const FILE_LINK_SELECTOR = 'a.requirement__link-file';
  const LINK_SELECTOR = `${NODE_LINK_SELECTOR}, ${FILE_LINK_SELECTOR}`;
  const UID_SELECTOR = '.requirement__parent-uid, .requirement__child-uid';
  const ROLE_SELECTOR = '.requirement__type-tag';
  const STATEMENT_SELECTOR =
    'sdoc-node-field[data-field-label="statement"] sdoc-field-content';
  const PREVIEWS_SUFFIX = '-relation-previews.js';
  const PREVIEW_ID = 'sdoc-relation-preview';
  // Must match SOURCE_PREVIEW_MAX_LINES in relation_previews.py.
  const MAX_CODE_LINES = 15;
  // A TRACE page links to the TRACE page of another document, while the
  // previews file is named after the document.
  const PAGE_SUFFIX_BY_VIEWTYPE = {
    traceability: '-TRACE.html'
  };
  const SHOW_DELAY_MS = 250;
  const HIDE_DELAY_MS = 150;
  const GAP_PX = 6;
  const MARGIN_PX = 8;

  // previews file URL -> Promise of the previews map or null:
  // { anchor: statement HTML } for a document,
  // { first line: [line HTML, ...] } for a source file.
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

  function previewsUrlFor(pageUrl, isFileLink) {
    const pageSuffix = isFileLink ?
      '.html' :
      PAGE_SUFFIX_BY_VIEWTYPE[document.body?.dataset.viewtype] ?? '.html';
    if (!pageUrl.endsWith(pageSuffix)) return null;
    return pageUrl.slice(0, -pageSuffix.length) + PREVIEWS_SUFFIX;
  }

  function parseHtml(html, pageUrl) {
    const template = document.createElement('template');
    template.innerHTML = html;
    rebaseUrls(template.content, pageUrl);
    return template.content;
  }

  async function findStatement(url) {
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
    const previewsUrl = previewsUrlFor(pageUrl, false);
    const previews = previewsUrl ? await loadPreviews(previewsUrl) : null;
    const html = previews?.[anchor];
    if (typeof html !== 'string') return null;

    // Same wrapper as on the linked page, so autogen.css styles it the same.
    const autogen = document.createElement('sdoc-autogen');
    autogen.append(parseHtml(html, pageUrl));
    return autogen;
  }

  // A File link ends in "#<node UID>#<first line>#<last line>".
  async function findCode(url) {
    const parts = url.hash.split('#');
    const first = Number.parseInt(parts.at(-2), 10);
    const last = Number.parseInt(parts.at(-1), 10);
    if (!(first > 0 && last >= first)) return null;

    const pageUrl = new URL(url.pathname, url).href;
    const previewsUrl = previewsUrlFor(pageUrl, true);
    const previews = previewsUrl ? await loadPreviews(previewsUrl) : null;
    const lines = previews?.[String(first)];
    if (!Array.isArray(lines) || lines.length === 0) return null;

    const rangeLength = last - first + 1;
    const shown = lines.slice(0, Math.min(rangeLength, MAX_CODE_LINES));
    // The "code" class picks up the token colors of pygments.css.
    const code = document.createElement('pre');
    code.className = 'relation_preview-code code';
    shown.forEach((html, index) => {
      const number = document.createElement('span');
      number.className = 'relation_preview-line_number';
      number.textContent = String(first + index);
      code.append(number, parseHtml(html, pageUrl), '\n');
    });

    const fragment = document.createDocumentFragment();
    fragment.append(code);
    if (rangeLength > shown.length) {
      const note = document.createElement('div');
      note.className = 'relation_preview-truncated';
      note.textContent = `Showing ${shown.length} of ${rangeLength} lines.`;
      fragment.append(note);
    }
    return fragment;
  }

  function findContent(link) {
    const url = new URL(link.getAttribute('href'), window.location.href);
    return link.matches(FILE_LINK_SELECTOR) ? findCode(url) : findStatement(url);
  }

  function appendText(parent, className, text) {
    if (!text) return;
    const element = document.createElement('span');
    element.className = className;
    element.textContent = text;
    parent.append(element);
  }

  function renderHeader(link) {
    const header = document.createElement('div');
    header.className = 'relation_preview-header';
    const role = link.querySelector(ROLE_SELECTOR)?.textContent.trim();

    if (link.matches(FILE_LINK_SELECTOR)) {
      // "src/file.py, lines: 1-2, function f()" without the role tag.
      const copy = link.cloneNode(true);
      copy.querySelectorAll(ROLE_SELECTOR).forEach((element) => element.remove());
      appendText(header, 'relation_preview-title',
        copy.textContent.replace(/\s+/g, ' ').trim());
    } else {
      appendText(header, 'relation_preview-uid',
        link.querySelector(UID_SELECTOR)?.textContent.trim());
      // The title is the link's own text, without the UID and role tags.
      appendText(header, 'relation_preview-title', Array.from(link.childNodes)
        .filter((node) => node.nodeType === Node.TEXT_NODE)
        .map((node) => node.textContent)
        .join(' ')
        .trim());
    }
    appendText(header, 'relation_preview-role', role);
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
    // Measure at the top-left corner, where nothing limits the card's size.
    element.style.left = '0px';
    element.style.top = '0px';
    element.style.maxHeight = '';
    const linkRect = link.getBoundingClientRect();
    const width = element.offsetWidth;
    let height = element.offsetHeight;

    const maxLeft = window.innerWidth - width - MARGIN_PX;
    const left = Math.max(MARGIN_PX, Math.min(linkRect.left, maxLeft));

    // Below the link if it fits, else above. If neither fits, use the side
    // with more room and let the card scroll.
    const roomBelow = window.innerHeight - MARGIN_PX - (linkRect.bottom + GAP_PX);
    const roomAbove = linkRect.top - GAP_PX - MARGIN_PX;
    const placeAbove = height > roomBelow &&
      (height <= roomAbove || roomAbove > roomBelow);
    const room = placeAbove ? roomAbove : roomBelow;
    if (height > room) {
      height = Math.max(room, 0);
      element.style.maxHeight = `${height}px`;
    }
    const top = placeAbove ?
      linkRect.top - GAP_PX - height :
      linkRect.bottom + GAP_PX;

    element.style.left = `${left}px`;
    element.style.top = `${top}px`;
  }

  async function show(link) {
    activeLink = link;
    let content = null;
    try {
      content = await findContent(link);
    } catch {
      content = null;
    }
    // The pointer or focus may have moved on while the previews loaded.
    if (activeLink !== link) return;

    const header = renderHeader(link);
    if (!content && !header.hasChildNodes()) return;

    const children = [header];
    if (content) {
      sanitize(content);
      const body = document.createElement('div');
      body.className = 'relation_preview-body';
      body.append(content);
      children.push(body);
    }

    const element = getCard();
    element.replaceChildren(...children);
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
