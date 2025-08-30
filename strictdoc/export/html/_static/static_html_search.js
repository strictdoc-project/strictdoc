/**
 * @relation(SDOC-SRS-155, scope=file)
 * @relation(SDOC-SRS-156, scope=file)
 */

(function() {
  function highlightWord(text, word) {
    let newStr = text.replace(new RegExp(word, "gi"), (match) => "<mark>" +
      match + "</mark>");
    return newStr;
  }

  function intersectSets(sets) {
    if (sets.length === 0) return new Set();

    let intersection = new Set(sets[0]);

    for (const s of sets.slice(1)) {
      intersection = new Set([...intersection].filter(x => s.has(x)));
    }

    return intersection;
  }

  class SearchResultsView {
    static PAGE_SIZE = 5;

    constructor() {
      const metaDocumentLevel = document.querySelector(
        'meta[name="strictdoc-document-level"]')?.content;
      console.assert(
        metaDocumentLevel,
        "SearchResultsView: strictdoc-document-level meta tag is missing."
      );

      this.documentLevel = parseInt(metaDocumentLevel, 10);
      console.assert(
        !isNaN(this.documentLevel),
        "SearchResultsView: strictdoc-document-level meta tag is not a valid number."
      );

      this.searchBox = document.getElementById("search");
      this.searchResults = document.getElementById("search_results");
      this.resultsCount = document.getElementById("results_count");
      this.suggestions = document.getElementById("suggestions");

      this.navigationStart = document.querySelector(
        "#results_navigation #start");
      this.navigationPrevious = document.querySelector(
        "#results_navigation #previous");
      this.navigationNext = document.querySelector(
        "#results_navigation #next");
      this.navigationEnd = document.querySelector(
        "#results_navigation #end");

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
      suggestions.addEventListener("click", this.acceptSuggestion, true);
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
        if (typeof userinput !== "undefined" && document.activeElement ===
          userinput) {
          userinput.blur();
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
      if (page < 1 || page > Math.ceil(this.results.length /
          SearchResultsView.PAGE_SIZE)) {
        return;
      }

      const pageResults = this.results.slice(
        (page - 1) * SearchResultsView.PAGE_SIZE,
        page * SearchResultsView.PAGE_SIZE
      );

      this.currentPage = page;

      const children = this.suggestions.childNodes;

      for (let i = 0; i < pageResults.length; i++) {
        let flatResult = pageResults[i];
        let entry = children[i];

        if (!entry) {
          entry = document.createElement("div");
          suggestions.appendChild(entry);
        }

        const node = window.SDOC_MAP_MID_TO_NODES[parseInt(flatResult, 10)];
        console.assert(!!node, "node must be defined for result: " +
          flatResult);

        let node_key_values = "";
        Object.entries(node).forEach(([key, value]) => {
          if (value === "" || key === "_LINK") {
            return;
          }

          for (let i = 0; i < this.highlightElements.length; i++) {
            const highlightElement = this.highlightElements[i];
            value = highlightWord(value, highlightElement);
          }

          node_key_values = node_key_values +
            `<div class="static_search-result-node-field"><span class="static_search-result-node-field-key">${key}:</span> ${value}</div>`;
        });

        const pathPrefix = (this.documentLevel === 0) ? "" : "../".repeat(
          this.documentLevel);

        const nodeLink = node["_LINK"];

        entry.innerHTML = `<div class="static_search-result-node">
      ${node_key_values}
      <div class="static_search-result-node-link">
          <a href="${pathPrefix}index.html?a=${nodeLink}">Go to node →</a>
      </div>
      </div>
      `;

      }

      while (children.length > pageResults.length) {
        this.suggestions.removeChild(this.suggestions.lastChild);
      }

      const rangeStart = (page - 1) * SearchResultsView.PAGE_SIZE + 1;
      const rangeEnd = Math.min(page * SearchResultsView.PAGE_SIZE, this
        .results.length);

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

      this.resultsCount.innerHTML = `\
  Results: <b>${rangeStart}–${rangeEnd}</b> from ${this.results.length}
  `;

      this._selectResult(0);
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

  const userinput = document.getElementById("userinput");
  userinput.dataset.prevValue = "";

  userinput.addEventListener("input", handleInputEvent_input, true);
  userinput.addEventListener("keyup", handleInputEvent_keyUp, true);
  userinput.addEventListener("keydown", handleInputEvent_keyDown, true);
  userinput.addEventListener("focus", handleInputEvent_focus, true);

  const searchResultsView = new SearchResultsView();

  function handleInputEvent_input() {
    if (!window.SDOC_SEARCH_INDEX || !window.SDOC_MAP_MID_TO_NODES) {
      console.log(
        "Search: Cannot perform search: Search index is not available yet.")
      return;
    }

    if (userinput.value === "") {
      userinput.dataset.prevValue = "";
      searchResultsView.hideResults();
      return;
    }

    // FIXME
    if (userinput.dataset.prevValue === '""' && userinput.value === '"') {
      userinput.value = ""
    } else if (userinput.value === '"') {
      const quote = userinput.value;
      userinput.value = quote + quote;

      // Place cursor between the two quotes.
      userinput.setSelectionRange(1, 1);
    }

    userinput.dataset.prevValue = userinput.value;

    const searchQuery = userinput.value.toLowerCase();

    const regex = /"([^"]+)"|(\S+)/g;
    let tokens = [];
    let hasQuoted = false;
    let queryDict = {};

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
      // At least one quoted phrase: treat each group as AND
      queryDict = {
        mode: "AND",
        terms: tokens.flat()
      };
    } else {
      // No quoted phrases: just OR everything
      queryDict = {
        mode: "OR",
        terms: tokens.flat()
      };
    }

    let results = [];

    if (queryDict["mode"] === "OR") {
      if (!searchQuery.includes('"')) {
        let uniqueResults = new Set();
        for (const token of queryDict["terms"]) {
          const tokenResults = window.SDOC_SEARCH_INDEX[token];
          if (tokenResults) {
            uniqueResults = new Set([...uniqueResults, ...tokenResults]);
          }
        }
        results.push(...uniqueResults);
      }
    } else {
      const firstTerm = queryDict["terms"][0];
      const firstTermResults = window.SDOC_SEARCH_INDEX[firstTerm];
      if (firstTermResults && firstTermResults.length > 0) {
        let uniqueResults = new Set(firstTermResults);

        if (queryDict["terms"].length > 1) {
          for (let i = 1; i < queryDict["terms"].length; i++) {
            const termResults = window.SDOC_SEARCH_INDEX[queryDict["terms"][
              i
            ]];
            const termUniqueResults = new Set(termResults);

            uniqueResults = intersectSets([uniqueResults, termUniqueResults]);
            if (uniqueResults.size === 0) {
              break;
            }
          }
        }

        results = Array.from(uniqueResults);
      }
    }

    if (results) {
      let highlightElements = null;
      if (queryDict["mode"] === "OR") {
        highlightElements = queryDict["terms"];
      } else {
        let finalAndResults = [];
        let finalUniqueResults = new Set();
        const andQuery = queryDict["terms"].join(" ");
        highlightElements = [andQuery];

        for (const result of results) {
          const node = window.SDOC_MAP_MID_TO_NODES[parseInt(result, 10)];
          console.assert(!!node, "node must be defined for result: " +
            result);


          let node_key_values = "";
          Object.entries(node).forEach(([key, value]) => {
            if (value === "") {
              return;
            }

            if (!finalUniqueResults.has(result) && value.toLowerCase()
              .includes(andQuery)) {
              finalUniqueResults.add(result);
              finalAndResults.push(result);
            }
          });
        }

        results = finalAndResults;
      }
      searchResultsView.populateResults(results, highlightElements);
    } else {
      searchResultsView.populateResults([], null);
    }
  }

  function handleInputEvent_keyDown(event) {
    // FIXME: Nothing for now.
  }

  function handleInputEvent_focus(event) {
    // FIXME: Nothing for now.
  }

  function handleInputEvent_keyUp(event) {
    if (event) {
      const key = event.key;
      if (key === "ArrowUp") {
        searchResultsView.selectPreviousResult();
        event.preventDefault && event.preventDefault();
        return;
      }
      if (key === "ArrowDown") {
        searchResultsView.selectNextResult();
        event.preventDefault && event.preventDefault();
        return;
      }
    }
  }

  window.addEventListener("load", async () => {
    const DB_VERSION = 1;
    const timestampMeta = document.querySelector(
      'meta[name="strictdoc-search-index-timestamp"]'
    )?.content;
    const projectHash = document.querySelector(
      'meta[name="strictdoc-project-hash"]'
    )?.content;
    const pathToSearchIndex = document.querySelector(
      'meta[name="strictdoc-search-index-path"]'
    )?.content;

    if (!projectHash || !pathToSearchIndex || !timestampMeta) {
      console.error("Search: Missing required meta tags!");
      return;
    }

    const dbName = "strictdoc_search_index_" + projectHash;

    const openDB = (name, version = 1) =>
      new Promise((resolve, reject) => {
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

    const deleteDB = (name) =>
      new Promise((resolve, reject) => {
        const delReq = indexedDB.deleteDatabase(name);
        delReq.onsuccess = () => resolve();
        delReq.onerror = () => reject(delReq.error);
      });

    const getFromStore = (db, storeName, key) =>
      new Promise((resolve, reject) => {
        const tx = db.transaction(storeName, "readonly");
        const store = tx.objectStore(storeName);
        const req = store.get(key);
        req.onsuccess = () => resolve(req.result);
        req.onerror = () => reject(req.error);
      });

    const saveToStore = (db, storeName, items) =>
      new Promise((resolve, reject) => {
        const tx = db.transaction(storeName, "readwrite");
        const store = tx.objectStore(storeName);
        items.forEach((item) => store.put(item));
        tx.oncomplete = () => resolve();
        tx.onerror = () => reject(tx.error);
      });

    const loadScript = (url) =>
      new Promise((resolve, reject) => {
        const script = document.createElement("script");
        script.src = url;
        script.onload = () => resolve();
        script.onerror = () => reject(new Error(
          `Failed to load script ${url}`));
        document.head.appendChild(script);
      });

    try {
      console.log("Search: LOAD_DB_INDEX: Start");
      const db = await openDB(dbName, DB_VERSION);
      const tsEntry = await getFromStore(db, "indexes", "TIMESTAMP");

      if (tsEntry && tsEntry.value === timestampMeta) {

        console.time("Search: LOAD_DB_INDEX");
        const lunrEntry = await getFromStore(db, "indexes",
          "SDOC_SEARCH_INDEX");
        const nodesEntry = await getFromStore(db, "indexes",
          "SDOC_MAP_MID_TO_NODES");
        console.timeEnd("Search: LOAD_DB_INDEX");

        if (lunrEntry && nodesEntry) {
          window.SDOC_SEARCH_INDEX = lunrEntry.value;
          window.SDOC_MAP_MID_TO_NODES = nodesEntry.value;
          return;
        }
      }

      db.close();
      await deleteDB(dbName);

      try {
        console.time("Search: LOAD_JS_INDEX");
        await loadScript(new URL(pathToSearchIndex, window.location
          .href).href);
        console.timeEnd("Search: LOAD_JS_INDEX");
        console.log("Search: JS search index loaded successfully.");
      } catch (e) {
        console.error("Search: Failed to load JS search index script:",
          e);
        return;
      }

      console.time("Search: SAVE_DB_INDEX");
      const newDB = await openDB(dbName, DB_VERSION);
      await saveToStore(newDB, "indexes", [{
        name: "SDOC_SEARCH_INDEX",
        value: window.SDOC_SEARCH_INDEX
      }, {
        name: "SDOC_MAP_MID_TO_NODES",
        value: window.SDOC_MAP_MID_TO_NODES
      }, {
        name: "TIMESTAMP",
        value: timestampMeta
      }, ]);
      console.timeEnd("Search: SAVE_DB_INDEX");

    } catch (err) {
      console.error("Search: Error loading search index:", err);

      try {
        await loadScript(new URL(pathToSearchIndex, window.location
          .href).href);
        console.log("Search: Script loaded without IndexedDB fallback");
      } catch (e) {
        console.error("Search: Failed to load search index script:", e);
      }
    }
  });
})();
