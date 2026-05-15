(function () {
    const STORAGE_KEY_PREFIX = 'strictdoc.table.hidden_cols';
    const URL_PARAM = 'hidden';

    // -------------------------------------------------------------------------
    // State I/O
    // -------------------------------------------------------------------------

    function getStorageKey() {
        return STORAGE_KEY_PREFIX + ':' + location.pathname;
    }

    // Returns array of hidden column names from URL, or null if param is absent.
    // null means "no explicit URL state" (different from [] which means "all visible").
    function readFromURL() {
        const params = new URLSearchParams(location.search);
        if (!params.has(URL_PARAM)) return null;
        const val = params.get(URL_PARAM);
        return val ? val.split('|').map(decodeURIComponent) : [];
    }

    function readFromStorage() {
        try {
            return JSON.parse(localStorage.getItem(getStorageKey()) || '[]');
        } catch (_) {
            return [];
        }
    }

    function writeToStorage(hiddenNames) {
        try {
            localStorage.setItem(getStorageKey(), JSON.stringify(hiddenNames));
        } catch (_) {}
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
        writeToStorage(hiddenNames);
        writeToURL(hiddenNames);
    }

    // -------------------------------------------------------------------------
    // Priority strategy
    //
    // URL param present → explicit state (shared link): apply it, persist to storage.
    // URL param absent  → personal preference: restore from storage, reflect in URL.
    //
    // To change the strategy, edit only this function.
    // -------------------------------------------------------------------------

    function resolveInitialHidden() {
        const fromURL = readFromURL();
        if (fromURL !== null) {
            writeToStorage(fromURL);
            return fromURL;
        }
        const fromStorage = readFromStorage();
        writeToURL(fromStorage);
        return fromStorage;
    }

    // -------------------------------------------------------------------------
    // Column visibility
    // -------------------------------------------------------------------------

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

    // -------------------------------------------------------------------------
    // Toolbar
    // -------------------------------------------------------------------------

    function buildToolbar(table, columns, onToggle) {
        const toolbar = document.createElement('div');
        toolbar.className = 'table-toolbar';

        const btn = document.createElement('button');
        btn.className = 'table-toolbar__btn action_button';
        btn.setAttribute('aria-haspopup', 'true');
        btn.setAttribute('aria-expanded', 'false');

        const panel = document.createElement('div');
        panel.className = 'table-toolbar__panel dropdown_menu';
        panel.hidden = true;
        panel.setAttribute('aria-hidden', 'true');
        panel.setAttribute('role', 'dialog');
        panel.setAttribute('aria-label', 'Column visibility');

        const panelHeader = document.createElement('div');
        panelHeader.className = 'table-toolbar__panel-header';

        const panelTitle = document.createElement('span');
        panelTitle.className = 'table-toolbar__panel-title';
        panelTitle.textContent = 'Columns';

        const resetBtn = document.createElement('button');
        resetBtn.className = 'table-toolbar__reset compact action_button';
        resetBtn.textContent = 'Show all';
        function syncResetBtn() {
            resetBtn.disabled = columns.every(c => c.visible);
        }

        resetBtn.addEventListener('click', () => {
            columns.forEach(col => onToggle(col, true));
            panel.querySelectorAll('input[type=checkbox]').forEach(cb => (cb.checked = true));
            updateBtnLabel(btn, columns);
            syncResetBtn();
        });

        panelHeader.appendChild(panelTitle);
        panelHeader.appendChild(resetBtn);
        panel.appendChild(panelHeader);

        const list = document.createElement('ul');
        list.className = 'table-toolbar__list';

        columns.forEach(col => {
            const item = document.createElement('li');
            item.className = 'table-toolbar__item';

            const label = document.createElement('label');
            label.className = 'table-toolbar__label';

            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.checked = col.visible;
            checkbox.addEventListener('change', () => {
                onToggle(col, checkbox.checked);
                updateBtnLabel(btn, columns);
                syncResetBtn();
            });

            label.appendChild(checkbox);
            label.appendChild(document.createTextNode(' ' + col.name));
            item.appendChild(label);
            list.appendChild(item);
        });

        panel.appendChild(list);

        btn.addEventListener('click', e => {
            e.stopPropagation();
            const opening = panel.hidden;
            panel.hidden = !opening;
            btn.setAttribute('aria-expanded', String(opening));
            panel.setAttribute('aria-hidden', String(!opening));
        });

        document.addEventListener('click', e => {
            if (!toolbar.contains(e.target)) {
                panel.hidden = true;
                btn.setAttribute('aria-expanded', 'false');
                panel.setAttribute('aria-hidden', 'true');
            }
        });

        toolbar.appendChild(btn);
        toolbar.appendChild(panel);

        updateBtnLabel(btn, columns);
        syncResetBtn();
        return toolbar;
    }

    function updateBtnLabel(btn, columns) {
        const hidden = columns.filter(c => !c.visible).length;
        btn.textContent = hidden > 0 ? 'Columns (' + hidden + ' hidden)' : 'Columns visibility';
    }

    // -------------------------------------------------------------------------
    // Init
    // -------------------------------------------------------------------------

    function init() {
        const table = document.querySelector('.content-view-table');
        if (!table) return;

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

        const toolbar = buildToolbar(table, columns, onToggle);
        table.parentNode.insertBefore(toolbar, table);

        headerCells.forEach((headerCell, index) => {
            headerCell.addEventListener('click', () => {
                const isAscending = headerCell.classList.contains('ascending');
                sortTable(index, !isAscending);
                headerCells.forEach(cell => cell.classList.remove('ascending', 'descending'));
                headerCell.classList.add(isAscending ? 'descending' : 'ascending');
            });
        });

        function sortTable(columnIndex, ascending) {
            const rows = Array.from(tbody.querySelectorAll(':scope > tr'));
            rows.sort((a, b) => {
                const cellA = (a.children[columnIndex] || {}).textContent || '';
                const cellB = (b.children[columnIndex] || {}).textContent || '';
                return ascending
                    ? cellA.trim().localeCompare(cellB.trim())
                    : cellB.trim().localeCompare(cellA.trim());
            });
            rows.forEach(row => tbody.appendChild(row));
        }
    }

    window.addEventListener('load', init);
})();
