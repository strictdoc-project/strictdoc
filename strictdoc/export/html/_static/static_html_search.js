/**
 * @relation(SDOC-SRS-155, scope=file)
 * @relation(SDOC-SRS-156, scope=file)
 *
 * Required DOM contract:
 * - #search
 * - #userinput
 * - #search_results
 * - #results_count
 * - #suggestions
 * - #results_navigation with #start, #previous, #next, #end
 * - meta[name="strictdoc-document-level"]
 * - meta[name="strictdoc-project-hash"]
 * - meta[name="strictdoc-search-index-timestamp"]
 * - meta[name="strictdoc-search-index-path"]
 */

(function() {
  const strictDocSearch = window.StrictDoc?.search;
  if (!strictDocSearch) {
    throw new Error(
      "static_html_search.js requires app_core.js to initialize StrictDoc.search."
    );
  }

  // =========================================================================
  // DOM and meta discovery
  // =========================================================================

  // Collect the DOM nodes that the static search UI depends on.
  function collectRequiredDom() {
    const selectorByRefKey = {
      searchBox: "#search",
      userinput: "#userinput",
      searchResults: "#search_results",
      resultsCount: "#results_count",
      suggestions: "#suggestions",
      navigationStart: "#results_navigation #start",
      navigationPrevious: "#results_navigation #previous",
      navigationNext: "#results_navigation #next",
      navigationEnd: "#results_navigation #end",
    };

    const dom = Object.fromEntries(
      Object.entries(selectorByRefKey).map(([key, selector]) => {
        if (selector.startsWith("#") && !selector.includes(" ")) {
          return [key, document.getElementById(selector.slice(1))];
        }
        return [key, document.querySelector(selector)];
      })
    );

    const missingSelectors = Object.entries(dom)
      .filter(([, element]) => !element)
      .map(([key]) => selectorByRefKey[key]);

    return {
      dom,
      missingSelectors
    };
  }

  // Collect the meta tags that configure search rendering and index loading.
  function collectRequiredMeta() {
    const selectorByMetaKey = {
      documentLevel: 'meta[name="strictdoc-document-level"]',
      projectHash: 'meta[name="strictdoc-project-hash"]',
      searchIndexTimestamp: 'meta[name="strictdoc-search-index-timestamp"]',
      searchIndexPath: 'meta[name="strictdoc-search-index-path"]',
    };

    const meta = Object.fromEntries(
      Object.entries(selectorByMetaKey).map(([key, selector]) => {
        return [key, document.querySelector(selector)?.content];
      })
    );

    const missingSelectors = Object.entries(meta)
      .filter(([, content]) => !content)
      .map(([key]) => selectorByMetaKey[key]);

    return {
      meta,
      missingSelectors,
    };
  }

  // =========================================================================
  // Query parsing and result shaping
  // =========================================================================

  function escapeRegExp(text) {
    return text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  }

  // Highlight matched terms in result text before rendering the suggestion entry.
  function highlightWord(text, word) {
    let newStr = text.replace(new RegExp(escapeRegExp(word), "gi"), (match) => "<mark>" +
      match + "</mark>");
    return newStr;
  }

  // Intersect per-token result sets for AND-style queries.
  function intersectSets(sets) {
    if (sets.length === 0) return new Set();

    let intersection = new Set(sets[0]);

    for (const s of sets.slice(1)) {
      intersection = new Set([...intersection].filter(x => s.has(x)));
    }

    return intersection;
  }

  // Parse the raw search text into a minimal query model used by the live search UI.
  function parseSearchQuery(searchQuery) {
    const regex = /"([^"]+)"|(\S+)/g;
    const tokens = [];
    let hasQuoted = false;

    const matches = [...searchQuery.matchAll(regex)];

    for (const match of matches) {
      if (match[1]) {
        // Quoted phrase → split into words
        hasQuoted = true;
        tokens.push(match[1].trim().split(/\s+/));
      } else if (match[2]) {
        // Single word
        tokens.push([match[2]]);
      }
    }

    if (hasQuoted) {
      return {
        mode: "AND",
        terms: tokens.flat(),
      };
    }

    return {
      mode: "OR",
      terms: tokens.flat(),
    };
  }

  // Execute a token query by unioning all indexed token matches.
  function executeOrQuery(parsedQuery, searchIndex) {
    let uniqueResults = new Set();
    for (const token of parsedQuery.terms) {
      const tokenResults = searchIndex[token];
      if (tokenResults) {
        uniqueResults = new Set([...uniqueResults, ...tokenResults]);
      }
    }
    return Array.from(uniqueResults);
  }

  // Execute a phrase query by intersecting the per-token index matches first.
  function executeAndQuery(parsedQuery, searchIndex) {
    const firstTerm = parsedQuery.terms[0];
    const firstTermResults = searchIndex[firstTerm];
    if (!firstTermResults || firstTermResults.length === 0) {
      return [];
    }

    let uniqueResults = new Set(firstTermResults);
    for (let i = 1; i < parsedQuery.terms.length; i++) {
      const termResults = searchIndex[parsedQuery.terms[i]];
      const termUniqueResults = new Set(termResults);

      uniqueResults = intersectSets([uniqueResults, termUniqueResults]);
      if (uniqueResults.size === 0) {
        break;
      }
    }

    return Array.from(uniqueResults);
  }

  // Refine AND-style results by verifying the combined phrase against node fields.
  function refineAndQueryResults(results, parsedQuery, nodesByMid) {
    const finalAndResults = [];
    const finalUniqueResults = new Set();
    const andQuery = parsedQuery.terms.join(" ");

    for (const result of results) {
      const node = nodesByMid[parseInt(result, 10)];
      console.assert(!!node, "node must be defined for result: " + result);

      Object.entries(node).forEach(([_, value]) => {
        if (value === "") {
          return;
        }

        if (!finalUniqueResults.has(result) && value.toLowerCase().includes(andQuery)) {
          finalUniqueResults.add(result);
          finalAndResults.push(result);
        }
      });
    }

    return {
      results: finalAndResults,
      highlightElements: [andQuery],
    };
  }

  // Build the data needed by the results view: result ids plus highlight terms.
  function buildSearchViewModel(parsedQuery, searchQuery, searchIndex, nodesByMid) {
    // Keep the existing live-input behavior for search text that still contains
    // a quote character but has not been parsed as a quoted phrase query.
    if (parsedQuery.mode === "OR" && searchQuery.includes('"')) {
      return {
        results: [],
        highlightElements: parsedQuery.terms,
      };
    }

    // ** "AND"
    // Quoted phrase queries first intersect token matches, then verify
    // that the full phrase exists in the matched node fields.
    if (parsedQuery.mode === "AND") {
      const results = executeAndQuery(parsedQuery, searchIndex);
      return refineAndQueryResults(results, parsedQuery, nodesByMid);
    }

    // ** "OR"
    // Unquoted queries use the default token-based OR search path.
    const results = executeOrQuery(parsedQuery, searchIndex);
    return {
      results,
      highlightElements: parsedQuery.terms,
    };
  }

  // =========================================================================
  // Live search UI
  // =========================================================================

  // Render and paginate the live search result list.
  class SearchResultsView {
    static PAGE_SIZE = 5;

    constructor(dom, { userinput, searchData, documentLevel }) {
      this.userinput = userinput;
      this.searchData = searchData;
      this.documentLevel = documentLevel;
      console.assert(
        !isNaN(this.documentLevel),
        "SearchResultsView: documentLevel must be a valid number."
      );

      this.searchBox = dom.searchBox;
      this.searchResults = dom.searchResults;
      this.resultsCount = dom.resultsCount;
      this.suggestions = dom.suggestions;

      this.navigationStart = dom.navigationStart;
      this.navigationPrevious = dom.navigationPrevious;
      this.navigationNext = dom.navigationNext;
      this.navigationEnd = dom.navigationEnd;

      this.navigationStart.addEventListener("click", () => this.displayPage(
        1), true);
      this.navigationPrevious.addEventListener("click", () => this
        .displayPage(this.currentPage - 1), true);
      this.navigationNext.addEventListener("click", () => this.displayPage(
        this.currentPage + 1), true);
      this.navigationEnd.addEventListener("click", () => this.displayPage(
          Math.ceil(this.results.length / SearchResultsView.PAGE_SIZE)),
        true);

      this.selectedIndex = 0;
      this.results = null;
      this.highlightElements = null;
      this.currentPage = 1;
      this.suggestions.addEventListener("click", this.acceptSuggestion, true);
      document.addEventListener("keydown", (event) => this.handleEscape(
        event), true);
    }

    handleEscape(event) {
      if (event.key === "Escape") {
        this.hideResults();
        // On Esc, remove focus from the input field.
        // Otherwise the field remains focused and a subsequent click won't fire a 'focus' event,
        // so the search won't restart. Blurring ensures the next refocus re‑triggers search with
        // the existing text.
        if (document.activeElement === this.userinput) {
          this.userinput.blur();
        }
      }
    }

    hideResults() {
      this.searchBox.removeAttribute("active");
      this.resultsCount.innerHTML = "";
      this.suggestions.replaceChildren();
      this.selectedIndex = 0;
    }

    populateResults(results, highlightElements) {
      const resultsLength = results.length;

      if (resultsLength == 0) {
        this.suggestions.replaceChildren();
        this.resultsCount.innerHTML = `No results.`;
        return;
      }

      this.results = results;
      this.highlightElements = highlightElements;

      this.displayPage(1);

      this.searchBox.setAttribute("active", "");
    }

    displayPage(page) {
      // Ignore requests that point outside the available pagination range.
      if (page < 1 || page > Math.ceil(this.results.length /
          SearchResultsView.PAGE_SIZE)) {
        return;
      }

      // Slice the full result list down to the subset rendered on this page.
      const pageResults = this.results.slice(
        (page - 1) * SearchResultsView.PAGE_SIZE,
        page * SearchResultsView.PAGE_SIZE
      );

      // Persist the current page so the navigation buttons can move relative to it.
      this.currentPage = page;

      // Reuse already rendered result containers where possible.
      const children = this.suggestions.childNodes;

      // Render each result entry for the requested page.
      for (let i = 0; i < pageResults.length; i++) {
        let nodeId = pageResults[i];
        let resultElement = children[i];

        // Create a result container only when the current page needs more rows
        // than were already rendered for the previous page.
        if (!resultElement) {
          resultElement = document.createElement("div");
          this.suggestions.appendChild(resultElement);
        }

        this.renderResultElement(resultElement, nodeId);
      }

      // Remove leftover DOM rows when the new page has fewer results than the previous one.
      while (children.length > pageResults.length) {
        this.suggestions.removeChild(this.suggestions.lastChild);
      }

      // Update pagination controls based on the current page position.
      this.updatePaginationState(page);

      // Refresh the result counter text for the currently visible range.
      this.updateResultsCount(page);

      // Reset keyboard selection to the first visible result on each page change.
      this._selectResult(0);
    }

    updatePaginationState(page) {
      if (this.results.length > SearchResultsView.PAGE_SIZE) {
        if (page < 2) {
          this.navigationStart.setAttribute("disabled", "");
          this.navigationPrevious.setAttribute("disabled", "");
        } else {
          this.navigationStart.removeAttribute("disabled");
          this.navigationPrevious.removeAttribute("disabled");
        }
        if (page >= Math.ceil(this.results.length / SearchResultsView
            .PAGE_SIZE)) {
          this.navigationNext.setAttribute("disabled", "");
          this.navigationEnd.setAttribute("disabled", "");
        } else {
          this.navigationNext.removeAttribute("disabled");
          this.navigationEnd.removeAttribute("disabled");
        }
      } else {
        this.navigationStart.setAttribute("disabled", "");
        this.navigationPrevious.setAttribute("disabled", "");
        this.navigationNext.setAttribute("disabled", "");
        this.navigationEnd.setAttribute("disabled", "");
      }
    }

    updateResultsCount(page) {
      // Compute the human-readable result range shown above the list.
      const rangeStart = (page - 1) * SearchResultsView.PAGE_SIZE + 1;
      const rangeEnd = Math.min(page * SearchResultsView.PAGE_SIZE, this
        .results.length);

      this.resultsCount.innerHTML = `\
  Results: <b>${rangeStart}–${rangeEnd}</b> from ${this.results.length}
  `;
    }

    renderResultElement(resultElement, nodeId) {
      // Resolve the indexed node data behind the current search result id.
      const node = this.searchData.nodesByMid[parseInt(nodeId, 10)];
      console.assert(!!node, "node must be defined for result: " +
        nodeId);

      // Build the HTML fragment with node fields, applying term highlighting
      // to every visible field except the navigation link field.
      let nodeFieldsHtml = "";
      Object.entries(node).forEach(([key, value]) => {
        if (value === "" || key === "_LINK") {
          return;
        }

        for (let i = 0; i < this.highlightElements.length; i++) {
          const highlightElement = this.highlightElements[i];
          value = highlightWord(value, highlightElement);
        }

        nodeFieldsHtml = nodeFieldsHtml +
          `<div class="static_search-result-node-field"><span class="static_search-result-node-field-key">${key}:</span> ${value}</div>`;
      });

      const pathPrefix = (this.documentLevel === 0) ? "" : "../".repeat(
        this.documentLevel);

      // Render the visible result entry together with the deep link to the node.
      const nodeLink = node["_LINK"];

      resultElement.innerHTML = `<div class="static_search-result-node">
      ${nodeFieldsHtml}
      <div class="static_search-result-node-link">
          <a href="${pathPrefix}index.html?a=${nodeLink}">Go to node →</a>
      </div>
      </div>
      `;
    }

    selectNextResult() {
      if (this.selectedIndex < (this.suggestions.childNodes.length - 1)) {
        this._selectResult(this.selectedIndex + 1);
      }
    }

    selectPreviousResult() {
      if (this.selectedIndex > 0) {
        this._selectResult(this.selectedIndex - 1);
      }
    }

    acceptSuggestion(event) {
      // Nothing for now.
    }

    _selectResult(index) {
      let node = this.suggestions.childNodes[this.selectedIndex];
      node && (node.style.backgroundColor = "");

      this.selectedIndex = index;

      node = this.suggestions.childNodes[index];
      node && (node.style.backgroundColor = "rgba(0, 0, 255, 0.1)");
    }
  }

  // Orchestrate user input events and translate them into search updates.
  class SearchInputController {
    constructor({ userinput, searchData, searchResultsView }) {
      this.userinput = userinput;
      this.searchData = searchData;
      this.searchResultsView = searchResultsView;
      this.previousInputValue = "";
    }

    attachEventListeners() {
      this.userinput.addEventListener("input", () => this.handleInput(), true);
      this.userinput.addEventListener("keyup", (event) => this.handleKeyUp(
        event), true);
      this.userinput.addEventListener("keydown", (event) => this.handleKeyDown(
        event), true);
      this.userinput.addEventListener("focus", (event) => this.handleFocus(
        event), true);
    }

    handleInput() {
      // Wait until the search index and node lookup map are loaded.
      // TODO: Replace this per-input guard with an explicit "search index ready"
      // state and a visible UI signal for the user when live search is not ready yet.
      if (!this.searchData.index || !this.searchData.nodesByMid) {
        console.log(
          "Search: Cannot perform search: Search index is not available yet.")
        return;
      }

      // Reset the live search UI when the input becomes empty.
      if (this.userinput.value === "") {
        this.previousInputValue = "";
        this.searchResultsView.hideResults();
        return;
      }

      // Preserve the current live-input behavior for quote editing.
      // FIXME
      // If the previous input step already auto-inserted "" and the user has
      // edited the field back down to a single quote, treat that as deleting
      // the auto-completed quote pair and clear the field completely.
      if (this.previousInputValue === '""' && this.userinput.value === '"') {
        this.userinput.value = ""
      // If the user has typed a single quote into an otherwise empty field,
      // auto-insert the matching closing quote.
      } else if (this.userinput.value === '"') {
        const quote = this.userinput.value;
        this.userinput.value = quote + quote;

        // Place the cursor between the two quotes
        // so the next typed characters become the quoted phrase.
        this.userinput.setSelectionRange(1, 1);
      }

      // Persist the latest input value for the next edit step.
      this.previousInputValue = this.userinput.value;

      // Build the normalized search query from the current input.
      const searchQuery = this.userinput.value.toLowerCase();

      // Parse the query and build the view model shown in the live results list.
      const parsedQuery = parseSearchQuery(searchQuery);

      const searchViewModel = buildSearchViewModel(
        parsedQuery,
        searchQuery,
        this.searchData.index,
        this.searchData.nodesByMid
      );
      this.searchResultsView.populateResults(
        searchViewModel.results,
        searchViewModel.highlightElements
      );
    }

    handleKeyDown(event) {
      if (event && event.key === "Enter") {
        event.preventDefault && event.preventDefault();
        const searchQuery = this.userinput.value || "";
        const encodedQuery = encodeURIComponent(searchQuery);
        window.location.assign(`/search?q=${encodedQuery}`);
      }
    }

    handleFocus(event) {
      // FIXME: Nothing for now.
    }

    handleKeyUp(event) {
      if (event) {
        const key = event.key;
        if (key === "ArrowUp") {
          this.searchResultsView.selectPreviousResult();
          event.preventDefault && event.preventDefault();
          return;
        }
        if (key === "ArrowDown") {
          this.searchResultsView.selectNextResult();
          event.preventDefault && event.preventDefault();
          return;
        }
      }
    }
  }

  // =========================================================================
  // Search index initialization
  // =========================================================================

  // Open the IndexedDB database that caches the generated search index.
  function openSearchIndexDB(name, version = 1) {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(name, version);
      request.onupgradeneeded = (e) => {
        const db = e.target.result;
        db.createObjectStore("indexes", {
          keyPath: "name"
        });
      };
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  // Drop the cached search index when it becomes stale.
  function deleteSearchIndexDB(name) {
    return new Promise((resolve, reject) => {
      const delReq = indexedDB.deleteDatabase(name);
      delReq.onsuccess = () => resolve();
      delReq.onerror = () => reject(delReq.error);
    });
  }

  // Read a cached value from the search index store.
  function getFromSearchIndexStore(db, storeName, key) {
    return new Promise((resolve, reject) => {
      const tx = db.transaction(storeName, "readonly");
      const store = tx.objectStore(storeName);
      const req = store.get(key);
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    });
  }

  // Persist the current search index payload to the cache store.
  function saveToSearchIndexStore(db, storeName, items) {
    return new Promise((resolve, reject) => {
      const tx = db.transaction(storeName, "readwrite");
      const store = tx.objectStore(storeName);
      items.forEach((item) => store.put(item));
      tx.oncomplete = () => resolve();
      tx.onerror = () => reject(tx.error);
    });
  }

  // Load the generated search index JavaScript file into the page.
  function loadScript(url) {
    return new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = url;
      script.onload = () => {
        script.remove();
        resolve();
      };
      script.onerror = () => reject(new Error(
        `Failed to load script ${url}`));
      document.head.appendChild(script);
    });
  }

  // Load the generated search index, optionally bypassing the browser cache.
  async function loadSearchIndexFromScript(pathToSearchIndex, cacheBusting) {
    const searchIndexURL = new URL(pathToSearchIndex, window.location.href);
    if (cacheBusting) {
      searchIndexURL.searchParams.set("_refresh", Date.now().toString());
    }
    console.time("Search: LOAD_JS_INDEX");
    await loadScript(searchIndexURL.href);
    console.timeEnd("Search: LOAD_JS_INDEX");
    console.log("Search: JS search index loaded successfully.");
  }

  // Save the in-memory search index into IndexedDB for faster reloads.
  async function saveCurrentSearchIndexToDB({
    dbName,
    dbVersion,
    timestampMeta,
    searchData,
  }) {
    console.time("Search: SAVE_DB_INDEX");
    const db = await openSearchIndexDB(dbName, dbVersion);
    await saveToSearchIndexStore(db, "indexes", [{
      name: "STRICTDOC_SEARCH_INDEX",
      value: searchData.index
    }, {
      name: "STRICTDOC_SEARCH_NODES_BY_MID",
      value: searchData.nodesByMid
    }, {
      name: "TIMESTAMP",
      value: timestampMeta
    }, ]);
    db.close();
    console.timeEnd("Search: SAVE_DB_INDEX");
  }

  // Refresh the cached search index after relevant Turbo stream updates.
  function installSearchIndexRefreshHandler({
    pathToSearchIndex,
    dbName,
    dbVersion,
    timestampMeta,
    searchData,
  }) {
    let refreshScheduled = false;
    let refreshInProgress = false;
    let refreshQueued = false;

    const refreshSearchIndexFromServer = async () => {
      if (refreshInProgress) {
        refreshQueued = true;
        return;
      }

      refreshInProgress = true;
      try {
        await loadSearchIndexFromScript(pathToSearchIndex, true);
        await saveCurrentSearchIndexToDB({
          dbName,
          dbVersion,
          timestampMeta,
          searchData,
        });
      } catch (refreshError) {
        console.error(
          "Search: Failed to refresh search index after Turbo stream update:",
          refreshError
        );
      } finally {
        refreshInProgress = false;
        if (refreshQueued) {
          refreshQueued = false;
          void refreshSearchIndexFromServer();
        }
      }
    };

    const scheduleRefreshSearchIndexFromServer = () => {
      if (refreshScheduled) {
        return;
      }
      refreshScheduled = true;
      window.setTimeout(() => {
        refreshScheduled = false;
        void refreshSearchIndexFromServer();
      }, 0);
    };

    document.addEventListener("turbo:before-stream-render", (event) => {
      const streamElement = event.target;
      if (!(streamElement instanceof HTMLElement)) {
        return;
      }
      if (streamElement.tagName !== "TURBO-STREAM") {
        return;
      }
      const target = streamElement.getAttribute("target");
      // FIXME: HACK: For now we refresh the entire index on any update to the TOC.
      // Ideally we should get a dedicated stream update for the search index
      // and only refresh on that. But this will do for now.
      if (target === "frame-toc") {
        scheduleRefreshSearchIndexFromServer();
      }
    }, true);
  }

  // Initialize the search index from cache or from the generated script.
  async function initializeSearchIndex({
    projectHash,
    pathToSearchIndex,
    timestampMeta,
    searchData,
  }) {
    const DB_VERSION = 1;
    const dbName = "strictdoc_search_index_" + projectHash;

    installSearchIndexRefreshHandler({
      pathToSearchIndex,
      dbName,
      dbVersion: DB_VERSION,
      timestampMeta,
      searchData,
    });

    try {
      console.log("Search: LOAD_DB_INDEX: Start");
      const db = await openSearchIndexDB(dbName, DB_VERSION);
      const tsEntry = await getFromSearchIndexStore(db, "indexes", "TIMESTAMP");

      if (tsEntry && tsEntry.value === timestampMeta) {
        console.time("Search: LOAD_DB_INDEX");
        const lunrEntry = await getFromSearchIndexStore(
          db,
          "indexes",
          "STRICTDOC_SEARCH_INDEX"
        );
        const nodesEntry = await getFromSearchIndexStore(
          db,
          "indexes",
          "STRICTDOC_SEARCH_NODES_BY_MID"
        );
        console.timeEnd("Search: LOAD_DB_INDEX");

        if (lunrEntry && nodesEntry) {
          searchData.index = lunrEntry.value;
          searchData.nodesByMid = nodesEntry.value;
          db.close();
          return;
        }
      }

      db.close();
      await deleteSearchIndexDB(dbName);

      try {
        await loadSearchIndexFromScript(pathToSearchIndex, false);
      } catch (e) {
        console.error("Search: Failed to load JS search index script:",
          e);
        return;
      }

      await saveCurrentSearchIndexToDB({
        dbName,
        dbVersion: DB_VERSION,
        timestampMeta,
        searchData,
      });

    } catch (err) {
      console.error("Search: Error loading search index:", err);

      try {
        await loadSearchIndexFromScript(pathToSearchIndex, false);
        console.log("Search: Script loaded without IndexedDB fallback");
      } catch (e) {
        console.error("Search: Failed to load search index script:", e);
      }
    }
  }

  // =========================================================================
  // App initialization
  // =========================================================================

  // Initialize the UI controllers after all required DOM and meta are present.
  const { dom, missingSelectors } = collectRequiredDom();
  const { meta, missingSelectors: missingMetaSelectors } = collectRequiredMeta();

  if (missingSelectors.length > 0) {
    console.assert(
      false,
      `Search: initialization skipped because required DOM elements are missing: ${missingSelectors.join(", ")}`
    );
    return;
  }

  if (missingMetaSelectors.length > 0) {
    console.assert(
      false,
      `Search: initialization skipped because required meta tags are missing: ${missingMetaSelectors.join(", ")}`
    );
    return;
  }

  const { userinput } = dom;
  const documentLevel = parseInt(meta.documentLevel, 10);

  const searchResultsView = new SearchResultsView(dom, {
    userinput,
    searchData: strictDocSearch,
    documentLevel,
  });
  const searchInputController = new SearchInputController({
    userinput,
    searchData: strictDocSearch,
    searchResultsView,
  });
  searchInputController.attachEventListeners();

  // Defer search index initialization until the page and generated assets are ready.
  window.addEventListener("load", async () => {
    const timestampMeta = meta.searchIndexTimestamp;
    const projectHash = meta.projectHash;
    const pathToSearchIndex = meta.searchIndexPath;

    if (!projectHash || !pathToSearchIndex || !timestampMeta) {
      console.error("Search: Missing required meta tags!");
      return;
    }
    await initializeSearchIndex({
      projectHash,
      pathToSearchIndex,
      timestampMeta,
      searchData: strictDocSearch,
    });
  });
})();
