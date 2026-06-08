(function () {
    const TURBO_ACCEPT = 'text/vnd.turbo-stream.html';

    // DOM contract for table-view inline editing.
    // The script is attached to the container marked with js-table_view_edit.
    // Inside it, js-table_view_edit-field marks editable fields and its value
    // selects the handling path: "autocomplete", "contenteditable", "comments",
    // or "relations". js-table_view_edit-add-field marks links that add comment
    // or relation rows into an open inline form. js-table_view_edit-form marks
    // the form submitted for a field; it may be nested inside that field or wrap
    // several fields, as planned for the document custom-metadata editor.
    // js-table_view_edit-submit-unchanged marks creation fields whose initial
    // empty form state must still be submitted so backend validation can run.
    const ATTR_CONTAINER = 'js-table_view_edit';
    const ATTR_TABLE = 'js-table_view_edit-table';
    const ATTR_TOGGLE = 'js-table_view_edit-toggle';
    const ATTR_FIELD = 'js-table_view_edit-field';
    const ATTR_ADD_FIELD = 'js-table_view_edit-add-field';
    const ATTR_FORM = 'js-table_view_edit-form';
    const ATTR_SUBMIT_UNCHANGED = 'js-table_view_edit-submit-unchanged';
    const ATTR_CUSTOM_META_ROW = 'js-table_view_edit-custom_meta-row';
    const ATTR_CUSTOM_META_DELETE_ACTION =
        'js-table_view_edit-custom_meta-delete_action';
    const ATTR_CUSTOM_META_DRAG_HANDLE =
        'js-table_view_edit-custom_meta-drag_handle';
    const ATTR_CUSTOM_META_NAME = 'js-table_view_edit-custom_meta-name';

    const FIELD_AUTOCOMPLETE = 'autocomplete';
    const FIELD_CONTENTEDITABLE = 'contenteditable';
    const FIELD_COMMENTS = 'comments';
    const FIELD_RELATIONS = 'relations';

    let editMode = false;
    let activeInlineCell = null;
    let activeAutocompleteCell = null;
    // [FEATURE: passive-open] Cell to open after the current save resolves.
    let pendingNextCell = null;
    let customMetaReorderPending = false;
    const customMetaDragState = {
        row: null,
        originalNextSibling: null,
        targetRow: null,
        position: null,
    };

    function getMainContainer() {
        return document.querySelector(`[${ATTR_CONTAINER}]`);
    }

    function getTable() {
        return document.querySelector(`[${ATTR_TABLE}]`);
    }

    function getHandler() {
        return document.querySelector(`[${ATTR_TOGGLE}]`);
    }

    function getFieldForm(field) {
        // Most inline forms are injected inside their editable field. A shared
        // form may instead wrap several fields, so both supported placements
        // are part of the explicit table-view editing DOM contract.
        return (
            field.querySelector(`[${ATTR_FORM}]`) ||
            field.closest(`[${ATTR_FORM}]`)
        );
    }

    function clearFieldErrors(field) {
        // Most inline editors contain all of their errors inside the active
        // field. Custom metadata fields share one form, so clearing the whole
        // form would also remove errors from other still-open metadata rows.
        const errorScope =
            field.closest(`[${ATTR_CUSTOM_META_ROW}]`) || field;
        errorScope
            .querySelectorAll('sdoc-form-error')
            .forEach(error => error.remove());
    }

    function updateMode(item, mode) {
        if (mode) {
            item?.setAttribute('data-mode', mode);
        } else { // mode == "" or not present
            item?.removeAttribute('data-mode');
        }
    }

    function updateButtonState(item, state) {
        item?.setAttribute('aria-pressed', state ? 'true' : 'false');
    }

    function setEditMode(on) {
        editMode = on;
        const main = getMainContainer();
        const table = getTable();
        const btn = getHandler();
        if (on) {
            updateMode(main, 'edit');
            updateMode(table, 'editable');
            updateButtonState(btn, true);
        } else {
            updateMode(main);
            updateMode(table);
            updateButtonState(btn);
            pendingNextCell = null;
            if (activeInlineCell) cancelInlineCell();
            if (activeAutocompleteCell) cancelAutocompleteCell();
            // [FEATURE: passive-open] Close any cells that are open but no longer
            // tracked (passive-open after a validation error).
            document.querySelectorAll(`[${ATTR_FIELD}][data-mode="editing"]`).forEach(cell => restoreInlineCellDOM(cell));
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
        updateMode(cell);
        cell.removeAttribute('data-validation-error');
        clearFieldErrors(cell);
        if (cell._originalHTML !== undefined) {
            cell.innerHTML = cell._originalHTML;
            delete cell._originalHTML;
        }
        delete cell._originalFormData;
    }

    // Saves original HTML, marks cell as editing, and fetches the inline form.
    function initInlineCellState(cell) {
        cell._originalHTML = cell.innerHTML;
        cell.removeAttribute('data-validation-error');
        updateMode(cell, 'editing');
        fetchTurboStream(cell.dataset.url, cell);
    }

    // --- Autocomplete cell ---

    function getAutocompleteInput(cell) {
        // Autocomplete follows the same external field contract as all other
        // edit modes: js-table_view_edit-field is set on the cell/container.
        // The save path still needs the inner sdoc-autocompletable control
        // because its sibling hidden input contains the normalized value.
        return cell.querySelector('sdoc-autocompletable');
    }

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
            cell.removeAttribute('data-mode');
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
                headers: { 'Accept': TURBO_ACCEPT },
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

    async function fetchTurboStream(url, cell = null) {
        try {
            const response = await fetch(url, {
                headers: { 'Accept': TURBO_ACCEPT },
            });
            const html = await response.text();
            if (response.ok) {
                renderTurboStream(html);
                // [FEATURE: skip-save-if-unchanged]
                // Capture the serialized form state right after the server renders it —
                // before any user input. Used in saveInlineCell to skip the POST when
                // nothing has changed.
                if (cell) {
                    const form = getFieldForm(cell);
                    if (form) {
                        cell._originalFormData = new URLSearchParams(new FormData(form)).toString();
                    }
                }
            }
        } catch (err) {
            console.error('Table stream fetch error:', err);
        }
    }

    // --- Inline-form cells (contenteditable / comments / relations) ---

    function openInlineCell(cell) {
        if (activeInlineCell === cell) return;
        if (activeInlineCell) {
            // [FEATURE: passive-open] Null activeInlineCell immediately so the
            // document.click handler (which fires after table.click) doesn't see
            // it and trigger a second save. Remember the intended next cell — it
            // will be opened only if the save succeeds.
            const prev = activeInlineCell;
            activeInlineCell = null;
            pendingNextCell = cell;
            saveInlineCell(prev);
            return;
        }
        pendingNextCell = null;
        activeInlineCell = cell;
        // [FEATURE: passive-open] If the cell is already open (passive-open after a
        // validation error), don't re-fetch the form — just reactivate it in place.
        if (cell.getAttribute('data-mode') === 'editing') return;
        initInlineCellState(cell);
    }

    // [FEATURE: passive-open] Open the cell that was clicked while a save was
    // in flight. Called after a successful save (or skip-save) to complete the
    // cell-switch that was deferred by openInlineCell.
    function openPendingCell() {
        if (pendingNextCell) {
            const next = pendingNextCell;
            pendingNextCell = null;
            openInlineCell(next);
        }
    }

    function cancelInlineCell() {
        if (!activeInlineCell) return;
        pendingNextCell = null;
        const cell = activeInlineCell;
        activeInlineCell = null;
        restoreInlineCellDOM(cell);
    }

    function clearCustomMetaDragState() {
        customMetaDragState.row?.removeAttribute('data-dragging');
        customMetaDragState.targetRow?.removeAttribute('data-drop-position');
        customMetaDragState.row = null;
        customMetaDragState.originalNextSibling = null;
        customMetaDragState.targetRow = null;
        customMetaDragState.position = null;
    }

    function setCustomMetaDropTarget(row, position) {
        customMetaDragState.targetRow?.removeAttribute('data-drop-position');
        customMetaDragState.targetRow = row;
        customMetaDragState.position = position;
        row?.setAttribute('data-drop-position', position);
    }

    async function saveCustomMetaReorder(row, originalNextSibling) {
        const form = row.closest(`[${ATTR_FORM}]`);
        if (!form) return;

        customMetaReorderPending = true;
        const formData = new URLSearchParams(new FormData(form));
        formData.set('action', 'reorder');
        formData.set('active_form_key', row.dataset.formKey);

        try {
            const response = await fetch(form.action, {
                method: 'POST',
                headers: { 'Accept': TURBO_ACCEPT },
                body: formData,
            });
            const html = await response.text();
            if (response.ok) {
                renderTurboStream(html);
                return;
            }
            console.error('Custom metadata reorder failed:', html);
        } catch (err) {
            console.error('Custom metadata reorder error:', err);
        } finally {
            customMetaReorderPending = false;
        }

        form.insertBefore(row, originalNextSibling);
    }

    async function deleteCustomMetaRow(deleteAction) {
        const row = deleteAction.closest(`[${ATTR_CUSTOM_META_ROW}]`);
        const form = row?.closest(`[${ATTR_FORM}]`);
        if (!row || !form) return;

        if (activeInlineCell) cancelInlineCell();
        if (activeAutocompleteCell) cancelAutocompleteCell();

        const formKey = row.dataset.formKey;
        const nextSibling = row.nextSibling;
        row.remove();

        const formData = new URLSearchParams(new FormData(form));
        formData.set('action', 'delete');
        formData.set('active_form_key', formKey);

        try {
            const response = await fetch(form.action, {
                method: 'POST',
                headers: { 'Accept': TURBO_ACCEPT },
                body: formData,
            });
            const html = await response.text();
            if (response.ok) {
                renderTurboStream(html);
                return;
            }
            console.error('Custom metadata delete failed:', html);
        } catch (err) {
            console.error('Custom metadata delete error:', err);
        }

        form.insertBefore(row, nextSibling);
    }

    async function saveInlineCell(cell) {
        if (!cell) return;

        const form = getFieldForm(cell);
        if (!form) {
            // Stream not yet loaded — restore original content without saving.
            // activeInlineCell is already null when called from openInlineCell
            // (nulled there to prevent document.click double-save), but may still
            // be set when called from document.click directly.
            activeInlineCell = null;
            restoreInlineCellDOM(cell);
            openPendingCell();
            return;
        }

        // [FEATURE: skip-save-if-unchanged]
        // Compare current form state against the snapshot taken when the form loaded.
        // If identical — close the cell without sending a request to the server.
        const currentData = new URLSearchParams(new FormData(form)).toString();
        if (
            !cell.hasAttribute(ATTR_SUBMIT_UNCHANGED) &&
            cell._originalFormData !== undefined &&
            currentData === cell._originalFormData
        ) {
            if (activeInlineCell === cell) activeInlineCell = null;
            restoreInlineCellDOM(cell);
            openPendingCell();
            return;
        }

        // Clear only errors belonging to the field being submitted.
        clearFieldErrors(cell);

        const formData = new URLSearchParams(new FormData(form));
        const activeFormKey = cell.querySelector(
            'input[name="active_form_key"]'
        )?.value;
        if (activeFormKey !== undefined) {
            // A shared custom-metadata form may contain several passive-open
            // rows, each with its own active_form_key input. The cell being
            // saved must determine which row receives the validation stream.
            formData.set('active_form_key', activeFormKey);
        }

        try {
            const response = await fetch(form.action, {
                method: 'POST',
                headers: { 'Accept': TURBO_ACCEPT },
                body: formData,
            });
            const html = await response.text();
            if (response.ok) {
                // Only clear activeInlineCell if this cell is still the active one.
                // When called via openInlineCell, activeInlineCell was already nulled
                // there — don't overwrite it if it has moved on to another cell.
                if (activeInlineCell === cell) activeInlineCell = null;
                cell.removeAttribute('data-mode');
                delete cell._originalHTML;
                delete cell._originalFormData;
                renderTurboStream(html);
                // [FEATURE: passive-open] Open the cell the user clicked while this
                // save was in flight (set by openInlineCell before starting the save).
                openPendingCell();
            } else {
                // [FEATURE: passive-open] Validation error — go passive-open regardless
                // of whether save was triggered by click-outside or by a cell switch.
                // Discard pendingNextCell: the next cell must not open while this one has an error.
                if (activeInlineCell === cell) activeInlineCell = null;
                pendingNextCell = null;
                const contentType = response.headers.get('Content-Type') || '';
                if (contentType.includes('turbo-stream')) {
                    // Server re-rendered the form with errors in the right places.
                    // data-mode='editing' stays — form remains visible and interactive.
                    renderTurboStream(html);
                } else {
                    // Validation responses are currently HTMLResponse objects whose
                    // body is plain text. A 5xx response, however, contains a full
                    // error page and must never be split into field-error elements.
                    cell.setAttribute('data-validation-error', 'true');
                    const errorLines = response.status >= 500
                        ? ['Unable to save this field.']
                        : html.trim().split('\n').filter(Boolean);
                    if (response.status >= 500) {
                        console.error('Inline cell server error:', html);
                    }
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
        } catch (err) {
            console.error('Inline cell save error:', err);
            // Network error — restore cell and discard any pending next cell.
            if (activeInlineCell === cell) activeInlineCell = null;
            pendingNextCell = null;
            restoreInlineCellDOM(cell);
        }
    }

    function init() {
        const editBtn = getHandler();
        if (!editBtn) return;

        editBtn.addEventListener('click', function () {
            setEditMode(!editMode);
        });

        const main = getMainContainer();
        if (!main) return;

        // One delegated click handler for all editable fields in the main table view:
        // both regular table cells and document-level fields above the table.
        main.addEventListener('click', function (e) {
            if (!editMode) return;

            const customMetaDeleteAction = e.target.closest(
                `[${ATTR_CUSTOM_META_DELETE_ACTION}]`
            );
            if (customMetaDeleteAction) {
                e.preventDefault();
                deleteCustomMetaRow(customMetaDeleteAction);
                return;
            }

            const customMetaDragHandle = e.target.closest(
                `[${ATTR_CUSTOM_META_DRAG_HANDLE}]`
            );
            if (customMetaDragHandle) {
                e.preventDefault();
                return;
            }

            // "Add comment" / "Add relation" link inside inline form — fetch stream, don't navigate
            const addCommentLink = e.target.closest(`[${ATTR_ADD_FIELD}]`);
            if (addCommentLink) {
                e.preventDefault();
                fetchTurboStream(addCommentLink.href);
                return;
            }

            const editableField = e.target.closest(`[${ATTR_FIELD}]`);
            if (!editableField) return;

            const fieldType = editableField.getAttribute(ATTR_FIELD);
            if (fieldType === FIELD_AUTOCOMPLETE) {
                e.preventDefault();
                openAutocompleteCell(editableField);
                return;
            }
            if (
                fieldType === FIELD_CONTENTEDITABLE ||
                fieldType === FIELD_COMMENTS ||
                fieldType === FIELD_RELATIONS
            ) {
                e.preventDefault();
                openInlineCell(editableField);
                return;
            }
        });

        main.addEventListener('dragstart', function (e) {
            if (!editMode || customMetaReorderPending) {
                e.preventDefault();
                return;
            }
            const dragHandle = e.target.closest(
                `[${ATTR_CUSTOM_META_DRAG_HANDLE}]`
            );
            const row = dragHandle?.closest(`[${ATTR_CUSTOM_META_ROW}]`);
            if (!row) return;

            if (activeInlineCell) cancelInlineCell();
            if (activeAutocompleteCell) cancelAutocompleteCell();

            customMetaDragState.row = row;
            customMetaDragState.originalNextSibling = row.nextSibling;
            row.setAttribute('data-dragging', 'true');
            e.dataTransfer.effectAllowed = 'move';
            e.dataTransfer.setData('text/plain', row.dataset.formKey);
        });

        main.addEventListener('dragover', function (e) {
            const draggedRow = customMetaDragState.row;
            const targetRow = e.target.closest(`[${ATTR_CUSTOM_META_ROW}]`);
            if (!draggedRow || !targetRow || draggedRow === targetRow) {
                setCustomMetaDropTarget(null, null);
                return;
            }

            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';
            const targetName = targetRow.querySelector(
                `[${ATTR_CUSTOM_META_NAME}]`
            );
            if (!targetName) return;
            const targetBounds = targetName.getBoundingClientRect();
            const position =
                e.clientY < targetBounds.top + targetBounds.height / 2
                    ? 'before'
                    : 'after';
            setCustomMetaDropTarget(targetRow, position);
        });

        main.addEventListener('drop', function (e) {
            const row = customMetaDragState.row;
            const targetRow = customMetaDragState.targetRow;
            const position = customMetaDragState.position;
            const originalNextSibling =
                customMetaDragState.originalNextSibling;
            if (!row || !targetRow || !position) {
                clearCustomMetaDragState();
                return;
            }

            e.preventDefault();
            const form = row.closest(`[${ATTR_FORM}]`);
            if (!form) {
                clearCustomMetaDragState();
                return;
            }
            const originalOrder = Array.from(
                form.querySelectorAll(`[${ATTR_CUSTOM_META_ROW}]`)
            );
            if (position === 'before') {
                form.insertBefore(row, targetRow);
            } else {
                form.insertBefore(row, targetRow.nextSibling);
            }
            const reorderedRows = Array.from(
                form.querySelectorAll(`[${ATTR_CUSTOM_META_ROW}]`)
            );
            const orderChanged = originalOrder.some(
                (originalRow, index) => originalRow !== reorderedRows[index]
            );
            clearCustomMetaDragState();
            if (orderChanged) {
                saveCustomMetaReorder(row, originalNextSibling);
            }
        });

        main.addEventListener('dragend', function () {
            clearCustomMetaDragState();
        });

        // Save autocomplete cell on blur (Stimulus handles the dropdown interaction).
        // Uses capture phase to catch blur events from contenteditable sdoc-autocompletable.
        main.addEventListener('blur', function (e) {
            if (!editMode) return;
            const cell = e.target.closest(`[${ATTR_FIELD}="${FIELD_AUTOCOMPLETE}"]`);
            if (!cell) return;
            const ac = getAutocompleteInput(cell);
            if (!ac || !ac.contains(e.target)) return;
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
                const fieldType = activeInlineCell?.getAttribute(ATTR_FIELD);
                if (activeInlineCell && (
                    fieldType === FIELD_CONTENTEDITABLE ||
                    fieldType === FIELD_COMMENTS
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
                saveAutocompleteCell(activeAutocompleteCell, getAutocompleteInput(activeAutocompleteCell));
            }
        });
    }

    window.addEventListener('load', init);
})();
