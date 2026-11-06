
/*
 * RST Editor for StrictDoc
 *
 * - Keeps the StrictDoc contenteditable element in its original DOM position.
 * - Places table highlights in a fixed overlay under document.body.
 * - Supports editing reStructuredText grid tables.
 * - Adds a toolbar for inserting tables.
 * - Initializes editor for dynamically inserted StrictDoc fields.
 */

class RSTEditor {
    constructor(textarea, options = {}) {
        if (typeof textarea === "string") {
            textarea = document.querySelector(textarea);
        }

        if (!textarea || !textarea.ownerDocument) {
            throw new TypeError(
                "RSTEditor requires an editable DOM element."
            );
        }

        this.textarea = textarea;

        this.options = {
            highlightTables: true,
            editable: true,
            ...options
        };

        this.elements = [];
        this.activeElement = null;

        this.editorWindow = null;
        this.contextMenu = null;
        this.destroyed = false;

        this._resizeObserver = null;
        this._dragCleanup = null;

        // Retained for compatibility; this class does not move the field.
        this._originalParent = textarea.parentNode;
        this._originalNextSibling = textarea.nextSibling;
        this._originalStyle = textarea.getAttribute("style");

        this._buildDOM();
        this._bindEvents();

        this.innerSave = this.textarea.innerHTML;


        this.refresh();

        this._watchForRemoval();

    }

    /* --------------------------------------------------
       DOM initialization and events
    -------------------------------------------------- */

    _buildDOM() {
        const doc = this.textarea.ownerDocument;
        const win = doc.defaultView;

        if (!doc.body) {
            throw new Error(
                "Cannot initialize RSTEditor: document.body is unavailable."
            );
        }

        /*
         * The wrapper is an independent, viewport-sized overlay.
         * Never append children to or move the StrictDoc editable element.
         */
        this.wrapper = doc.createElement("div");
        this.wrapper.className = "rst-table-wrapper";

        Object.assign(this.wrapper.style, {
            position: "fixed",
            inset: "0",
            width: "100%",
            height: "100%",
            overflow: "visible",
            pointerEvents: "none",
            zIndex: "1000"
        });

        this.overlay = doc.createElement("div");
        this.overlay.className = "rst-table-overlay";

        Object.assign(this.overlay.style, {
            position: "absolute",
            inset: "0",
            width: "100%",
            height: "100%",
            overflow: "visible",
            pointerEvents: "none"
        });

        this.wrapper.appendChild(this.overlay);
        doc.body.appendChild(this.wrapper);

        // Range.getBoundingClientRect() returns viewport coordinates.
        this._positionWrapper = () => {
            if (this.destroyed || !this.textarea.isConnected) return;
            this._positionHighlights();
        };

        this._onWindowResize = this._positionWrapper;
        this._onWindowScroll = this._positionWrapper;

        win?.addEventListener("resize", this._onWindowResize);
        win?.addEventListener("scroll", this._onWindowScroll, true);

        const ResizeObserverClass = win?.ResizeObserver;

        this._resizeObserver = ResizeObserverClass
            ? new ResizeObserverClass(this._positionWrapper)
            : null;

        this._resizeObserver?.observe(this.textarea);
    }

    _watchForRemoval() {
        const element = this.textarea;
        const doc = element.ownerDocument;

        this._removalObserver?.disconnect();

        this._removalObserver = new MutationObserver(() => {
            // isConnected is false when the element is detached from the document.
            if (!element.isConnected) {
                // The editable field was removed; release its resources.
                this._removalObserver.disconnect();
                this._removalObserver = null;

                this.destroy();
            }
        });

        this._removalObserver.observe(doc.documentElement, {
            childList: true,
            subtree: true
        });
    }

    _destroyHighlights() {
        if (this.overlayWrapper) {
            this.overlayWrapper.remove();
            this.overlayWrapper = null;
            this.overlay = null;
        }

        this.highlights = [];
        this.activeElement = null;
    }


    _bindEvents() {
        this._onInput = () => this.refresh();
        this._onScroll = () => this._positionHighlights();

        this._onKeyDown = event => {
            if (event.key === "Escape") {
                this.closeEditor();
            }
        };

        this._onDocumentClick = event => {
            if (
                this.contextMenu &&
                !this.contextMenu.contains(event.target)
            ) {
                this._hideContextMenu();
            }
        };

        this.textarea.addEventListener("input", this._onInput);
        this.textarea.addEventListener("scroll", this._onScroll);
        this.textarea.addEventListener("keydown", this._onKeyDown);

        this.textarea.ownerDocument.addEventListener(
            "click",
            this._onDocumentClick
        );
    }

    /* --------------------------------------------------
       Source helpers
    -------------------------------------------------- */

    _getSourceText() {
        /*
         * The field is expected to contain plain RST text.
         * innerText handles rendered line breaks better than innerHTML
         * when the editable contains normal text nodes and line breaks.
         */
        return this.textarea.innerText.replace(/\r\n?/g, "\n");
    }

    _getSourceLines() {
        return this._getSourceText().split("\n");
    }

    _dispatchSourceChange() {
        /*
         * Set the baseline before dispatching input so the listener's
         * refresh does not recursively emit another input event.
         */
        this.innerSave = this.textarea.innerHTML;

        const win = this.textarea.ownerDocument.defaultView;
        const InputEventClass = win?.InputEvent;

        if (InputEventClass) {
            this.textarea.dispatchEvent(
                new InputEventClass("input", {
                    bubbles: true,
                    inputType: "insertText",
                    data: null
                })
            );
        } else {
            this.textarea.dispatchEvent(
                new Event("input", { bubbles: true })
            );
        }

        this.textarea.dispatchEvent(
            new Event("change", { bubbles: true })
        );
    }

    _replaceSource(source) {
        /*
         * Replace the editable's content with a text node, not HTML.
         * This prevents RST characters from being interpreted as markup.
         */
        const doc = this.textarea.ownerDocument;
        this.textarea.replaceChildren(
            doc.createTextNode(source)
        );

        this.refresh();
        this._dispatchSourceChange();
    }

    /* --------------------------------------------------
       Table detection and parsing
    -------------------------------------------------- */

    _isBorder(line) {
        return /^\s*\+[-=+]+\+\s*$/.test(line);
    }

    _isRow(line) {
        return /^\s*\|.*\|\s*$/.test(line);
    }

    _isTableLine(line) {
        return this._isBorder(line) || this._isRow(line);
    }

    _isHeaderBorder(line) {
        return line.includes("=") && this._isBorder(line);
    }

    _parseTable(lines, startLine, endLine) {
        const tableLines = lines.slice(startLine, endLine + 1);

        if (tableLines.length < 4) return null;

        const headerSeparatorIndex = tableLines.findIndex(
            (line, index) =>
                index > 0 && this._isHeaderBorder(line)
        );

        if (headerSeparatorIndex < 0) return null;

        let headerLineIndex = -1;

        for (let i = headerSeparatorIndex - 1; i >= 0; i--) {
            if (this._isRow(tableLines[i])) {
                headerLineIndex = i;
                break;
            }
        }

        if (headerLineIndex < 0) return null;

        const splitRow = line =>
            line.trim()
                .slice(1, -1)
                .split("|")
                .map(cell => cell.trim());

        const headers = splitRow(tableLines[headerLineIndex]);
        const data = [];

        for (
            let i = headerSeparatorIndex + 1;
            i < tableLines.length;
            i++
        ) {
            if (this._isRow(tableLines[i])) {
                data.push(splitRow(tableLines[i]));
            }
        }

        if (!headers.length) return null;

        if (data.some(row => row.length !== headers.length)) {
            return null;
        }

        return {
            startLine,
            endLine,
            headers,
            data,
            highlight: null,
            type: "table"
        };
    }

    refresh() {
        if (this.destroyed) return;

        const oldActiveIndex = this.activeElement
            ? this.activeElement.index
            : -1;

        this._removeHighlights();

        const lines = this._getSourceLines();

        // Detect contiguous grid-table line ranges.
        const tableRanges = [];
        let start = -1;

        for (let i = 0; i < lines.length; i++) {
            if (this._isTableLine(lines[i])) {
                if (start === -1) start = i;
            } else if (start !== -1) {
                tableRanges.push([start, i - 1]);
                start = -1;
            }
        }

        if (start !== -1) {
            tableRanges.push([start, lines.length - 1]);
        }

        this.elements = tableRanges
            .map(([first, last]) =>
                this._parseTable(lines, first, last)
            )
            .filter(Boolean);

        this.elements.forEach((table, index) => {
            table.index = index;

            if (this.options.highlightTables) {
                this._createHighlight(table);
            }
        });

        // Restore the active item if it still exists.
        if (this.activeElement) {
            const activeIndex = Math.min(
                oldActiveIndex,
                this.elements.length - 1
            );

            if (activeIndex >= 0) {
                this.activeElement = this.elements[activeIndex];
            } else {
                this.closeEditor();
            }
        }

        this._positionHighlights();

        /*
         * refresh() is a render/parse operation only.
         * It must not dispatch input events itself.
         */
        this.innerSave = this.textarea.innerHTML;

        return this.elements;
    }

    getElements() {
        return this.elements.map(element => ({
            type: element.type,
            startLine: element.startLine,
            endLine: element.endLine,
            ...(element.type === "table" ? {
                headers: [...element.headers],
                data: element.data.map(row => [...row])
            } : {
                url: element.url,
                sourceUrl: element.sourceUrl
            })
        }));
    }

    // Backward-compatible API for existing integrations.
    getTables() {
        return this.elements
            .filter(element => element.type === "table")
            .map(table => ({
                startLine: table.startLine,
                endLine: table.endLine,
                headers: [...table.headers],
                data: table.data.map(row => [...row])
            }));
    }

    /* --------------------------------------------------
       Highlight creation and positioning
    -------------------------------------------------- */

    _createHighlight(table) {
        const doc = this.textarea.ownerDocument;
        const highlight = doc.createElement("div");

        highlight.className = "rst-table-highlight";

        Object.assign(highlight.style, {
            position: "absolute",
            boxSizing: "border-box",
            pointerEvents: "auto"
        });

        if (table.type === "table") {
            highlight.title = "Click to edit this table";

            highlight.addEventListener("click", event => {
                event.preventDefault();
                this.openEditor(table.index);
            });
        }

        highlight.dataset.tableIndex = String(table.index);

        this.overlay.appendChild(highlight);
        table.highlight = highlight;
    }

    _removeHighlights() {
        this.overlay?.replaceChildren();
    }

    _positionHighlights() {
        if (this.destroyed || !this.textarea.isConnected) return;

        const doc = this.textarea.ownerDocument;
        const win = doc.defaultView;

        if (!win) return;

        const walkerFilter = win.NodeFilter.SHOW_TEXT;

        this.elements.forEach(table => {
            const highlight = table.highlight;
            if (!highlight) return;

            const lineRects = [];
            const walker = doc.createTreeWalker(
                this.textarea,
                walkerFilter
            );

            let node;
            let logicalLine = 0;

            while ((node = walker.nextNode())) {
                const text = node.textContent;

                for (let i = 0; i < text.length; i++) {
                    if (
                        logicalLine >= table.startLine &&
                        logicalLine <= table.endLine &&
                        text[i] !== "\n"
                    ) {
                        const range = doc.createRange();

                        range.setStart(node, i);
                        range.setEnd(node, i + 1);

                        const rect = range.getBoundingClientRect();

                        if (rect.width || rect.height) {
                            lineRects.push(rect);
                        }
                    }

                    if (text[i] === "\n") {
                        logicalLine++;
                    }
                }
            }

            if (!lineRects.length) {
                highlight.style.display = "none";
                return;
            }

            const top = Math.min(
                ...lineRects.map(rect => rect.top)
            );

            const bottom = Math.max(
                ...lineRects.map(rect => rect.bottom)
            );

            const left = Math.min(
                ...lineRects.map(rect => rect.left)
            );

            const right = Math.max(
                ...lineRects.map(rect => rect.right)
            );

            /*
             * The wrapper is position:fixed at viewport origin.
             * Range rectangles are also viewport-relative.
             */
            Object.assign(highlight.style, {
                display: "",
                top: `${top}px`,
                left: `${left}px`,
                height: `${Math.max(2, bottom - top)}px`,
                width: `${Math.max(2, right - left)}px`
            });

            highlight.classList.toggle(
                "active",
                this.activeElement?.index === table.index
            );
        });
    }

    /* --------------------------------------------------
       RST serialization and source synchronization
    -------------------------------------------------- */

    _serializeTable(table) {
        const headers = table.headers;
        const data = table.data;

        const widths = headers.map((header, column) =>
            Math.max(
                String(header ?? "").length,
                ...data.map(row =>
                    String(row[column] ?? "").length
                )
            )
        );

        const border = character =>
            "+" +
            widths.map(width => character.repeat(width + 2)).join("+") +
            "+";

        const renderRow = row =>
            "|" +
            row.map((cell, column) =>
                ` ${String(cell ?? "").padEnd(widths[column])} `
            ).join("|") +
            "|";

        const output = [
            border("-"),
            renderRow(headers),
            border("=")
        ];

        data.forEach((row, index) => {
            output.push(renderRow(row));

            if (index < data.length - 1) {
                output.push(border("-"));
            }
        });

        output.push(border("-"));

        return output.join("\n");
    }

    _syncSource(table) {
        if (!table) return;

        const lines = this._getSourceLines();
        const serialized = this._serializeTable(table).split("\n");

        const previousStart = table.startLine;
        const previousEnd = table.endLine;

        const updatedLines = [
            ...lines.slice(0, previousStart),
            ...serialized,
            ...lines.slice(previousEnd + 1)
        ];

        this._replaceSource(updatedLines.join("\n"));

        // Rebind to the newly parsed table.
        const updatedTable = this.elements[table.index];

        if (updatedTable) {
            this.activeElement = updatedTable;
        }
    }


    /* --------------------------------------------------
       Floating table editor
    -------------------------------------------------- */

    openEditor(index) {
        if (!this.options.editable) return;

        const table = this.elements[index];

        if (!table || table.type !== "table") return;

        this.closeEditor();
        this.activeElement = table;

        const doc = this.textarea.ownerDocument;

        const win = doc.createElement("div");
        win.className = "rst-editor-window";

        const header = doc.createElement("div");
        header.className = "rst-editor-header";

        const title = doc.createElement("span");
        title.textContent = `Table Editor ${index + 1}`;

        const closeButton = doc.createElement("button");
        closeButton.type = "button";
        closeButton.textContent = "Close";

        closeButton.addEventListener("click", () => {
            this.closeEditor();
        });

        header.append(title, closeButton);

        const content = doc.createElement("div");
        content.className = "rst-editor-content";

        win.append(header, content);
        doc.body.appendChild(win);

        this.editorWindow = win;

        this._renderEditorTable(content, table);
        this._makeDraggable(win, header);

        Object.assign(win.style, {
            position: "fixed",
            left: "25%",
            top: "25%",
            width: "50%",
            height: "50%"
        });

        table.highlight?.classList.add("active");
    }

    _renderEditorTable(container, table) {
        container.replaceChildren();

        const doc = container.ownerDocument;

        const htmlTable = doc.createElement("table");
        htmlTable.className = "rst-editor-table";

        const thead = doc.createElement("thead");
        const headerRow = doc.createElement("tr");

        table.headers.forEach((value, column) => {
            const th = doc.createElement("th");

            th.appendChild(
                this._makeCellInput(value, true, 0, column)
            );

            headerRow.appendChild(th);
        });

        thead.appendChild(headerRow);
        htmlTable.appendChild(thead);

        const tbody = doc.createElement("tbody");

        table.data.forEach((row, rowIndex) => {
            const tr = doc.createElement("tr");

            row.forEach((value, column) => {
                const td = doc.createElement("td");

                td.appendChild(
                    this._makeCellInput(
                        value,
                        false,
                        rowIndex,
                        column
                    )
                );

                tr.appendChild(td);
            });

            tbody.appendChild(tr);
        });

        htmlTable.appendChild(tbody);

        htmlTable.addEventListener("contextmenu", event => {
            const cell = event.target.closest("th, td");

            if (!cell) return;

            event.preventDefault();

            const input = cell.querySelector("input");

            if (!input) return;

            this._showContextMenu(
                event.clientX,
                event.clientY,
                {
                    isHeader: input.dataset.header === "true",
                    row: Number(input.dataset.row),
                    column: Number(input.dataset.column)
                }
            );
        });

        container.appendChild(htmlTable);
    }

    _makeCellInput(value, isHeader, row, column) {
        const input = this.textarea.ownerDocument.createElement("input");

        input.type = "text";
        input.value = value;

        input.dataset.header = String(isHeader);
        input.dataset.row = String(row);
        input.dataset.column = String(column);

        input.setAttribute(
            "aria-label",
            `${isHeader ? "Header" : `Row ${row + 1}`}, column ${column + 1}`
        );

        input.addEventListener("input", () => {
            const table = this.activeElement;

            if (!table) return;

            const currentColumn = Number(input.dataset.column);
            const currentRow = Number(input.dataset.row);

            if (input.dataset.header === "true") {
                table.headers[currentColumn] = input.value;
            } else if (table.data[currentRow]) {
                table.data[currentRow][currentColumn] = input.value;
            }

            this._syncSource(table);
        });

        return input;
    }

    closeEditor() {
        this.editorWindow?.remove();
        this.editorWindow = null;

        this._hideContextMenu();

        this.elements.forEach(table => {
            table.highlight?.classList.remove("active");
        });

        this.activeElement = null;
    }

    /* --------------------------------------------------
       Context menu and structural editing
    -------------------------------------------------- */

    _showContextMenu(x, y, target) {
        this._hideContextMenu();

        const doc = this.textarea.ownerDocument;
        const win = doc.defaultView;

        const menu = doc.createElement("div");
        menu.className = "rst-context-menu";

        const actions = [
            ["Add Row Before", () => this._changeRow(target, -1)],
            ["Add Row After", () => this._changeRow(target, 1)],
            ["Delete Row", () => this._deleteRow(target)],
            ["divider", null],
            ["Add Column Before", () => this._changeColumn(target, -1)],
            ["Add Column After", () => this._changeColumn(target, 1)],
            ["Delete Column", () => this._deleteColumn(target)]
        ];

        actions.forEach(([label, action]) => {
            if (label === "divider") {
                const divider = doc.createElement("div");
                divider.className = "divider";
                menu.appendChild(divider);
                return;
            }

            const button = doc.createElement("button");
            button.type = "button";
            button.textContent = label;

            button.addEventListener("click", () => {
                action();
                this._hideContextMenu();
            });

            menu.appendChild(button);
        });

        doc.body.appendChild(menu);
        this.contextMenu = menu;

        menu.style.left = `${Math.max(
            4,
            Math.min(x, win.innerWidth - menu.offsetWidth - 4)
        )}px`;

        menu.style.top = `${Math.max(
            4,
            Math.min(y, win.innerHeight - menu.offsetHeight - 4)
        )}px`;
    }

    _hideContextMenu() {
        this.contextMenu?.remove();
        this.contextMenu = null;
    }

    _changeRow(target, direction) {
        const table = this.activeElement;

        if (!table) return;

        const index = target.isHeader
            ? (direction < 0 ? 0 : table.data.length)
            : target.row + (direction > 0 ? 1 : 0);

        const newRow = Array(table.headers.length).fill("");

        table.data.splice(index, 0, newRow);

        this._afterStructureChange(table);
    }

    _deleteRow(target) {
        const table = this.activeElement;

        if (!table || table.data.length <= 1) return;

        const index = target.isHeader ? 0 : target.row;

        if (index < 0 || index >= table.data.length) return;

        table.data.splice(index, 1);

        this._afterStructureChange(table);
    }

    _changeColumn(target, direction) {
        const table = this.activeElement;

        if (!table) return;

        const index = target.column + (direction > 0 ? 1 : 0);

        table.headers.splice(index, 0, "");

        table.data.forEach(row => {
            row.splice(index, 0, "");
        });

        this._afterStructureChange(table);
    }

    _deleteColumn(target) {
        const table = this.activeElement;

        if (!table || table.headers.length <= 1) return;

        table.headers.splice(target.column, 1);

        table.data.forEach(row => {
            row.splice(target.column, 1);
        });

        this._afterStructureChange(table);
    }

    _afterStructureChange(table) {
        this._syncSource(table);

        if (!this.activeElement || !this.editorWindow) return;

        const content = this.editorWindow.querySelector(
            ".rst-editor-content"
        );

        if (content) {
            this._renderEditorTable(content, this.activeElement);
        }
    }

    /* --------------------------------------------------
       Draggable editor window
    -------------------------------------------------- */

    _makeDraggable(element, handle) {
        const doc = element.ownerDocument;
        const win = doc.defaultView;

        const onMouseDown = event => {
            if (event.target.closest("button")) return;

            event.preventDefault();

            const startX = event.clientX;
            const startY = event.clientY;

            const rect = element.getBoundingClientRect();
            const startLeft = rect.left;
            const startTop = rect.top;

            const onMove = moveEvent => {
                const left = Math.max(
                    0,
                    Math.min(
                        startLeft + moveEvent.clientX - startX,
                        win.innerWidth - element.offsetWidth
                    )
                );

                const top = Math.max(
                    0,
                    Math.min(
                        startTop + moveEvent.clientY - startY,
                        win.innerHeight - element.offsetHeight
                    )
                );

                element.style.left = `${left}px`;
                element.style.top = `${top}px`;
            };

            const onUp = () => {
                doc.removeEventListener("mousemove", onMove);
                doc.removeEventListener("mouseup", onUp);
                this._dragCleanup = null;
            };

            this._dragCleanup?.();

            this._dragCleanup = onUp;

            doc.addEventListener("mousemove", onMove);
            doc.addEventListener("mouseup", onUp);
        };

        handle.addEventListener("mousedown", onMouseDown);
    }

    /* --------------------------------------------------
       Cleanup
    -------------------------------------------------- */

    destroy() {
        if (this.destroyed) return;

        this.closeEditor();

        const doc = this.textarea.ownerDocument;
        const win = doc.defaultView;

        this.textarea.removeEventListener("input", this._onInput);
        this.textarea.removeEventListener("scroll", this._onScroll);
        this.textarea.removeEventListener("keydown", this._onKeyDown);

        win?.removeEventListener("resize", this._onWindowResize);
        win?.removeEventListener("scroll", this._onWindowScroll, true);

        doc.removeEventListener("click", this._onDocumentClick);

        this._resizeObserver?.disconnect();
        this._resizeObserver = null;

        this._dragCleanup?.();
        this._dragCleanup = null;

        /*
         * Critical: do not move the StrictDoc editable element,
         * restore its position, or overwrite its inline styles.
         */
        this.wrapper?.remove();

        this.elements = [];
        this.activeElement = null;

        this.destroyed = true;
    }
}

/* ==================================================
Statement toolbar
================================================== */

function addStatementIcons() {
    const target = document.querySelector(
        'sdoc-contenteditable[data-field-label="STATEMENT"]'
    );

    if (!target) {
        console.warn("STATEMENT field not found.");
        return null;
    }

    const existing = document.querySelector(
        ".statement-icon-toolbar"
    );

    if (existing) {
        return () => existing.remove();
    }

    const toolbar = document.createElement("div");
    toolbar.className = "statement-icon-toolbar";

    Object.assign(toolbar.style, {
        position: "fixed",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: "6px",
        zIndex: "512"
    });

    let savedRange = null;

    function saveCursor() {
        const selection = window.getSelection();

        if (!selection || !selection.rangeCount) return;

        const range = selection.getRangeAt(0);

        if (target.contains(range.startContainer)) {
            savedRange = range.cloneRange();
        }
    }

    target.addEventListener("mouseup", saveCursor);
    target.addEventListener("keyup", saveCursor);

    function insertAtSavedCursor(text) {
        target.focus();

        const selection = window.getSelection();

        if (
            !savedRange ||
            !target.contains(savedRange.startContainer)
        ) {
            console.warn(
                "No saved cursor position. Place the cursor in the statement first."
            );
            return;
        }

        selection.removeAllRanges();
        selection.addRange(savedRange);

        const range = selection.getRangeAt(0);
        range.deleteContents();

        const textNode = document.createTextNode(text);

        range.insertNode(textNode);
        range.setStartAfter(textNode);
        range.collapse(true);

        selection.removeAllRanges();
        selection.addRange(range);

        savedRange = range.cloneRange();

        target.dispatchEvent(
            new InputEvent("input", {
                bubbles: true,
                inputType: "insertText",
                data: text
            })
        );
    }

    let savedButtonRect = null;

    function showTablePicker(buttonElement) {
        document.querySelector("#table-picker")?.remove();

        const maxCols = 10;
        const maxRows = 8;
        let selectedCols = 1;
        let selectedRows = 1;

        const picker = document.createElement("div");
        picker.id = "table-picker";

        Object.assign(picker.style, {
            position: "fixed",
            zIndex: "2147483647",
            padding: "12px",
            background: "#ffffff",
            color: "#222222",
            border: "1px solid #cccccc",
            borderRadius: "8px",
            boxShadow: "0 4px 20px rgba(0,0,0,.25)",
            display: "block",
            visibility: "visible",
            opacity: "1",
            width: "max-content",
            fontFamily: "Arial, sans-serif"
        });

        const title = document.createElement("div");
        title.textContent = "Insert table";
        Object.assign(title.style, {
            fontSize: "13px",
            fontWeight: "600",
            marginBottom: "6px"
        });

        const label = document.createElement("div");
        label.textContent = "1 column × 1 row";
        Object.assign(label.style, {
            fontSize: "12px",
            marginBottom: "10px",
            color: "#555555"
        });

        const grid = document.createElement("div");
        Object.assign(grid.style, {
            display: "grid",
            gridTemplateColumns: `repeat(${maxCols}, 22px)`,
            gap: "3px"
        });

        function updateGrid(cols, rows) {
            selectedCols = cols;
            selectedRows = rows;

            label.textContent =
                `${cols} column${cols === 1 ? "" : "s"} × ` +
                `${rows} row${rows === 1 ? "" : "s"}`;

            Array.from(grid.children).forEach((cell, index) => {
                const col = (index % maxCols) + 1;
                const row = Math.floor(index / maxCols) + 1;
                const selected = col <= cols && row <= rows;

                cell.style.backgroundColor =
                    selected ? "#b8d7ff" : "#ffffff";

                cell.style.borderColor =
                    selected ? "#2675d8" : "#aaaaaa";
            });
        }

        for (let row = 1; row <= maxRows; row++) {
            for (let col = 1; col <= maxCols; col++) {
                const cell = document.createElement("button");

                cell.type = "button";
                cell.title = `${col} columns × ${row} rows`;
                cell.setAttribute("aria-label", cell.title);

                Object.assign(cell.style, {
                    width: "22px",
                    height: "22px",
                    padding: "0",
                    border: "1px solid #aaaaaa",
                    borderRadius: "2px",
                    cursor: "pointer",
                    backgroundColor: "#ffffff"
                });

                cell.addEventListener("mouseenter", () => {
                    updateGrid(col, row);
                });

                cell.addEventListener("focus", () => {
                    updateGrid(col, row);
                });

                cell.addEventListener("click", (event) => {
                    event.preventDefault();
                    event.stopPropagation();

                    const cols = selectedCols;
                    const rows = selectedRows;

                    picker.remove();

                    const text = createAsciiTable(cols, rows);
                    insertAtSavedCursor(text);
                });

                grid.appendChild(cell);
            }
        }

        picker.append(title, label, grid);
        document.body.appendChild(picker);


        // Close when clicking anywhere outside the picker.
        function handleOutsideClick(event) {
            if (!picker.contains(event.target)) {
                picker.remove();
                cleanup();
            }
        }

        // Close when the mouse leaves the picker.
        function handleMouseLeave() {
            picker.remove();
            cleanup();
        }

        function cleanup() {
            document.removeEventListener(
                "mousedown",
                handleOutsideClick,
                true
            );

            picker.removeEventListener(
                "mouseleave",
                handleMouseLeave
            );
        }

        // Delay registration so the opening click doesn't close it.
        setTimeout(() => {
            if (!picker.isConnected) return;

            document.addEventListener(
                "mousedown",
                handleOutsideClick,
                true
            );

            picker.addEventListener(
                "mouseleave",
                handleMouseLeave
            );
        }, 0);





        // Position relative to the toolbar button.
        const rect = buttonElement?.getBoundingClientRect();

        let x = rect ? rect.left : 20;
        let y = rect ? rect.bottom + 4 : 20;

        // Measure after attaching the picker to the document.
        const pickerWidth = picker.offsetWidth;
        const pickerHeight = picker.offsetHeight;

        x = Math.max(
            8,
            Math.min(x, window.innerWidth - pickerWidth - 8)
        );

        // If there isn't enough room below the button, show it above.
        if (y + pickerHeight > window.innerHeight - 8 && rect) {
            y = rect.top - pickerHeight - 4;
        }

        y = Math.max(
            8,
            Math.min(y, window.innerHeight - pickerHeight - 8)
        );

        picker.style.left = `${savedButtonRect.left}px`;
        picker.style.top = `${savedButtonRect.bottom}px`;

        updateGrid(1, 1);

        // Close on Escape.
        picker.tabIndex = -1;

        picker.addEventListener("keydown", (event) => {
            if (event.key === "Escape") {
                picker.remove();
            }
        });

        return picker;
    }

    function createAsciiTable(cols, rows) {
        const cellWidth = 12;
        const border = "+" +
            Array(cols).fill("-".repeat(cellWidth + 2)).join("+") +
            "+";

        const separator = "+" +
            Array(cols).fill("=".repeat(cellWidth + 2)).join("+") +
            "+";

        const makeRow = (values = []) =>
            "|" +
            Array.from({ length: cols }, (_, i) => {
                const value = values[i] ?? "";
                return " " + String(value).padEnd(cellWidth).slice(0, cellWidth) + " ";
            }).join("|") +
            "|";

        const lines = [border, makeRow(), separator];

        for (let row = 0; row < rows; row++) {
            lines.push(makeRow());
            lines.push(border);
        }

        return "\n\n" + lines.join("\n") + "\n\n";
    }

    const actions = [
        {
            icon: "▦",
            title: "Insert a table",
            run: () => {
                showTablePicker();
            }
        }
    ];

    actions.forEach(({ icon, title, run }) => {
        const button = document.createElement("button");



    button.addEventListener("mousedown", (event) => {
        const rect = event.currentTarget.getBoundingClientRect();
        savedButtonRect = {
            left: rect.left,
            bottom: rect.bottom
        };
            console.log(savedButtonRect);
    });

        button.type = "button";
        button.textContent = icon;
        button.title = title;
        button.setAttribute("aria-label", title);

        Object.assign(button.style, {
            width: "28px",
            height: "28px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: "0",
            border: "1px solid #d0d0d0",
            borderRadius: "6px",
            background: "#fff",
            color: "#333",
            fontSize: "15px",
            cursor: "pointer",
            boxShadow: "0 1px 3px rgba(0,0,0,0.12)"
        });

        button.addEventListener("mouseenter", () => {
            button.style.background = "#f0f0f0";
        });

        button.addEventListener("mouseleave", () => {
            button.style.background = "#fff";
        });

        button.addEventListener("click", event => {
            event.preventDefault();
            event.stopPropagation();
            run();
        });

        toolbar.appendChild(button);
    });

    document.body.appendChild(toolbar);

    function updatePosition() {
        if (!target.isConnected) {
            toolbar.remove();
            return;
        }

        const rect = target.getBoundingClientRect();

        Object.assign(toolbar.style, {
            left: `${Math.max(
                8,
                rect.left - toolbar.offsetWidth - 8
            )}px`,
            top: "50%",
            transform: "translateY(-50%)"
        });
    }

    updatePosition();

    window.addEventListener("scroll", updatePosition, true);
    window.addEventListener("resize", updatePosition);

    const resizeObserver = new ResizeObserver(updatePosition);
    resizeObserver.observe(target);

    return function removeStatementIcons() {
        window.removeEventListener("scroll", updatePosition, true);
        window.removeEventListener("resize", updatePosition);

        resizeObserver.disconnect();

        target.removeEventListener("mouseup", saveCursor);
        target.removeEventListener("keyup", saveCursor);

        toolbar.remove();
    };
}

/* ==================================================
   StrictDoc editor initialization
================================================== */

function installRSTEditor() {
    const SEL_RST_EDITABLE =
        'sdoc-contenteditable[data-js-editable-field]' +
        '[data-field-type="multiline"][contenteditable="true"]';

    const instances = new WeakMap();

    function initializeRSTEditor(editable) {
        if (
            editable.dataset.rstEditorInitialized === "true"
        ) {
            return;
        }

        try {
            const instance = new RSTEditor(editable);

            instances.set(editable, instance);
            editable.dataset.rstEditorInitialized = "true";
        } catch (error) {
            console.error(
                "Failed to initialize RSTEditor:",
                error
            );
        }
    }

    function scanForEditableFields(root = document) {
        if (
            root instanceof Element &&
            root.matches(SEL_RST_EDITABLE)
        ) {
            initializeRSTEditor(root);
        }

        root.querySelectorAll?.(SEL_RST_EDITABLE)
            .forEach(initializeRSTEditor);
    }

    function maybeInstallToolbar() {
        const input = document.getElementById("document_markup");

        if (
            input?.value === "RST" &&
            !document.querySelector(".statement-icon-toolbar")
        ) {
            addStatementIcons();
        }
    }

    const observer = new MutationObserver(mutations => {
        for (const mutation of mutations) {
            for (const node of mutation.addedNodes) {
                if (!(node instanceof Element)) continue;

                if (
                    node.matches(SEL_RST_EDITABLE) ||
                    node.querySelector(SEL_RST_EDITABLE)
                ) {
                    scanForEditableFields(node);
                    maybeInstallToolbar();
                }
            }
        }
    });

    observer.observe(document.documentElement, {
        childList: true,
        subtree: true
    });

    document.addEventListener("turbo:load", () => {
        scanForEditableFields();
        maybeInstallToolbar();
    });

    document.addEventListener("turbo:frame-load", () => {
        scanForEditableFields();
        maybeInstallToolbar();
    });

    scanForEditableFields();
    maybeInstallToolbar();

    return function uninstallTableEditor() {
        observer.disconnect();

        document.querySelectorAll(SEL_RST_EDITABLE)
            .forEach(editable => {
                instances.get(editable)?.destroy();
                delete editable.dataset.rstEditorInitialized;
            });

        document.querySelector(".statement-icon-toolbar")?.remove();
    };
}

/* Start the integration. */
installRSTEditor();
