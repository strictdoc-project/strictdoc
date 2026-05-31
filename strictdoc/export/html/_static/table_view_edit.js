(function () {
    let editMode = false;
    let activeInlineCell = null;
    let activeAutocompleteCell = null;

    function getTable() {
        return document.querySelector('.content-view-table');
    }

    function setEditMode(on) {
        editMode = on;
        const table = getTable();
        if (table) {
            table.classList.toggle('table--is-editable', on);
        }
        const btn = document.querySelector('[data-testid="table-toolbar-edit-btn"]');
        if (btn) {
            btn.classList.toggle('is-active', on);
            btn.setAttribute('aria-pressed', on ? 'true' : 'false');
        }
        if (!on) {
            if (activeInlineCell) cancelInlineCell();
            if (activeAutocompleteCell) cancelAutocompleteCell();
        }
    }

    // --- Shared inline-cell helpers ---

    function renderTurboStream(html) {
        if (typeof Turbo !== 'undefined' && typeof Turbo.renderStreamMessage === 'function') {
            Turbo.renderStreamMessage(html);
        }
    }

    // Restores cell DOM to its pre-edit state. Call after nulling the active variable.
    function restoreInlineCellDOM(cell) {
        cell.classList.remove('cell--editing');
        if (cell._originalHTML !== undefined) {
            cell.innerHTML = cell._originalHTML;
            delete cell._originalHTML;
        }
    }

    // Saves original HTML, marks cell as editing, and fetches the inline form.
    function initInlineCellState(cell) {
        cell._originalHTML = cell.innerHTML;
        cell.removeAttribute('data-validation-error');
        cell.classList.add('cell--editing');
        fetchTurboStream(cell.dataset.url);
    }

    // --- Autocomplete cell ---

    function openAutocompleteCell(cell) {
        if (activeAutocompleteCell === cell) return;
        if (activeAutocompleteCell) cancelAutocompleteCell();
        if (activeInlineCell) saveInlineCell(activeInlineCell);

        activeAutocompleteCell = cell;
        initInlineCellState(cell);
    }

    function cancelAutocompleteCell() {
        if (!activeAutocompleteCell) return;
        const cell = activeAutocompleteCell;
        activeAutocompleteCell = null;
        restoreInlineCellDOM(cell);
    }

    async function saveAutocompleteCell(cell, ac) {
        const hiddenInput = ac.nextElementSibling;
        const rawValue = hiddenInput ? hiddenInput.value : ac.innerText;
        const newValue = rawValue.trim().replace(/,\s*$/, '').trim();
        const originalValue = (cell.dataset.currentValue || '').trim();

        if (activeAutocompleteCell === cell) {
            activeAutocompleteCell = null;
            cell.classList.remove('cell--editing');
        }

        if (newValue === originalValue) {
            if (cell._originalHTML !== undefined) {
                cell.innerHTML = cell._originalHTML;
                delete cell._originalHTML;
            }
            return;
        }

        cell.dataset.currentValue = newValue;

        const formData = new FormData();
        formData.append('node_mid', cell.dataset.nodeMid);
        formData.append('field_name', cell.dataset.fieldName);
        formData.append('field_value', newValue);

        let ok = false;
        try {
            const response = await fetch('/actions/table/update_node_field', {
                method: 'POST',
                headers: { 'Accept': 'text/vnd.turbo-stream.html' },
                body: formData,
            });
            const html = await response.text();
            if (response.ok) {
                ok = true;
                renderTurboStream(html);
            } else {
                console.error('Table autocomplete save failed:', html);
                cell.dataset.currentValue = originalValue;
                cell.setAttribute('data-validation-error', 'true');
            }
        } catch (err) {
            console.error('Table autocomplete save error:', err);
            cell.dataset.currentValue = originalValue;
        }

        if (!ok && cell._originalHTML !== undefined) {
            cell.innerHTML = cell._originalHTML;
        }
        delete cell._originalHTML;
    }

    // --- Stream fetch ---

    async function fetchTurboStream(url) {
        try {
            const response = await fetch(url, {
                headers: { 'Accept': 'text/vnd.turbo-stream.html' },
            });
            const html = await response.text();
            if (response.ok) {
                renderTurboStream(html);
            }
        } catch (err) {
            console.error('Table stream fetch error:', err);
        }
    }

    // --- Inline-form cells (contenteditable / comments / relations) ---

    function openInlineCell(cell) {
        if (activeInlineCell === cell) return;
        if (activeInlineCell) saveInlineCell(activeInlineCell);

        activeInlineCell = cell;
        initInlineCellState(cell);
    }

    function cancelInlineCell() {
        if (!activeInlineCell) return;
        const cell = activeInlineCell;
        activeInlineCell = null;
        restoreInlineCellDOM(cell);
    }

    async function saveInlineCell(cell) {
        if (!cell) return;
        activeInlineCell = null;
        cell.classList.remove('cell--editing');

        const form = cell.querySelector('form');
        if (!form) {
            // Stream not yet loaded — just restore original content
            if (cell._originalHTML !== undefined) {
                cell.innerHTML = cell._originalHTML;
                delete cell._originalHTML;
            }
            return;
        }

        const formData = new URLSearchParams(new FormData(form));

        try {
            const response = await fetch(form.action, {
                method: 'POST',
                headers: { 'Accept': 'text/vnd.turbo-stream.html' },
                body: formData,
            });
            const html = await response.text();
            if (response.ok) {
                renderTurboStream(html);
            } else {
                cell.setAttribute('data-validation-error', 'true');
                if (cell._originalHTML !== undefined) {
                    cell.innerHTML = cell._originalHTML;
                }
            }
        } catch (err) {
            console.error('Inline cell save error:', err);
            if (cell._originalHTML !== undefined) {
                cell.innerHTML = cell._originalHTML;
            }
        }

        delete cell._originalHTML;
    }

    function init() {
        const editBtn = document.querySelector('[data-testid="table-toolbar-edit-btn"]');
        if (!editBtn) return;

        editBtn.addEventListener('click', function () {
            setEditMode(!editMode);
        });

        const table = getTable();
        if (!table) return;

        table.addEventListener('click', function (e) {
            if (!editMode) return;

            // "Add comment" link inside inline comments form — fetch stream, don't navigate
            const addCommentLink = e.target.closest('[data-action-type="add_field"]');
            if (addCommentLink) {
                e.preventDefault();
                fetchTurboStream(addCommentLink.href);
                return;
            }

            const autocompleteCell = e.target.closest('[data-field-type="autocomplete"]');
            if (autocompleteCell) {
                e.preventDefault();
                openAutocompleteCell(autocompleteCell);
                return;
            }
            const inlineCell = e.target.closest(
                '[data-field-type="comments"], [data-field-type="relations"], [data-field-type="contenteditable"]'
            );
            if (inlineCell) {
                e.preventDefault();
                openInlineCell(inlineCell);
                return;
            }
        });

        // Save autocomplete cell on blur (Stimulus handles the dropdown interaction).
        // Uses capture phase to catch blur events from contenteditable sdoc-autocompletable.
        table.addEventListener('blur', function (e) {
            if (!editMode) return;
            const ac = e.target.closest('[data-controller="autocompletable"]');
            if (!ac) return;
            const cell = ac.closest('[data-field-type="autocomplete"]');
            if (!cell) return;
            setTimeout(function () {
                // If focus returned to this autocompletable (user clicked a dropdown option), skip.
                if (ac === document.activeElement || ac.contains(document.activeElement)) return;
                saveAutocompleteCell(cell, ac);
            }, 200);
        }, true);

        document.addEventListener('keydown', function (e) {
            if (e.key !== 'Escape') return;
            if (activeInlineCell) { e.preventDefault(); cancelInlineCell(); }
            if (activeAutocompleteCell) { e.preventDefault(); cancelAutocompleteCell(); }
        });

        document.addEventListener('click', function (e) {
            if (activeInlineCell && !e.composedPath().includes(activeInlineCell)) {
                saveInlineCell(activeInlineCell);
            }
            if (activeAutocompleteCell && !e.composedPath().includes(activeAutocompleteCell)) {
                saveAutocompleteCell(activeAutocompleteCell, activeAutocompleteCell.querySelector('[data-controller="autocompletable"]'));
            }
        });
    }

    window.addEventListener('load', init);
})();
