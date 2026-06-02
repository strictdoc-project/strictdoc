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
        cell.removeAttribute('data-validation-error');
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

        const form = cell.querySelector('form');
        if (!form) {
            // Stream not yet loaded — just restore original content.
            // This path is synchronous (called before activeInlineCell is updated
            // to the next cell), so nulling activeInlineCell here is safe.
            activeInlineCell = null;
            cell.classList.remove('cell--editing');
            if (cell._originalHTML !== undefined) {
                cell.innerHTML = cell._originalHTML;
                delete cell._originalHTML;
            }
            return;
        }

        // Clear any previous inline errors before submitting.
        form.querySelectorAll('sdoc-form-error').forEach(el => el.remove());

        const formData = new URLSearchParams(new FormData(form));

        try {
            const response = await fetch(form.action, {
                method: 'POST',
                headers: { 'Accept': 'text/vnd.turbo-stream.html' },
                body: formData,
            });
            const html = await response.text();
            if (response.ok) {
                // Only clear activeInlineCell if this cell is still the active one.
                // When called from openInlineCell() for the previous cell, activeInlineCell
                // has already been updated to the next cell — do not overwrite it.
                if (activeInlineCell === cell) activeInlineCell = null;
                cell.classList.remove('cell--editing');
                delete cell._originalHTML;
                renderTurboStream(html);
            } else {
                if (activeInlineCell !== cell) {
                    // Called for a cell that is no longer active (openInlineCell switched to
                    // a new cell before this async response arrived). This includes the case
                    // where the user clicks away from a cell that already shows a validation
                    // error — the invalid edit is discarded and the cell is restored to its
                    // original value.
                    restoreInlineCellDOM(cell);
                } else {
                    const contentType = response.headers.get('Content-Type') || '';
                    if (contentType.includes('turbo-stream')) {
                        // Server re-rendered the form with errors in the right places.
                        // Keep activeInlineCell and cell--editing so the form stays interactive.
                        // Do NOT set data-validation-error on the cell — errors are shown inline.
                        renderTurboStream(html);
                    } else {
                        // Plain text error (single-field contenteditable): mark cell and insert errors.
                        cell.setAttribute('data-validation-error', 'true');
                        const errorLines = html.trim().split('\n').filter(Boolean);
                        const insertBeforeEl = form.querySelector('sdoc-form-row:last-of-type') || null;
                        errorLines.forEach(line => {
                            const errorEl = document.createElement('sdoc-form-error');
                            errorEl.textContent = line.trim();
                            if (insertBeforeEl) {
                                form.insertBefore(errorEl, insertBeforeEl);
                            } else {
                                form.appendChild(errorEl);
                            }
                        });
                    }
                }
            }
        } catch (err) {
            console.error('Inline cell save error:', err);
            // Same guard as the success path: don't clear activeInlineCell if it has
            // already moved on to another cell.
            if (activeInlineCell === cell) activeInlineCell = null;
            restoreInlineCellDOM(cell);
        }
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
            if (e.key === 'Escape') {
                if (activeInlineCell) { e.preventDefault(); cancelInlineCell(); }
                if (activeAutocompleteCell) { e.preventDefault(); cancelAutocompleteCell(); }
                return;
            }
            if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
                if (activeInlineCell && (
                    activeInlineCell.dataset.fieldType === 'contenteditable' ||
                    activeInlineCell.dataset.fieldType === 'comments'
                )) {
                    e.preventDefault();
                    saveInlineCell(activeInlineCell);
                }
            }
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
