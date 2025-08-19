class SearchResultsView {
    static PAGE_SIZE = 3;

    constructor() {
        const metaDocumentLevel = document.querySelector('meta[name="strictdoc-document-level"]')?.content;
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

        this.navigationStart = document.querySelector("#results_navigation #start");
        this.navigationPrevious = document.querySelector("#results_navigation #previous");
        this.navigationNext = document.querySelector("#results_navigation #next");
        this.navigationEnd = document.querySelector("#results_navigation #end");

        this.navigationStart.addEventListener("click", () => this.displayPage(1), true);
        this.navigationPrevious.addEventListener("click", () => this.displayPage(this.currentPage - 1), true);
        this.navigationNext.addEventListener("click", () => this.displayPage(this.currentPage + 1), true);
        this.navigationEnd.addEventListener("click", () => this.displayPage(Math.ceil(this.results.length / SearchResultsView.PAGE_SIZE)), true);

        this.selectedIndex = 0;
        this.results = null;
        this.currentPage = 1;
        suggestions.addEventListener("click", this.acceptSuggestion, true);
        document.addEventListener("keydown", (event) => this.handleEscape(event), true);
    }

    handleEscape(event) {
        if (event.key === "Escape") {
            this.hideResults();
            // On Esc, remove focus from the input field.
            // Otherwise the field remains focused and a subsequent click won't fire a 'focus' event,
            // so the search won't restart. Blurring ensures the next refocus re‑triggers search with
            // the existing text.
            if (typeof userinput !== "undefined" && document.activeElement === userinput) {
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

    populateResults(results) {
        const resultsLength = results.length;

        if (resultsLength == 0) {
            this.suggestions.replaceChildren();
            this.resultsCount.innerHTML = `No results.`;
            return;
        }

        let uniqueResults = [];
        let mapMIDtoResult = {};
        for (let i = 0; i < resultsLength; i++) {
            const result = results[i];

            let displayResult = null;
            if (!(result.ref in mapMIDtoResult)) {
                uniqueResults.push(result);
                mapMIDtoResult[result.ref] = displayResult;
            }
            if (uniqueResults.length >= 25) {
                break;
            }
        }

        this.results = uniqueResults;

        this.displayPage(1);

        this.searchBox.setAttribute("active", "");
    }

    displayPage(page) {
        if (page < 1 || page > Math.ceil(this.results.length / SearchResultsView.PAGE_SIZE)) {
            return;
        }

        const pageResults = this.results.slice(
            (page - 1) * SearchResultsView.PAGE_SIZE,
            page * SearchResultsView.PAGE_SIZE
        );

        this.currentPage = page;

        const children = this.suggestions.childNodes;

        for (let i = 0; i < pageResults.length; i++){
            let flatResult = pageResults[i];
            let entry = children[i];

            if (!entry){
                entry = document.createElement("div");
                suggestions.appendChild(entry);
            }

            const node = window.SDOC_MAP_MID_TO_NODES[flatResult.ref];
            let node_key_values = "";
            Object.entries(node).forEach(([key, value]) => {
                if (key === "MID" || value === "") {
                    return;
                }
                node_key_values = node_key_values + `<div class="static_search-result-node-field"><span class="static_search-result-node-field-key">${key}:</span> ${value}</div>`;
            });

            const pathPrefix = (this.documentLevel === 0) ? "" : "../".repeat(this.documentLevel);

            entry.innerHTML = `<div class="static_search-result-node">
    ${node_key_values}
    <div class="static_search-result-node-link">
        <a href="${pathPrefix}index.html?a=${node["UID"]}">Go to node →</a>
    </div>
    </div>
    `;

        }

        while (children.length > pageResults.length){
            this.suggestions.removeChild(this.suggestions.lastChild);
        }

        const rangeStart = (page - 1) * SearchResultsView.PAGE_SIZE + 1;
        const rangeEnd = Math.min(page * SearchResultsView.PAGE_SIZE, this.results.length);

        if (this.results.length > SearchResultsView.PAGE_SIZE) {
            if (page < 2) {
                this.navigationStart.setAttribute("disabled", "");
                this.navigationPrevious.setAttribute("disabled", "");
            } else {
                this.navigationStart.removeAttribute("disabled");
                this.navigationPrevious.removeAttribute("disabled");
            }
            if (page >= Math.ceil(this.results.length / SearchResultsView.PAGE_SIZE)) {
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
        console.log("acceptSuggestion");
        const target = (event || window.event).target;
        userinput.value = target.textContent;
        suggestions.textContent = "";
        return false;
    }

    _selectResult(index) {
        let node = this.suggestions.childNodes[this.selectedIndex];
        node && (node.style.backgroundColor = "");

        this.selectedIndex = index;

        node = this.suggestions.childNodes[index];
        node && (node.style.backgroundColor = "rgba(0, 0, 255, 0.1)");
    }
}

let idx = lunr.Index.load(window.SDOC_LUNR_SEARCH_INDEX);

const userinput = document.getElementById("userinput");
userinput.addEventListener("input", handleInputEvent_input, true);
userinput.addEventListener("keyup", handleInputEvent_keyUp, true);
userinput.addEventListener("keydown", handleInputEvent_keyDown, true);
userinput.addEventListener("focus", handleInputEvent_focus, true);

const searchResultsView = new SearchResultsView();

function handleInputEvent_input(){
    if (userinput.value === "") {
        // searchResultsView.clearResults
        searchResultsView.hideResults();
        return;
    }

    console.log("User input: " + userinput.value);

    let results = idx.search(userinput.value);
    searchResultsView.populateResults(results);
}

function handleInputEvent_keyDown(event) {
    // FIXME
    // const keyCode = (event || window.event).keyCode;
    // if (keyCode === 13) {
    //     event.preventDefault && event.preventDefault();
    //     const node = suggestions.childNodes[selectedIndex];
    //     if (!node) {
    //         return;
    //     }
    //     userinput.value = node.textContent;
    //     suggestions.textContent = "";
    //     return;
    // }
}

function handleInputEvent_focus(event) {
    if (userinput.value !== "") {
        let results = idx.search(userinput.value);
        searchResultsView.populateResults(results);
    }
}

function handleInputEvent_keyUp(event) {
    if(event){
        const key = event.key;
        if (key === "ArrowUp") {
            searchResultsView.selectPreviousResult();
            event.preventDefault && event.preventDefault();
            return;
        }
        if(key === "ArrowDown"){
            searchResultsView.selectNextResult();
            event.preventDefault && event.preventDefault();
            return;
        }
    }
}
