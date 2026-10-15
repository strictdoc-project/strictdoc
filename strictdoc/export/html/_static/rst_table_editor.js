class RSTTableEditor {
    constructor(textarea, options = {}) {
        // Accept either a DOM element or a CSS selector.
        if (typeof textarea === "string") {
            textarea = document.querySelector(textarea);
        }

        /*
         * Keep the existing element handling unchanged.
         * The editor is designed to work with the editable field
         * supplied by the caller.
         */

        this.textarea = textarea;

        // Default configuration can be overridden by the caller.
        this.options = {
            highlightTables: true,
            editable: true,
            ...options
        };

        // Table state and references to dynamically created elements.
        this.tables = [];
        this.activeTable = null;
        this.editorWindow = null;
        this.contextMenu = null;
        this.destroyed = false;

        // References used to clean up observers and drag handlers.
        this._resizeObserver = null;
        this._dragCleanup = null;

        // Preserve the original DOM position and inline styles for cleanup.
        this._originalParent = textarea.parentNode;
        this._originalNextSibling = textarea.nextSibling;
        this._originalStyle = textarea.getAttribute("style");

        this._buildDOM();
        this._bindEvents();
        this.refresh();
    }

    /* --------------------------------------------------
       DOM initialization and event management
    -------------------------------------------------- */

    _buildDOM() {
        const doc = this.textarea.ownerDocument;

        // Create a wrapper around the editable field.
        this.wrapper = doc.createElement("div");
        this.wrapper.className = "rst-table-wrapper";

        this.textarea.parentNode.insertBefore(
            this.wrapper,
            this.textarea
        );

        /*
         * The wrapper is currently inserted before the editable field,
         * but the field itself is not moved into it.
         */

        // The overlay contains the clickable highlights for detected tables.
        this.overlay = doc.createElement("div");
        this.overlay.className = "rst-table-overlay";
        this.textarea.appendChild(this.overlay);

        // Keep the overlay from intercepting normal text input.
        this.overlay.style.pointerEvents = "none";

        // Reposition highlights when the editable field changes size.
        this._resizeObserver =
            typeof ResizeObserver !== "undefined"
                ? new ResizeObserver(() => this._positionHighlights())
                : null;

        this._resizeObserver?.observe(this.textarea);
    }

    _bindEvents() {
        // Refresh table detection whenever the source content changes.
        this._onInput = () => this.refresh();

        // Recalculate highlight positions when the content scrolls.
        this._onScroll = () => this._positionHighlights();

        // Recalculate highlight positions when the viewport changes size.
        this._onWindowResize = () => this._positionHighlights();

        // Close the context menu when the user clicks outside it.
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

        // Escape closes the floating table editor.
        this.textarea.addEventListener("keydown", event => {
            if (event.key === "Escape") {
                this.closeEditor();
            }
        });

        window.addEventListener("resize", this._onWindowResize);
        document.addEventListener("click", this._onDocumentClick);
    }

    /* --------------------------------------------------
       Table detection and parsing
    -------------------------------------------------- */

    // Match a grid-table border made of +, - and = characters.
    _isBorder(line) {
        return /^\s*\+[-=+]+\+\s*$/.test(line);
    }

    // Match a grid-table row enclosed by vertical bars.
    _isRow(line) {
        return /^\s*\|.*\|\s*$/.test(line);
    }

    // A table can contain either border lines or row lines.
    _isTableLine(line) {
        return this._isBorder(line) || this._isRow(line);
    }

    // In an RST grid table, the header separator contains = characters.
    _isHeaderBorder(line) {
        return line.includes("=") && this._isBorder(line);
    }

    /**
     * Parse a candidate table range into its headers and data rows.
     * Return null when the range does not match the expected structure.
     */
    _parseTable(lines, startLine, endLine) {
        const tableLines = lines.slice(startLine, endLine + 1);

        // A valid table requires enough lines for borders and content.
        if (tableLines.length < 4) return null;

        // Find the separator between the header and the data rows.
        const headerSeparatorIndex = tableLines.findIndex(
            (line, index) =>
                index > 0 && this._isHeaderBorder(line)
        );

        if (headerSeparatorIndex < 0) return null;

        // Locate the last row before the header separator.
        const headerLineIndex = tableLines
            .slice(0, headerSeparatorIndex)
            .findLastIndex(line => this._isRow(line));

        if (headerLineIndex < 0) return null;

        // Remove the outer bars and trim whitespace from each cell.
        const splitRow = line =>
            line.trim()
                .slice(1, -1)
                .split("|")
                .map(cell => cell.trim());

        const headers = splitRow(tableLines[headerLineIndex]);
        const data = [];

        // Collect the data rows that follow the header separator.
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

        // Reject malformed tables whose rows have different column counts.
        if (data.some(row => row.length !== headers.length)) {
            return null;
        }

        return {
            startLine,
            endLine,
            headers,
            data,
            highlight: null
        };
    }

    /**
     * Re-detect tables in the current source and update their highlights.
     * The active table is restored by its previous index when possible.
     */
    refresh() {
        if (this.destroyed) return;

        const oldActiveIndex = this.activeTable
            ? this.activeTable.index
            : -1;

        // Remove stale highlights before rebuilding the table list.
        this._removeHighlights();

        const lines = this.textarea.innerHTML.split(/\r?\n/);
        const ranges = [];

        let start = -1;

        // Identify contiguous ranges of potential table lines.
        for (let i = 0; i < lines.length; i++) {
            if (this._isTableLine(lines[i])) {
                if (start === -1) start = i;
            } else if (start !== -1) {
                ranges.push([start, i - 1]);
                start = -1;
            }
        }

        // Include a table range that reaches the end of the content.
        if (start !== -1) {
            ranges.push([start, lines.length - 1]);
        }

        // Parse the candidate ranges and discard invalid tables.
        this.tables = ranges
            .map(([first, last]) =>
                this._parseTable(lines, first, last)
            )
            .filter(Boolean);

        // Assign stable-in-this-refresh indexes and create highlights.
        this.tables.forEach((table, index) => {
            table.index = index;

            if (this.options.highlightTables) {
                this._createHighlight(table);
            }
        });

        // Restore the active table by its previous ordinal position.
        if (this.activeTable) {
            const activeIndex = Math.min(
                oldActiveIndex,
                this.tables.length - 1
            );

            if (activeIndex >= 0) {
                this.activeTable = this.tables[activeIndex];
            } else {
                // The active table no longer exists.
                this.closeEditor();
            }
        }

        this._positionHighlights();

        /*
         * Keep the existing source-change notification behavior.
         * innerSave prevents this check from dispatching input repeatedly
         * when the source content has not changed.
         */
        if (this.textarea.innerHTML != this.innerSave) {
            this.innerSave = this.textarea.innerHTML;

            this.textarea.dispatchEvent(
                new Event("input", { bubbles: true })
            );
        }

        return this.tables;
    }

    /**
     * Return a copy of the parsed table data without DOM references.
     */
    getTables() {
        return this.tables.map(table => ({
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
        const highlight = document.createElement("div");

        highlight.className = "rst-table-highlight";
        highlight.style.pointerEvents = "auto";
        highlight.title = "Click to edit this table";
        highlight.dataset.tableIndex = table.index;

        // Open the editor for the selected table when its highlight is clicked.
        highlight.addEventListener("click", event => {
            event.preventDefault();
            this.openEditor(table.index);
        });

        this.overlay.appendChild(highlight);
        table.highlight = highlight;
    }

    // Remove all existing highlight elements from the overlay.
    _removeHighlights() {
        this.overlay.replaceChildren();
    }

    /**
     * Find the viewport Y-coordinate of a logical line by walking
     * through the text nodes and counting newline characters.
     */
    coords(contenteditable, line) {
        const walker = document.createTreeWalker(
            contenteditable,
            NodeFilter.SHOW_TEXT
        );

        let currentLine = 0;
        let node;

        while ((node = walker.nextNode())) {
            const text = node.textContent;

            for (let i = 0; i < text.length; i++) {
                if (currentLine === line) {
                    const range = document.createRange();

                    range.setStart(node, i);
                    range.setEnd(node, i + 1);

                    const rect = range.getBoundingClientRect();

                    if (rect.height > 0) {
                        return rect.top;
                    }
                }

                if (text[i] === "\n") {
                    currentLine++;
                }
            }
        }

        return null;
    }

    /**
     * Position each highlight using the rendered character rectangles.
     *
     * This implementation measures actual text-node geometry rather
     * than estimating positions from font size or character width.
     */
    _positionHighlights() {
        if (this.destroyed) return;

        const editorRect = this.textarea.getBoundingClientRect();

        this.tables.forEach(table => {
            const highlight = table.highlight;
            if (!highlight) return;

            // Verify that both ends of the table can be located.
            const startY = this.coords(this.textarea, table.startLine);
            const endY = this.coords(this.textarea, table.endLine);

            if (startY === null || endY === null) {
                highlight.style.display = "none";
                return;
            }

            const lineRects = [];

            // Walk text nodes and collect rendered rectangles for
            // characters belonging to the table's logical line range.
            const walker = document.createTreeWalker(
                this.textarea,
                NodeFilter.SHOW_TEXT
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
                        const range = document.createRange();

                        range.setStart(node, i);
                        range.setEnd(node, i + 1);

                        const rect = range.getBoundingClientRect();

                        // Ignore characters that have no rendered area.
                        if (rect.width || rect.height) {
                            lineRects.push(rect);
                        }
                    }

                    if (text[i] === "\n") {
                        logicalLine++;
                    }
                }
            }

            // Hide the highlight if no rendered characters were found.
            if (!lineRects.length) {
                highlight.style.display = "none";
                return;
            }

            // Calculate the bounding rectangle around all collected text.
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

            highlight.style.display = "";
            highlight.style.position = "absolute";

            // Convert viewport coordinates to overlay-relative coordinates.
            highlight.style.top =
                `${top - editorRect.top + this.textarea.scrollTop}px`;

            highlight.style.left =
                `${left - editorRect.left + this.textarea.scrollLeft}px`;

            highlight.style.height = `${bottom - top}px`;
            highlight.style.width = `${right - left}px`;

            // Keep the active table visually distinguished.
            highlight.classList.toggle(
                "active",
                this.activeTable?.index === table.index
            );
        });
    }

    /* --------------------------------------------------
       RST serialization and source synchronization
    -------------------------------------------------- */

    /**
     * Serialize a parsed table back into reStructuredText grid-table syntax.
     *
     * Column widths are calculated from the longest cell in each column.
     * The first border separates the table from preceding content,
     * and the equals-sign border separates the header from the data rows.
     */
    _serializeTable(table) {
        const headers = table.headers;
        const data = table.data;

        // Determine the minimum width needed for each column.
        const widths = headers.map((header, column) => {
            return Math.max(
                header.length,
                ...data.map(row => (row[column] ?? "").length)
            );
        });

        // Build a horizontal border using the supplied character.
        const border = character =>
            "+" + widths
                .map(width => character.repeat(width))
                .join("+") + "+";

        // Render a row with cells padded to their column widths.
        const renderRow = row =>
            "|" + row.map((cell, column) =>
                String(cell ?? "").padEnd(widths[column])
            ).join("|") + "|";

        const output = [
            border("-"),
            renderRow(headers),
            border("=")
        ];

        // Add data rows and separators between consecutive rows.
        data.forEach((row, index) => {
            output.push(renderRow(row));

            if (index < data.length - 1) {
                output.push(border("-"));
            }
        });

        // Close the table with a final border.
        output.push(border("-"));

        return output.join("\n");
    }

    /**
     * Replace the original table's source lines with the serialized version.
     * Then refresh table detection and notify application code of the change.
     */
    _syncSource(table) {
        if (!table) return;

        const lines = this.textarea.innerHTML.split(/\r?\n/);
        const serialized = this._serializeTable(table).split("\n");

        const previousStart = table.startLine;
        const previousEnd = table.endLine;

        // Preserve content before and after the table being edited.
        const updatedLines = [
            ...lines.slice(0, previousStart),
            ...serialized,
            ...lines.slice(previousEnd + 1)
        ];

        this.textarea.innerHTML = updatedLines.join("\n");

        // Update the table's line boundaries before refreshing detection.
        table.endLine = previousStart + serialized.length - 1;

        const cursor = this.textarea.selectionStart;

        // Reparse the source and recreate the table highlights.
        this.refresh();

        // Rebind the active table to the newly parsed table at the same index.
        const updatedTable = this.tables[table.index];

        if (updatedTable) {
            this.activeTable = updatedTable;
        }

        // Notify listeners that the source has changed.
        this.textarea.dispatchEvent(
            new Event("change", { bubbles: true })
        );
    }

    /* --------------------------------------------------
       Floating table editor
    -------------------------------------------------- */

    /**
     * Open the floating editor for the table at the specified index.
     */
    openEditor(index) {
        if (!this.options.editable) return;

        const table = this.tables[index];
        if (!table) return;

        // Close any existing editor before opening another.
        this.closeEditor();

        this.activeTable = table;

        const win = document.createElement("div");
        win.className = "rst-editor-window";

        const header = document.createElement("div");
        header.className = "rst-editor-header";

        const title = document.createElement("span");
        title.textContent = `Table Editor ${index + 1}`;

        // The close button removes the floating editor.
        const closeButton = document.createElement("button");
        closeButton.type = "button";
        closeButton.textContent = "Close";

        closeButton.addEventListener("click", () => {
            this.closeEditor();
        });

        header.append(title, closeButton);

        const content = document.createElement("div");
        content.className = "rst-editor-content";

        win.append(header, content);
        document.body.appendChild(win);

        this.editorWindow = win;

        // Populate the editor with inputs for each header and data cell.
        this._renderEditorTable(content, table);

        // Allow the window to be dragged using its header.
        this._makeDraggable(win, header);

        // Determine the position of the table highlight, if available.
        const highlight = table.highlight;

        const rect = highlight
            ? highlight.getBoundingClientRect()
            : this.textarea.getBoundingClientRect();

        const winRect = win.getBoundingClientRect();

        // Calculate an initial position that stays within the viewport.
        win.style.left = Math.max(
            8,
            Math.min(
                rect.left,
                window.innerWidth - winRect.width - 8
            )
        ) + "px";

        win.style.top = Math.max(
            8,
            Math.min(
                rect.bottom + 8,
                window.innerHeight - Math.min(
                    winRect.height,
                    window.innerHeight - 16
                ) - 8
            )
        ) + "px";

        /*
         * The following positioning rules override the calculated
         * coordinates above. They are retained to preserve the
         * current centered-window behavior.
         */
        win.style.position = "fixed";
        win.style.left = "25%";
        win.style.top = "25%";
        win.style.width = "50%";
        win.style.height = "50%";

        // Mark the selected table's highlight as active.
        if (highlight) {
            highlight.classList.add("active");
        }
    }

    /**
     * Render the table as an HTML table containing editable text inputs.
     */
    _renderEditorTable(container, table) {
        container.replaceChildren();

        const htmlTable = document.createElement("table");
        htmlTable.className = "rst-editor-table";

        // Render the header row.
        const thead = document.createElement("thead");
        const headerRow = document.createElement("tr");

        table.headers.forEach((value, column) => {
            const th = document.createElement("th");

            const input = this._makeCellInput(
                value,
                true,
                0,
                column
            );

            th.appendChild(input);
            headerRow.appendChild(th);
        });

        thead.appendChild(headerRow);
        htmlTable.appendChild(thead);

        // Render the body rows.
        const tbody = document.createElement("tbody");

        table.data.forEach((row, rowIndex) => {
            const tr = document.createElement("tr");

            row.forEach((value, column) => {
                const td = document.createElement("td");

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

        /*
         * Right-clicking a cell opens the structural-editing menu.
         * The target metadata identifies the row and column to modify.
         */
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

    /**
     * Create an input for a header or data cell.
     * Input changes update the parsed table and synchronize the source.
     */
    _makeCellInput(value, isHeader, row, column) {
        const input = document.createElement("input");

        input.type = "text";
        input.value = value;

        // Store the cell coordinates for subsequent edits and context menus.
        input.dataset.header = String(isHeader);
        input.dataset.row = String(row);
        input.dataset.column = String(column);

        // Provide an accessible name describing the cell's location.
        input.setAttribute(
            "aria-label",
            `${isHeader ? "Header" : "Row " + (row + 1)}, column ${column + 1}`
        );

        // Apply each edit immediately to the table model and source text.
        input.addEventListener("input", () => {
            const table = this.activeTable;
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

    /**
     * Close the floating editor, hide the context menu,
     * and clear the active-table state.
     */
    closeEditor() {
        if (this.editorWindow) {
            this.editorWindow.remove();
            this.editorWindow = null;
        }

        this._hideContextMenu();

        // Remove active styling from all remaining highlights.
        this.tables.forEach(table => {
            table.highlight?.classList.remove("active");
        });

        this.activeTable = null;
    }

    /* --------------------------------------------------
       Context menu and structural editing
    -------------------------------------------------- */

    /**
     * Display the context menu at the requested viewport coordinates.
     * Menu placement is clamped to keep it inside the viewport.
     */
    _showContextMenu(x, y, target) {
        this._hideContextMenu();

        const menu = document.createElement("div");
        menu.className = "rst-context-menu";

        // Each action delegates to the corresponding structural operation.
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
            // Render a visual separator between row and column operations.
            if (label === "divider") {
                const divider = document.createElement("div");
                divider.className = "divider";

                menu.appendChild(divider);
                return;
            }

            const button = document.createElement("button");
            button.type = "button";
            button.textContent = label;

            button.addEventListener("click", () => {
                action();
                this._hideContextMenu();
            });

            menu.appendChild(button);
        });

        document.body.appendChild(menu);
        this.contextMenu = menu;

        // Clamp the menu coordinates after its dimensions are available.
        menu.style.left = Math.max(
            4,
            Math.min(x, window.innerWidth - menu.offsetWidth - 4)
        ) + "px";

        menu.style.top = Math.max(
            4,
            Math.min(y, window.innerHeight - menu.offsetHeight - 4)
        ) + "px";
    }

    // Remove the context menu and clear its reference.
    _hideContextMenu() {
        this.contextMenu?.remove();
        this.contextMenu = null;
    }

    /**
     * Insert an empty row before or after the selected row.
     * For header cells, insert at the beginning or end of the data.
     */
    _changeRow(target, direction) {
        const table = this.activeTable;
        if (!table) return;

        let index;

        if (target.isHeader) {
            index = direction < 0 ? 0 : table.data.length;
        } else {
            index = target.row + (direction > 0 ? 1 : 0);
        }

        // Create an empty row with the current number of columns.
        const newRow = Array(table.headers.length).fill("");

        table.data.splice(index, 0, newRow);

        this._afterStructureChange(table);
    }

    /**
     * Delete a data row.
     * Prevent deletion when only one data row remains.
     */
    _deleteRow(target) {
        const table = this.activeTable;
        if (!table || table.data.length <= 1) return;

        const index = target.isHeader ? 0 : target.row;

        // Ignore indexes that do not refer to an existing data row.
        if (index < 0 || index >= table.data.length) return;

        table.data.splice(index, 1);

        this._afterStructureChange(table);
    }

    /**
     * Insert an empty column before or after the selected column.
     * Update both the headers and every data row.
     */
    _changeColumn(target, direction) {
        const table = this.activeTable;
        if (!table) return;

        const index = target.column + (direction > 0 ? 1 : 0);

        table.headers.splice(index, 0, "");

        table.data.forEach(row => {
            row.splice(index, 0, "");
        });

        this._afterStructureChange(table);
    }

    /**
     * Delete the selected column from the header and all data rows.
     * Keep at least one column in the table.
     */
    _deleteColumn(target) {
        const table = this.activeTable;
        if (!table || table.headers.length <= 1) return;

        table.headers.splice(target.column, 1);

        table.data.forEach(row => {
            row.splice(target.column, 1);
        });

        this._afterStructureChange(table);
    }

    /**
     * Synchronize structural changes with the source and rerender
     * the editor so its inputs reflect the updated table structure.
     */
    _afterStructureChange(table) {
        this._syncSource(table);

        if (!this.activeTable || !this.editorWindow) return;

        const content = this.editorWindow.querySelector(
            ".rst-editor-content"
        );

        this._renderEditorTable(content, this.activeTable);
    }

    /* --------------------------------------------------
       Draggable floating editor
    -------------------------------------------------- */

    /**
     * Enable dragging of the floating window using its header.
     * Mouse movement is tracked on the document so dragging continues
     * even when the pointer moves outside the header.
     */
    _makeDraggable(element, handle) {
        const onMouseDown = event => {
            // Do not initiate dragging when a button is clicked.
            if (event.target.closest("button")) return;

            event.preventDefault();

            const startX = event.clientX;
            const startY = event.clientY;

            const startLeft = element.offsetLeft;
            const startTop = element.offsetTop;

            // Move the window while keeping it within the viewport.
            const onMove = moveEvent => {
                const left = Math.max(
                    0,
                    Math.min(
                        startLeft + moveEvent.clientX - startX,
                        window.innerWidth - element.offsetWidth
                    )
                );

                const top = Math.max(
                    0,
                    Math.min(
                        startTop + moveEvent.clientY - startY,
                        window.innerHeight - element.offsetHeight
                    )
                );

                element.style.left = left + "px";
                element.style.top = top + "px";
            };

            // Stop tracking mouse movement when dragging ends.
            const onUp = () => {
                document.removeEventListener("mousemove", onMove);
                document.removeEventListener("mouseup", onUp);
            };

            document.addEventListener("mousemove", onMove);
            document.addEventListener("mouseup", onUp);
        };

        handle.addEventListener("mousedown", onMouseDown);
    }

    /* --------------------------------------------------
       Cleanup and restoration
    -------------------------------------------------- */

    /**
     * Remove editor UI, listeners, and observers.
     * Restore the editable field to its original DOM position and style.
     */
    destroy() {
        // Avoid running cleanup more than once.
        if (this.destroyed) return;

        this.closeEditor();

        // Remove listeners registered on the editable field.
        this.textarea.removeEventListener("input", this._onInput);
        this.textarea.removeEventListener("scroll", this._onScroll);

        // Remove global listeners and disconnect the resize observer.
        window.removeEventListener("resize", this._onWindowResize);
        document.removeEventListener("click", this._onDocumentClick);

        this._resizeObserver?.disconnect();

        // Remove the overlay from the editable field.
        this.overlay.remove();

        // Restore the editable field to the wrapper's former location.
        if (this.wrapper.parentNode) {
            this.wrapper.parentNode.insertBefore(
                this.textarea,
                this.wrapper
            );

            this.wrapper.remove();
        }

        // Restore the exact original inline style attribute.
        if (this._originalStyle === null) {
            this.textarea.removeAttribute("style");
        } else {
            this.textarea.setAttribute("style", this._originalStyle);
        }

        // Clear table state and mark the instance as destroyed.
        this.tables = [];
        this.activeTable = null;
        this.destroyed = true;
    }
}

/**
 * Install the RST table editor for StrictDoc editable fields.
 * A MutationObserver handles dynamically inserted fields, while
 * Turbo lifecycle events trigger a fresh scan after navigation.
 */
function installTableEditor() {
    // Select multiline, contenteditable StrictDoc fields.
    const SEL_RST_EDITABLE =
        'sdoc-contenteditable[data-js-editable-field]' +
        '[data-field-type="multiline"][contenteditable="true"]';

    /**
     * Initialize an editable field only once.
     * Set the marker before construction to prevent re-entrant setup.
     */
    function initializeRSTEditor(editable) {
        if (editable.dataset.rstEditorInitialized === "true") return;

        editable.dataset.rstEditorInitialized = "true";

        new RSTTableEditor(editable);
    }

    /**
     * Scan a root element and its descendants for eligible fields.
     * The root itself is checked because it may be a matching field.
     */
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

    // Watch for matching fields added anywhere in the document.
    const rstFieldObserver = new MutationObserver(mutations => {
        for (const mutation of mutations) {
            for (const node of mutation.addedNodes) {
                // Ignore text nodes and other non-element nodes.
                if (!(node instanceof Element)) continue;

                // Scan only inserted elements that may contain target fields.
                if (
                    node.matches(SEL_RST_EDITABLE) ||
                    node.querySelector(SEL_RST_EDITABLE)
                ) {
                    scanForEditableFields(node);
                }
            }
        }
    });

    rstFieldObserver.observe(document.documentElement, {
        childList: true,
        subtree: true
    });

    // Rescan fields after Turbo page navigation or frame updates.
    document.addEventListener("turbo:load", () => {
        scanForEditableFields();
    });

    document.addEventListener("turbo:frame-load", () => {
        scanForEditableFields();
    });
}
