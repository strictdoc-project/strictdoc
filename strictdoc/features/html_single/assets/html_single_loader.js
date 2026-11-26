// html_single_loader.js
//
// The loader of the single-file HTML export (html-single). The exporter
// inlines this script into the exported file, next to a JSON manifest with
// all files of the HTML export.
//
// - The loader shows each exported page in its own iframe. The pages keep
//   their own scripts and element IDs, like in the multi-file export.
// - The loader replaces the references of a page to CSS, JavaScript, images
//   and fonts with blob: URLs of the embedded files.
// - The address of the exported file holds the current page:
//   <file>.html#/<page path>#<anchor>. The back button and bookmarks work.
// - A stable link <file>.html?a=<UID or MID> opens the page of the node.
// - Libraries that the export does not embed are loaded from a CDN or
//   replaced with a stub (see html_single_libraries.py).
//
// The pages run in iframes with the srcdoc attribute. Such an iframe has the
// origin of the exported file. The pages can therefore use the IndexedDB of
// the file, for example for the static editor, and the blob: URLs of the
// loader.
//
// @relation(SDOC-SRS-217, scope=file)

(() => {
  'use strict';

  // A virtual origin to resolve relative paths of the exported files.
  const VIRTUAL_ORIGIN = 'https://strictdoc-html-single.invalid/';
  const FRAME_CLASS = 'strictdoc-html-single-frame';

  const MANIFEST = JSON.parse(
    document.getElementById('strictdoc-html-single-data').textContent
  );
  const FILES = MANIFEST.files;
  const SCRIPTS = MANIFEST.scripts || {};

  // Stubs for libraries that the export leaves out because no page uses
  // them. The inline scripts of the pages still call the libraries.
  const LIBRARY_STUBS = {
    mathjax: `
      window.MathJax = Object.assign(window.MathJax || {}, {
        typeset() {},
        typesetClear() {},
        typesetPromise() { return Promise.resolve(); },
        startup: { promise: Promise.resolve() },
      });`,
    mermaid: `
      window.mermaid = {
        initialize() {},
        run() { return Promise.resolve(); },
      };`,
    plantuml: `
      window.PlantUMLCore = {
        renderToString(lines, onSuccess, onError) {
          onError('PlantUML is not available.');
        },
      };`,
  };

  const bytesCache = new Map();
  const blobURLCache = new Map();
  let projectMapPromise = null;
  let renderCounter = 0;

  // ---------------------------------------------------------------------
  // Embedded files
  // ---------------------------------------------------------------------

  function hasFile(path) {
    return Object.prototype.hasOwnProperty.call(FILES, path);
  }

  function getMimeType(path) {
    return FILES[path][0];
  }

  function getBytes(path) {
    if (!bytesCache.has(path)) {
      const binary = atob(FILES[path][1]);
      const compressed = new Uint8Array(binary.length);
      for (let index = 0; index < binary.length; index += 1) {
        compressed[index] = binary.charCodeAt(index);
      }
      const stream = new Blob([compressed])
        .stream()
        .pipeThrough(new DecompressionStream('gzip'));
      bytesCache.set(path, new Response(stream).arrayBuffer());
    }
    return bytesCache.get(path);
  }

  async function getText(path) {
    return new TextDecoder().decode(await getBytes(path));
  }

  function getBlobURL(path) {
    if (!blobURLCache.has(path)) {
      blobURLCache.set(path, createBlobURL(path));
    }
    return blobURLCache.get(path);
  }

  async function createBlobURL(path) {
    let content = await getBytes(path);
    if (getMimeType(path) === 'text/css') {
      content = await rewriteCSS(await getText(path), path);
    }
    return URL.createObjectURL(new Blob([content], { type: getMimeType(path) }));
  }

  async function rewriteCSS(css, cssPath) {
    const pattern = /url\(\s*(['"]?)([^'")]+)\1\s*\)/g;
    const replacements = new Map();
    for (const match of css.matchAll(pattern)) {
      const target = resolvePath(match[2], cssPath);
      if (target !== null && hasFile(target.path)) {
        replacements.set(match[0], `url("${await getBlobURL(target.path)}")`);
      }
    }
    return css.replace(pattern, (match) => replacements.get(match) || match);
  }

  // ---------------------------------------------------------------------
  // Paths and routes
  // ---------------------------------------------------------------------

  // Resolve a reference of an exported file to a path in the manifest.
  // Returns null for external URLs.
  function resolvePath(reference, fromPath) {
    if (
      reference === null ||
      reference === '' ||
      /^(?:[a-z][a-z0-9+.-]*:|\/\/)/i.test(reference)
    ) {
      return null;
    }
    let url;
    try {
      url = new URL(reference, VIRTUAL_ORIGIN + fromPath);
    } catch (error) {
      return null;
    }
    if (!url.href.startsWith(VIRTUAL_ORIGIN)) {
      return null;
    }
    return {
      path: decodeURIComponent(url.pathname.slice(1)),
      search: url.search,
      hash: url.hash,
    };
  }

  function getShellURL() {
    return window.location.href.split(/[?#]/)[0];
  }

  function createRouteURL(path, hash) {
    return `${getShellURL()}#/${path}${hash || ''}`;
  }

  // The current route: "#/<page path>#<anchor>". A hash without the
  // leading slash is a stable anchor (UID or MID) of a node.
  function parseLocation() {
    const anchor = new URLSearchParams(window.location.search).get('a');
    if (anchor !== null && anchor.length > 0) {
      return { stableAnchor: anchor };
    }
    const hash = window.location.hash;
    if (hash.startsWith('#/')) {
      const route = hash.slice(2);
      const index = route.indexOf('#');
      return index === -1 ?
        { path: route, hash: '' } :
        { path: route.slice(0, index), hash: route.slice(index) };
    }
    if (hash.length > 1) {
      return { stableAnchor: decodeURIComponent(hash.slice(1)) };
    }
    return { path: MANIFEST.start, hash: '' };
  }

  // Classify the target of a link that a reader clicks in a page.
  function resolveLink(href, fromPath) {
    if (href === null || href.startsWith('#')) {
      return null;
    }
    const shellPrefix = `${getShellURL()}#/`;
    if (href.startsWith(shellPrefix)) {
      const route = href.slice(shellPrefix.length);
      const index = route.indexOf('#');
      return index === -1 ?
        { path: route, hash: '' } :
        { path: route.slice(0, index), hash: route.slice(index) };
    }
    const target = resolvePath(href, fromPath);
    if (target === null) {
      return null;
    }
    const anchor = new URLSearchParams(target.search).get('a');
    if (anchor !== null && anchor.length > 0) {
      return { stableAnchor: anchor };
    }
    if (target.path === MANIFEST.start && target.hash.length > 1) {
      return { stableAnchor: decodeURIComponent(target.hash.slice(1)) };
    }
    if (hasFile(target.path) && getMimeType(target.path) !== 'text/html') {
      return { file: target.path };
    }
    return { path: target.path, hash: target.hash };
  }

  // Resolve a UID, MID or node link with the project map of the export,
  // like stable_uri_forwarder.js does in the multi-file export.
  async function resolveStableAnchor(anchor) {
    const projectMap = await loadProjectMap();
    const needle = anchor.toLowerCase();
    for (const [page, nodes] of Object.entries(projectMap)) {
      for (const node of nodes) {
        const keys = [node._LINK, node.UID, node.MID].filter(
          (key) => typeof key === 'string'
        );
        if (keys.some((key) => key.toLowerCase() === needle)) {
          return { path: page, hash: `#${node._LINK}` };
        }
      }
    }
    return null;
  }

  function loadProjectMap() {
    if (projectMapPromise === null) {
      projectMapPromise = (async () => {
        if (!hasFile(MANIFEST.project_map)) {
          return {};
        }
        // project_map.js assigns window.StrictDoc.project.map. Run it in a
        // sandboxed function instead of the page of the loader.
        const sandbox = { StrictDoc: undefined };
        const source = await getText(MANIFEST.project_map);
        new Function('window', source)(sandbox);
        return sandbox.StrictDoc?.project?.map || {};
      })();
    }
    return projectMapPromise;
  }

  // ---------------------------------------------------------------------
  // Navigation
  // ---------------------------------------------------------------------

  function navigate(path, hash, { replace = false } = {}) {
    const url = createRouteURL(path, hash);
    if (replace) {
      window.history.replaceState(null, '', url);
    } else {
      window.history.pushState(null, '', url);
    }
    renderPage(path, hash);
  }

  async function navigateToStableAnchor(anchor, { replace = false } = {}) {
    const target = await resolveStableAnchor(anchor);
    if (target === null) {
      navigate(MANIFEST.start, '', { replace });
      return;
    }
    navigate(target.path, target.hash, { replace });
  }

  async function downloadFile(path) {
    const link = document.createElement('a');
    link.href = await getBlobURL(path);
    link.download = path.split('/').pop();
    document.body.appendChild(link);
    link.click();
    link.remove();
  }

  // Called by the pages when a reader clicks a link.
  function followLink(href, fromPath, newWindow) {
    const target = resolveLink(href, fromPath);
    if (target === null) {
      return false;
    }
    if (target.file !== undefined) {
      downloadFile(target.file);
      return true;
    }
    if (newWindow) {
      if (target.stableAnchor !== undefined) {
        window.open(`${getShellURL()}?a=${encodeURIComponent(target.stableAnchor)}`);
      } else {
        window.open(createRouteURL(target.path, target.hash));
      }
      return true;
    }
    if (target.stableAnchor !== undefined) {
      navigateToStableAnchor(target.stableAnchor);
    } else {
      navigate(target.path, target.hash);
    }
    return true;
  }

  // Called by the pages when the anchor of a page changes, for example
  // after a click in the table of contents.
  function updateAnchor(path, hash) {
    window.history.replaceState(null, '', createRouteURL(path, hash));
  }

  async function onLocationChange({ replace = true } = {}) {
    const route = parseLocation();
    if (route.stableAnchor !== undefined) {
      await navigateToStableAnchor(route.stableAnchor, { replace });
      return;
    }
    renderPage(route.path, route.hash);
  }

  // ---------------------------------------------------------------------
  // Rendering a page
  // ---------------------------------------------------------------------

  async function renderPage(path, hash) {
    renderCounter += 1;
    const renderId = renderCounter;
    let pageHTML;
    if (hasFile(path) && getMimeType(path) === 'text/html') {
      pageHTML = await preparePage(path);
    } else {
      pageHTML = createMissingPage(path);
    }
    if (renderId !== renderCounter) {
      // A newer navigation started while this page was prepared.
      return;
    }
    showFrame(pageHTML, path, hash);
  }

  // A new iframe for every page keeps the history of the browser free from
  // iframe entries. The back button then only follows the routes.
  function showFrame(pageHTML, path, hash) {
    const frame = document.createElement('iframe');
    frame.className = FRAME_CLASS;
    frame.setAttribute('title', path);
    frame.addEventListener('load', () => {
      document.title = frame.contentDocument?.title || document.title;
      if (hash.length > 1) {
        frame.contentWindow.location.hash = hash;
      }
      frame.contentWindow.focus();
    }, { once: true });
    frame.srcdoc = pageHTML;
    for (const oldFrame of document.querySelectorAll(`iframe.${FRAME_CLASS}`)) {
      oldFrame.remove();
    }
    document.body.appendChild(frame);
  }

  function createMissingPage(path) {
    const escapedPath = path.replace(/[&<>"]/g, (character) => (
      { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[character]
    ));
    return `<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Page not included</title>
<style>body{font-family:sans-serif;margin:3em;line-height:1.5}</style>
</head><body data-testid="html-single-missing-page">
<h1>Page not included</h1>
<p>The single-file export does not include this page:</p>
<p><code>${escapedPath}</code></p>
<p><a href="#" onclick="history.back();return false;">Go back</a></p>
</body></html>`;
  }

  async function preparePage(path) {
    const pageDocument = new DOMParser().parseFromString(
      await getText(path),
      'text/html'
    );
    const fontURLs = await prepareMathJaxFonts(pageDocument, path);
    const tasks = [];
    for (const element of pageDocument.querySelectorAll('script[src]')) {
      tasks.push(prepareScript(element, path));
    }
    tasks.push(prepareContent(pageDocument, path));
    await Promise.all(tasks);

    const prelude = pageDocument.createElement('script');
    prelude.textContent = createPrelude(path, fontURLs);
    pageDocument.head.prepend(prelude);

    return `<!DOCTYPE html>\n${pageDocument.documentElement.outerHTML}`;
  }

  // Rewrite the HTML of a lazily loaded document chunk before the page
  // inserts it.
  async function prepareFragment(html, path) {
    const fragmentDocument = new DOMParser().parseFromString(
      `<!DOCTYPE html><html><body>${html}</body></html>`,
      'text/html'
    );
    await prepareContent(fragmentDocument, path);
    return fragmentDocument.body.innerHTML;
  }

  async function prepareContent(contentDocument, path) {
    const tasks = [];
    for (const element of contentDocument.querySelectorAll(
      'link[href], img[src], source[src], embed[src], object[data]'
    )) {
      tasks.push(prepareAsset(element, path));
    }
    for (const element of contentDocument.querySelectorAll('a[href]')) {
      prepareLink(element, path);
    }

    // Scripts that compute URLs from these values cannot resolve relative
    // paths against the srcdoc document. The loader turns them into
    // absolute virtual URLs and serves them in StrictDoc.loadScript().
    for (const element of contentDocument.querySelectorAll(
      '[data-chunk-src]'
    )) {
      const target = resolvePath(element.dataset.chunkSrc, path);
      if (target !== null) {
        element.dataset.chunkSrc = VIRTUAL_ORIGIN + target.path;
      }
    }
    for (const element of contentDocument.querySelectorAll(
      'meta[name="strictdoc-search-index-path"]'
    )) {
      const target = resolvePath(element.getAttribute('content'), path);
      if (target !== null) {
        element.setAttribute('content', VIRTUAL_ORIGIN + target.path);
      }
    }

    // The "Copy stable link" button resolves data-path against the page
    // URL. The loader turns the path into a link to the exported file.
    for (const element of contentDocument.querySelectorAll('[data-path]')) {
      const target = resolvePath(element.dataset.path, path);
      if (target !== null && target.hash.length > 1) {
        element.dataset.path = getShellURL() + target.hash;
      }
    }
    await Promise.all(tasks);
  }

  // Called by the pages after StrictDoc.loadScript() has run a script. A
  // chunk script stores the HTML of a document chunk in
  // StrictDoc.chunks, optionally gzip-compressed and base64-encoded. The
  // loader replaces it with the rewritten HTML as a plain string, which
  // toc_chunk_navigation.js also accepts.
  async function prepareChunks(pageWindow, path) {
    const chunks = pageWindow.StrictDoc?.chunks;
    if (!chunks) {
      return;
    }
    if (!pageWindow.StrictDocHTMLSinglePreparedChunks) {
      pageWindow.StrictDocHTMLSinglePreparedChunks = new Set();
    }
    const preparedKeys = pageWindow.StrictDocHTMLSinglePreparedChunks;
    for (const [key, value] of Object.entries(chunks)) {
      if (preparedKeys.has(key)) {
        continue;
      }
      preparedKeys.add(key);
      const chunkHTML = typeof value === 'string' ?
        value :
        await inflate(value.z);
      chunks[key] = await prepareFragment(chunkHTML, path);
    }
  }

  async function inflate(base64) {
    const binary = atob(base64);
    const bytes = new Uint8Array(binary.length);
    for (let index = 0; index < binary.length; index += 1) {
      bytes[index] = binary.charCodeAt(index);
    }
    const stream = new Blob([bytes])
      .stream()
      .pipeThrough(new DecompressionStream('gzip'));
    return new Response(stream).text();
  }

  async function prepareScript(element, pagePath) {
    const target = resolvePath(element.getAttribute('src'), pagePath);
    if (target === null) {
      return;
    }
    const script = SCRIPTS[target.path];
    if (script !== undefined && script.action === 'cdn') {
      if (script.module_global) {
        // An ES module cannot be loaded with a classic <script src>. A
        // module script imports it and exposes it as a global.
        const moduleScript = element.ownerDocument.createElement('script');
        moduleScript.type = 'module';
        moduleScript.setAttribute('onerror', createFailureHandler(script));
        moduleScript.textContent =
          `import * as library from ${JSON.stringify(script.url)};\n` +
          `window[${JSON.stringify(script.module_global)}] = library;`;
        const importMap = element.ownerDocument.createElement('script');
        importMap.type = 'importmap';
        importMap.textContent = JSON.stringify({
          imports: {},
          integrity: { [script.url]: script.integrity },
        });
        element.ownerDocument.head.prepend(importMap);
        element.replaceWith(moduleScript);
        return;
      }
      element.setAttribute('src', script.url);
      element.setAttribute('integrity', script.integrity);
      element.setAttribute('crossorigin', 'anonymous');
      element.setAttribute('onerror', createFailureHandler(script));
      return;
    }
    if (script !== undefined && script.action === 'stub') {
      const stub = element.ownerDocument.createElement('script');
      stub.textContent = LIBRARY_STUBS[script.library] || '';
      element.replaceWith(stub);
      return;
    }
    if (!hasFile(target.path)) {
      element.remove();
      return;
    }
    element.setAttribute('src', await getBlobURL(target.path));
  }

  // Without an internet connection, a CDN library fails to load. The
  // prelude then installs the stub of the library, so that the inline
  // scripts of the page keep working, and tells the reader.
  function createFailureHandler(script) {
    return `window.StrictDocHTMLSingleLibraryFailed(${JSON.stringify(script.library)})`;
  }

  async function prepareAsset(element, pagePath) {
    const attribute = element.tagName === 'OBJECT' ?
      'data' :
      element.hasAttribute('src') ? 'src' : 'href';
    const target = resolvePath(element.getAttribute(attribute), pagePath);
    if (target === null || !hasFile(target.path)) {
      return;
    }
    element.setAttribute(attribute, await getBlobURL(target.path));
  }

  function prepareLink(element, pagePath) {
    const href = element.getAttribute('href');
    if (href.startsWith('#')) {
      return;
    }
    const target = resolvePath(href, pagePath);
    if (target === null) {
      // An external link replaces the exported file, not only the iframe.
      if (!element.hasAttribute('target') && /^https?:/i.test(href)) {
        element.setAttribute('target', '_top');
      }
      return;
    }
    // Absolute links to the exported file keep "Open in new tab" working.
    // A click on the link does not reload the file: the prelude passes it
    // to followLink().
    if (!hasFile(target.path) || getMimeType(target.path) === 'text/html') {
      element.setAttribute('href', createRouteURL(target.path, target.hash));
    }
  }

  // MathJax loads its fonts from a path relative to its script. The loader
  // serves the embedded fonts as blob: URLs and rewrites the font URLs in the
  // styles that MathJax adds to the page.
  async function prepareMathJaxFonts(pageDocument, pagePath) {
    const folder = MANIFEST.mathjax_fonts_folder;
    if (!folder) {
      return {};
    }
    const usesMathJax = [...pageDocument.querySelectorAll('script[src]')].some(
      (element) => {
        const target = resolvePath(element.getAttribute('src'), pagePath);
        return target !== null && target.path.endsWith('/tex-mml-chtml.js');
      }
    );
    if (!usesMathJax) {
      return {};
    }
    const fontURLs = {};
    for (const path of Object.keys(FILES)) {
      if (path.startsWith(folder)) {
        fontURLs[path.slice(folder.length)] = await getBlobURL(path);
      }
    }
    return fontURLs;
  }

  // The prelude is the first script of every page. It runs before the
  // scripts of the page.
  function createPrelude(path, fontURLs) {
    return `(() => {
  const PAGE = ${JSON.stringify(path)};
  const SHELL = window.parent.StrictDocHTMLSingle;
  // app_core.js keeps an existing StrictDoc.loadScript().
  window.StrictDoc = window.StrictDoc || {};
  window.StrictDoc.loadScript = (url) => SHELL.getScriptURL(url, PAGE).then(
    (scriptURL) => new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = scriptURL;
      script.onload = () => { script.remove(); resolve(); };
      script.onerror = () => reject(new Error('Failed to load script ' + url));
      document.head.appendChild(script);
    })
  ).then(() => SHELL.prepareChunks(window, PAGE));
  // The URL of a srcdoc document is about:srcdoc. Its path and query
  // cannot change, only its fragment. Scripts that build a URL from
  // location.pathname keep only the fragment.
  for (const name of ['pushState', 'replaceState']) {
    const original = history[name].bind(history);
    history[name] = (state, title, url) => {
      if (url === undefined || url === null) {
        return original(state, title);
      }
      try {
        original(state, title, url);
      } catch (error) {
        const hash = new URL(String(url), 'https://page.invalid/').hash;
        original(state, title, 'about:srcdoc' + hash);
      }
      SHELL.updateAnchor(PAGE, window.location.hash);
    };
  }
  // Registered on window, so that the click handlers of the page, which
  // are registered on document or deeper, run first.
  window.addEventListener('click', (event) => {
    if (event.defaultPrevented || event.button !== 0 || event.altKey) return;
    const link = event.target.closest && event.target.closest('a[href]');
    if (!link) return;
    const target = link.getAttribute('target');
    const newWindow = event.ctrlKey || event.metaKey || event.shiftKey ||
      target === '_blank';
    if (target === '_top' && !newWindow) return;
    if (SHELL.followLink(link.getAttribute('href'), PAGE, newWindow)) {
      event.preventDefault();
    }
  });
  window.addEventListener('hashchange', () => {
    SHELL.updateAnchor(PAGE, window.location.hash);
  });
  const STUBS = {
${Object.entries(LIBRARY_STUBS).map(
    ([library, stub]) => `    ${JSON.stringify(library)}: () => {${stub}\n    },`
  ).join('\n')}
  };
  let failureNoticeShown = false;
  window.StrictDocHTMLSingleLibraryFailed = (library) => {
    STUBS[library]();
    if (failureNoticeShown) return;
    failureNoticeShown = true;
    const showNotice = () => {
      const notice = document.createElement('div');
      notice.setAttribute('data-testid', 'html-single-library-notice');
      notice.setAttribute('style', 'position:fixed;top:0;left:50%;' +
        'transform:translateX(-50%);z-index:100000;padding:6px 12px;' +
        'background:#fff3cd;border:1px solid #e0c36b;border-radius:0 0 6px 6px;' +
        'font:13px sans-serif;color:#5c4400;cursor:pointer');
      notice.textContent = 'Diagrams or formulas could not be loaded. ' +
        'This file loads them from the internet (' + library + '). ' +
        'Click to close.';
      notice.addEventListener('click', () => notice.remove());
      document.body.appendChild(notice);
    };
    if (document.body) showNotice();
    else document.addEventListener('DOMContentLoaded', showNotice);
  };
  // Ctrl+P prints the page in the iframe instead of the visible part of
  // the exported file.
  window.addEventListener('keydown', (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'p') {
      event.preventDefault();
      window.print();
    }
  });
  const FONT_URLS = ${JSON.stringify(fontURLs)};
  if (Object.keys(FONT_URLS).length > 0) {
    const pattern = /url\\((['"]?)[^'")]*?\\/([A-Za-z0-9_-]+\\.woff)\\1\\)/g;
    const rewrite = (css) => css.replace(pattern, (match, quote, name) => (
      FONT_URLS[name] ? 'url("' + FONT_URLS[name] + '")' : match
    ));
    const insertRule = CSSStyleSheet.prototype.insertRule;
    CSSStyleSheet.prototype.insertRule = function (rule, index) {
      return insertRule.call(this, rewrite(rule), index);
    };
    new MutationObserver((records) => {
      for (const record of records) {
        for (const node of record.addedNodes) {
          const style = node.nodeType === 1 && node.tagName === 'STYLE' ?
            node :
            node.parentNode && node.parentNode.tagName === 'STYLE' ?
              node.parentNode :
              null;
          if (style && style.textContent.includes('.woff')) {
            const css = rewrite(style.textContent);
            if (css !== style.textContent) style.textContent = css;
          }
        }
      }
    }).observe(document.documentElement, { childList: true, subtree: true });
  }
})();`;
  }

  // Called by the pages through StrictDoc.loadScript().
  async function getScriptURL(url, pagePath) {
    const reference = url.startsWith(VIRTUAL_ORIGIN) ?
      url.slice(VIRTUAL_ORIGIN.length - 1) :
      url;
    const target = resolvePath(reference, pagePath);
    if (target === null || !hasFile(target.path)) {
      return url;
    }
    return getBlobURL(target.path);
  }

  // ---------------------------------------------------------------------
  // Start
  // ---------------------------------------------------------------------

  if (typeof DecompressionStream === 'undefined') {
    document.body.insertAdjacentHTML(
      'beforeend',
      '<p>This browser cannot open the single-file export. ' +
      'Use a current version of Chrome, Edge, Firefox or Safari.</p>'
    );
    return;
  }

  window.StrictDocHTMLSingle = {
    followLink,
    getScriptURL,
    prepareChunks,
    updateAnchor,
  };
  window.addEventListener('keydown', (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'p') {
      const frame = document.querySelector(`iframe.${FRAME_CLASS}`);
      if (frame !== null) {
        event.preventDefault();
        frame.contentWindow.print();
      }
    }
  });
  window.addEventListener('popstate', () => onLocationChange());
  // A reader can also edit the route in the address bar.
  window.addEventListener('hashchange', () => onLocationChange());
  onLocationChange();
})();
