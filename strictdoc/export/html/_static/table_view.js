(function () {
    const STORAGE_KEY_PREFIX = 'strictdoc.table.hidden_cols';
    const ROWS_STORAGE_KEY_PREFIX = 'strictdoc.table.hidden_rows';
    const URL_PARAM = 'hidden';

    /*
     * State I/O
     */

    function storageKey(prefix) {
        return prefix + ':' + location.pathname;
    }

    function readJson(key) {
        try {
            return JSON.parse(localStorage.getItem(key) || '[]');
        } catch (_) {
            return [];
        }
    }

    function writeJson(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (_) {}
    }

    // Returns array of hidden column names from URL, or null if param is absent.
    // null means "no explicit URL state" (different from [] which means "all visible").
    function readFromURL() {
        const params = new URLSearchParams(location.search);
        if (!params.has(URL_PARAM)) return null;
        const val = params.get(URL_PARAM);
        return val ? val.split('|').map(decodeURIComponent) : [];
    }

    function writeToURL(hiddenNames) {
        // Build the hidden param manually to avoid URLSearchParams encoding '|' as '%7C'.
        const params = new URLSearchParams(location.search);
        params.delete(URL_PARAM);
        const rest = params.toString();

        let search = '';
        if (hiddenNames.length > 0) {
            const hiddenStr = URL_PARAM + '=' + hiddenNames.map(encodeURIComponent).join('|');
            search = '?' + (rest ? hiddenStr + '&' + rest : hiddenStr);
        } else if (rest) {
            search = '?' + rest;
        }

        history.replaceState(null, '', location.pathname + search + location.hash);
    }

    function persistState(hiddenNames) {
        writeJson(storageKey(STORAGE_KEY_PREFIX), hiddenNames);
        writeToURL(hiddenNames);
    }

    /*
     * Priority strategy
     *
     * URL param present → explicit state (shared link): apply it, persist to storage.
     * URL param absent  → personal preference: restore from storage, reflect in URL.
     *
     * To change the strategy, edit only this function.
     */

    function resolveInitialHidden() {
        const fromURL = readFromURL();
        if (fromURL !== null) {
            writeJson(storageKey(STORAGE_KEY_PREFIX), fromURL);
            return fromURL;
        }
        const fromStorage = readJson(storageKey(STORAGE_KEY_PREFIX));
        writeToURL(fromStorage);
        return fromStorage;
    }

    /*
     * Column visibility
     */

    function setColumnVisibility(table, index, visible) {
        const ths = table.querySelectorAll(':scope > thead > tr > th');
        if (ths[index]) ths[index].style.display = visible ? '' : 'none';
        table.querySelectorAll(':scope > tbody > tr').forEach(row => {
            const cell = row.children[index];
            if (cell) cell.style.display = visible ? '' : 'none';
        });
    }

    function applyHiddenNames(table, columns, hiddenNames) {
        const hiddenSet = new Set(hiddenNames);
        columns.forEach(col => {
            col.visible = !hiddenSet.has(col.name);
            setColumnVisibility(table, col.index, col.visible);
        });
    }

    /*
     * Shared panel helpers
     */

    function updateBtnLabel(btn, items) {
        const hidden = items.filter(i => !i.visible).length;
        const infoEl = btn.querySelector('.table-toolbar__btn-info');
        infoEl.textContent = hidden > 0 ? ' • ' + hidden + ' hidden' : '';
    }

    function syncResetBtn(resetBtn, items) {
        resetBtn.disabled = items.every(i => i.visible);
    }

    function openPanel(btn, panel) {
        panel.hidden = false;
        btn.setAttribute('aria-expanded', 'true');
        panel.setAttribute('aria-hidden', 'false');
    }

    function closePanel(btn, panel) {
        panel.hidden = true;
        btn.setAttribute('aria-expanded', 'false');
        panel.setAttribute('aria-hidden', 'true');
    }

    // panels registry — populated by each initXxxPanel() call
    const _panels = [];

    function closeAllPanels() {
        _panels.forEach(({ btn, panel }) => closePanel(btn, panel));
    }

    function initPanelToggle(btn, panel) {
        btn.addEventListener('click', e => {
            e.stopPropagation();
            const opening = panel.hidden;
            closeAllPanels();
            if (opening) openPanel(btn, panel);
        });
    }

    /*
     * Checkbox list item
     * Uses template-icon-checkbox from components/checkbox/index.jinja.
     * Expected: <label class="icon-checkbox"> with <input type="checkbox"> and <span>
     */

    function createCheckboxItem(testid, checked, label, onChange) {
        const tmpl = document.getElementById('template-icon-checkbox');
        const item = document.createElement('li');
        item.className = 'table-toolbar__item';
        const labelEl = tmpl.content.cloneNode(true).querySelector('label');
        const checkbox = labelEl.querySelector('input[type=checkbox]');
        const text = labelEl.querySelector('span');

        checkbox.checked = checked;
        labelEl.setAttribute('data-testid', testid);
        checkbox.addEventListener('change', () => onChange(checkbox.checked));

        text.textContent = label;
        item.appendChild(labelEl);
        return item;
    }

    /*
     * Columns panel
     */

    function initColumnsPanel(table, columns, onToggle) {
        const btn = document.querySelector('[data-testid="table-toolbar-columns-btn"]');
        const panel = document.querySelector('[data-testid="table-toolbar-columns-panel"]');
        const resetBtn = document.querySelector('[data-testid="table-toolbar-columns-reset"]');
        const list = document.querySelector('[data-testid="table-toolbar-columns-list"]');

        _panels.push({ btn, panel });

        columns.forEach(col => {
            list.appendChild(createCheckboxItem(
                'col-checkbox-' + col.name,
                col.visible,
                col.name,
                (checked) => {
                    onToggle(col, checked);
                    updateBtnLabel(btn, columns);
                    syncResetBtn(resetBtn, columns);
                }
            ));
        });

        resetBtn.addEventListener('click', () => {
            columns.forEach(col => onToggle(col, true));
            list.querySelectorAll('input[type=checkbox]').forEach(cb => (cb.checked = true));
            updateBtnLabel(btn, columns);
            syncResetBtn(resetBtn, columns);
        });

        initPanelToggle(btn, panel);

        updateBtnLabel(btn, columns);
        syncResetBtn(resetBtn, columns);
    }

    /*
     * Row visibility
     */

    function setRowTypeVisibility(tbody, type, visible) {
        tbody.querySelectorAll(':scope > tr[data-row-type="' + type + '"]').forEach(row => {
            row.style.display = visible ? '' : 'none';
        });
    }

    function initRowsPanel(tbody) {
        const btn = document.querySelector('[data-testid="table-toolbar-rows-btn"]');
        const panel = document.querySelector('[data-testid="table-toolbar-rows-panel"]');
        const resetBtn = document.querySelector('[data-testid="table-toolbar-rows-reset"]');
        const list = document.querySelector('[data-testid="table-toolbar-rows-list"]');

        _panels.push({ btn, panel });

        // Collect unique row types from the tbody, preserving first-seen order.
        const seenTypes = [];
        tbody.querySelectorAll(':scope > tr[data-row-type]').forEach(row => {
            const t = row.dataset.rowType;
            if (!seenTypes.includes(t)) seenTypes.push(t);
        });

        // Restore state from storage.
        const rowsKey = storageKey(ROWS_STORAGE_KEY_PREFIX);
        const hiddenTypes = new Set(readJson(rowsKey));
        seenTypes.forEach(type => {
            if (hiddenTypes.has(type)) setRowTypeVisibility(tbody, type, false);
        });

        const rowTypes = seenTypes.map(type => ({ type, visible: !hiddenTypes.has(type) }));

        rowTypes.forEach(rowType => {
            list.appendChild(createCheckboxItem(
                'row-checkbox-' + rowType.type,
                rowType.visible,
                rowType.type,
                (checked) => {
                    rowType.visible = checked;
                    setRowTypeVisibility(tbody, rowType.type, checked);
                    writeJson(rowsKey, rowTypes.filter(r => !r.visible).map(r => r.type));
                    updateBtnLabel(btn, rowTypes);
                    syncResetBtn(resetBtn, rowTypes);
                }
            ));
        });

        resetBtn.addEventListener('click', () => {
            rowTypes.forEach(rowType => {
                rowType.visible = true;
                setRowTypeVisibility(tbody, rowType.type, true);
            });
            list.querySelectorAll('input[type=checkbox]').forEach(cb => (cb.checked = true));
            writeJson(rowsKey, []);
            updateBtnLabel(btn, rowTypes);
            syncResetBtn(resetBtn, rowTypes);
        });

        initPanelToggle(btn, panel);

        updateBtnLabel(btn, rowTypes);
        syncResetBtn(resetBtn, rowTypes);
    }

    /*
     * Init
     */

    function init() {
        const table = document.querySelector('.content-view-table');
        if (!table) return;

        const toolbar = document.querySelector('[data-testid="table-toolbar"]');
        const headerCells = Array.from(table.querySelectorAll(':scope > thead > tr > .content-view-th'));
        const tbody = table.querySelector(':scope > tbody');

        const columns = headerCells.map((th, index) => ({
            index,
            name: th.textContent.trim(),
            visible: true,
        }));

        const hiddenNames = resolveInitialHidden();
        applyHiddenNames(table, columns, hiddenNames);

        function onToggle(col, visible) {
            col.visible = visible;
            setColumnVisibility(table, col.index, visible);
            persistState(columns.filter(c => !c.visible).map(c => c.name));
        }

        initColumnsPanel(table, columns, onToggle);
        initRowsPanel(tbody);

        document.addEventListener('click', e => {
            if (toolbar && !toolbar.contains(e.target)) {
                closeAllPanels();
            }
        });

        /*
         * Column sorting
         *
         * The sort logic (save originalRows, sort by textContent, restore on reset)
         * mirrors source_coverage_screen.js — a shared pattern, candidate for future
         * extraction into a common helper.
         *
         * Three-state cycle per column: none → asc → desc → none.
         * State is stored in data-sort attribute on <th>; CSS uses it to show
         * the matching icon variant (.sort-none / .sort-asc / .sort-desc).
         * Only the sort icon button triggers sorting, not the full <th>.
         */

        const originalRows = Array.from(tbody.querySelectorAll(':scope > tr'));
        let sortState = null; // { index, dir: 'asc'|'desc' }

        const sortResetWrapper = document.querySelector('.table-toolbar__sort-reset');
        const sortResetBtn = document.querySelector('[data-testid="table-toolbar-sort-reset"]');

        function setSortReset(active) {
            if (sortResetWrapper) sortResetWrapper.hidden = !active;
        }

        function clearSortUI() {
            headerCells.forEach(cell => cell.removeAttribute('data-sort'));
        }

        function applySort(index, dir) {
            const rows = Array.from(tbody.querySelectorAll(':scope > tr'));
            // Same comparator as source_coverage_screen.js (textContent / localeCompare).
            rows.sort((a, b) => {
                const cellA = (a.children[index] || {}).textContent || '';
                const cellB = (b.children[index] || {}).textContent || '';
                return dir === 'asc'
                    ? cellA.trim().localeCompare(cellB.trim())
                    : cellB.trim().localeCompare(cellA.trim());
            });
            rows.forEach(row => tbody.appendChild(row));
        }

        headerCells.forEach((headerCell, index) => {
            const sortBtn = headerCell.querySelector('.content-view-th__sort-btn');
            if (!sortBtn) return;

            sortBtn.addEventListener('click', e => {
                e.stopPropagation();
                const current = headerCell.getAttribute('data-sort'); // null | 'asc' | 'desc'
                const next = current === null ? 'asc' : current === 'asc' ? 'desc' : null;

                clearSortUI();

                if (next === null) {
                    // Reset to server-provided order.
                    originalRows.forEach(row => tbody.appendChild(row));
                    sortState = null;
                    setSortReset(false);
                } else {
                    headerCell.setAttribute('data-sort', next);
                    applySort(index, next);
                    sortState = { index, dir: next };
                    setSortReset(true);
                }
            });
        });

        if (sortResetBtn) {
            sortResetBtn.addEventListener('click', () => {
                clearSortUI();
                originalRows.forEach(row => tbody.appendChild(row));
                sortState = null;
                setSortReset(false);
            });
        }
    }

    window.addEventListener('load', init);
})();
