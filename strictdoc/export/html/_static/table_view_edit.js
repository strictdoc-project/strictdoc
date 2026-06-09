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
    const ATTR_ADD_NODE = 'js-table_view_edit-add-node';
    const ATTR_ADD_NODE_HANDLE = 'js-table_view_edit-add-node-handle';
    const ATTR_ADD_NODE_MENU = 'js-table_view_edit-add-node-menu';
    const ATTR_ADD_NODE_ACTION = 'js-table_view_edit-add-node-action';
    const ATTR_ADD_NODE_ACTIONS = 'js-table_view_edit-add-node-actions';
    const ATTR_ADD_NODE_BLOCKERS = 'js-table_view_edit-add-node-blockers';
    const ATTR_ADD_NODE_UNBLOCK = 'js-table_view_edit-add-node-unblock';
    const ADD_NODE_FEEDBACK_ID = 'table-add-node-feedback';
    const EVENT_BEFORE_TABLE_STATE_CHANGE =
        'strictdoc:table-view-before-state-change';
    const EVENT_AFTER_TABLE_STATE_CHANGE =
        'strictdoc:table-view-after-state-change';
    const ATTR_CUSTOM_META_ROW = 'js-table_view_edit-custom_meta-row';
    const ATTR_CUSTOM_META_DELETE_ACTION =
        'js-table_view_edit-custom_meta-delete_action';
    const ATTR_CUSTOM_META_DRAG_HANDLE =
        'js-table_view_edit-custom_meta-drag_handle';

    const FIELD_AUTOCOMPLETE = 'autocomplete';
    const FIELD_CONTENTEDITABLE = 'contenteditable';
    const FIELD_COMMENTS = 'comments';
    const FIELD_RELATIONS = 'relations';
    const INLINE_FIELD_TYPES = new Set([
        FIELD_CONTENTEDITABLE,
        FIELD_COMMENTS,
        FIELD_RELATIONS,
    ]);

    let editMode = false;
    let activeInlineCell = null;
    let activeAutocompleteCell = null;
    let activeAddNode = null;
    let addNodeUnblockInProgress = false;
    let pendingTableStateAnchor = null;
    // [FEATURE: passive-open] Cell to open after the current save resolves.
    let pendingNextCell = null;
    let customMetaReorderPending = false;
    const customMetaDragState = {
        armedRow: null,
        row: null,
        originalNextSibling: null,
        targetRow: null,
        position: null,
    };
    // Keep editing state outside DOM elements. Each cell has an independent
    // state object, so requests for different cells are allowed to run in
    // parallel.
    const cellStates = new WeakMap();

    function getCellState(cell) {
        let state = cellStates.get(cell);
        if (!state) {
            state = {
                // Display markup restored when editing is cancelled or fails.
                originalHTML: undefined,
                // Serialized form used to skip an unchanged inline save.
                originalFormData: undefined,
                // Shared by duplicate save triggers for this cell.
                savePromise: null,
                // Delayed blur save used by autocomplete dropdown interaction.
                autocompleteBlurTimer: null,
            };
            cellStates.set(cell, state);
        }
        return state;
    }

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
            closeAddNodeMenu();
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

    function getAddNodeFeedback() {
        return document.getElementById(ADD_NODE_FEEDBACK_ID);
    }

    function getAddNodeMenu(addNode) {
        return addNode?.querySelector(`[${ATTR_ADD_NODE_MENU}]`);
    }

    function getAddNodeState(addNode) {
        return addNode?.querySelector('[js-table_view_edit-add-node-state]');
    }

    function getAddNodeActions(addNode) {
        return addNode?.querySelector(`[${ATTR_ADD_NODE_ACTIONS}]`);
    }

    function getAddNodeBlockersContainer(addNode) {
        return addNode?.querySelector(`[${ATTR_ADD_NODE_BLOCKERS}]`);
    }

    function captureViewportAnchor(element, preserveLeft = false) {
        if (!element) return null;
        const bounds = element.getBoundingClientRect();
        const scrollContainer =
            element.closest('.main') || document.scrollingElement;
        return {
            element,
            left: bounds.left,
            preserveLeft,
            scrollContainer,
            top: bounds.top,
        };
    }

    function restoreViewportAnchor(anchor, element = anchor?.element) {
        if (!anchor) return;
        if (!element?.isConnected) return;
        const bounds = element.getBoundingClientRect();
        if (anchor.preserveLeft) {
            anchor.scrollContainer.scrollLeft += bounds.left - anchor.left;
        }
        anchor.scrollContainer.scrollTop += bounds.top - anchor.top;
    }

    function setAddNodeMessage(addNode, message, isError = false) {
        const state = getAddNodeState(addNode);
        if (!state) return;
        if (!message) {
            state.textContent = '';
            state.hidden = true;
            state.classList.remove('table-add-node__message--error');
            state.classList.add('table-add-node__message--hidden');
            return;
        }
        state.textContent = message;
        state.hidden = false;
        state.classList.remove('table-add-node__message--hidden');
        state.classList.toggle('table-add-node__message--error', isError);
    }

    function closeAddNodeMenu() {
        if (!activeAddNode) return;
        const menu = getAddNodeMenu(activeAddNode);
        menu?.setAttribute('hidden', '');
        activeAddNode.setAttribute('data-mode', 'closed');
        activeAddNode
            .querySelector(`[${ATTR_ADD_NODE_HANDLE}]`)
            ?.setAttribute('aria-expanded', 'false');
        setAddNodeMessage(activeAddNode, '');
        activeAddNode = null;
    }

    function tableHasActiveSort() {
        return Boolean(
            document.querySelector('.content-view-table thead th[data-sort]')
        );
    }

    function tableHasHiddenRowTypes() {
        return Array.from(
            document.querySelectorAll(
                '.content-view-table tbody tr[data-row-type]'
            )
        ).some(row => row.style.display === 'none');
    }

    function getAddNodeBlockers() {
        const blockers = [];
        if (tableHasActiveSort()) {
            blockers.push({
                type: 'sorting',
                message: 'Reset column sorting before adding nodes in Table view.',
                buttonLabel: 'Reset sorting',
            });
        }
        if (tableHasHiddenRowTypes()) {
            blockers.push({
                type: 'rows',
                message: 'Show all node types before adding nodes in Table view.',
                buttonLabel: 'Show all nodes',
            });
        }
        return blockers;
    }

    function renderAddNodeBlockedState(addNode) {
        const blockers = getAddNodeBlockers();
        const blockersContainer = getAddNodeBlockersContainer(addNode);
        const actions = getAddNodeActions(addNode);
        if (!blockersContainer || !actions) return blockers;

        blockersContainer.replaceChildren();
        blockers.forEach(blocker => {
            const row = document.createElement('div');
            row.className = 'table-add-node__blocker';

            const message = document.createElement('p');
            message.className = 'table-add-node__message';
            message.textContent = blocker.message;

            const button = document.createElement('button');
            button.className = 'table-add-node__unblock-button action_button compact';
            button.type = 'button';
            button.textContent = blocker.buttonLabel;
            button.setAttribute(ATTR_ADD_NODE_UNBLOCK, '');
            button.dataset.blocker = blocker.type;
            button.dataset.testid = `table-add-node-unblock-${blocker.type}`;

            row.append(message, button);
            blockersContainer.append(row);
        });

        const blocked = blockers.length > 0;
        blockersContainer.hidden = !blocked;
        actions.hidden = blocked;
        return blockers;
    }

    function getAddNodeBlockedReason() {
        return getAddNodeBlockers().map(blocker => blocker.message).join(' ');
    }

    function openAddNodeMenu(addNode) {
        if (activeAddNode === addNode) {
            closeAddNodeMenu();
            return;
        }
        closeAddNodeMenu();
        activeAddNode = addNode;
        activeAddNode.setAttribute('data-mode', 'open');
        activeAddNode
            .querySelector(`[${ATTR_ADD_NODE_HANDLE}]`)
            ?.setAttribute('aria-expanded', 'true');
        getAddNodeMenu(activeAddNode)?.removeAttribute('hidden');
        setAddNodeMessage(activeAddNode, '');
        renderAddNodeBlockedState(activeAddNode);
    }

    function clearCreatedRowMarker() {
        document
            .querySelectorAll('tr[data-node-created="true"]')
            .forEach(row => row.removeAttribute('data-node-created'));
    }

    function positionCreatedNodeFromFeedback(anchor) {
        const feedback = getAddNodeFeedback();
        const createdNodeMid = feedback?.dataset.createdNodeMid;
        if (!createdNodeMid) return;

        clearCreatedRowMarker();

        const row = document.querySelector(
            `tr[data-node-mid="${createdNodeMid}"]`
        );
        if (!row) return;
        row.setAttribute('data-node-created', 'true');
        restoreViewportAnchor(anchor, row);
        feedback.dataset.createdNodeMid = '';
    }

    function handleBeforeTableStateChange(event) {
        const changeType = event.detail?.changeType;
        if (activeAddNode) {
            pendingTableStateAnchor = captureViewportAnchor(
                getAddNodeMenu(activeAddNode)
            );
            return;
        }
        if (changeType !== 'sorting') {
            pendingTableStateAnchor = null;
            return;
        }
        const activeCell = activeInlineCell || activeAutocompleteCell;
        pendingTableStateAnchor = captureViewportAnchor(
            activeCell?.closest('tr[data-row-type]')
        );
    }

    function handleAfterTableStateChange() {
        const anchor = pendingTableStateAnchor;
        pendingTableStateAnchor = null;
        if (activeAddNode) {
            renderAddNodeBlockedState(activeAddNode);
        }
        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                restoreViewportAnchor(anchor);
            });
        });
    }

    // Restores cell DOM to its pre-edit state. Call after nulling the active variable.
    function restoreInlineCellDOM(cell) {
        const state = getCellState(cell);
        updateMode(cell);
        cell.removeAttribute('data-validation-error');
        clearFieldErrors(cell);
        if (state.originalHTML !== undefined) {
            cell.innerHTML = state.originalHTML;
            state.originalHTML = undefined;
        }
        state.originalFormData = undefined;
    }

    // Saves original HTML, marks cell as editing, and fetches the inline form.
    function initInlineCellState(cell) {
        const state = getCellState(cell);
        state.originalHTML = cell.innerHTML;
        state.originalFormData = undefined;
        cell.removeAttribute('data-validation-error');
        updateMode(cell, 'editing');
        fetchTurboStream(cell.dataset.url, cell);
    }

    async function runCellSave(cell, saveOperation) {
        const state = getCellState(cell);
        if (state.savePromise) {
            // Blur, outside-click, and keyboard handlers may request the same
            // logical save. Reuse the in-flight request for this cell only.
            return state.savePromise;
        }

        state.savePromise = saveOperation();
        try {
            return await state.savePromise;
        } finally {
            state.savePromise = null;
        }
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
        cancelAutocompleteBlurSave(cell);
        restoreInlineCellDOM(cell);
    }

    function cancelAutocompleteBlurSave(cell) {
        const state = getCellState(cell);
        if (state.autocompleteBlurTimer !== null) {
            clearTimeout(state.autocompleteBlurTimer);
            state.autocompleteBlurTimer = null;
        }
    }

    function scheduleAutocompleteBlurSave(cell, autocompleteInput) {
        const state = getCellState(cell);
        cancelAutocompleteBlurSave(cell);
        state.autocompleteBlurTimer = setTimeout(function () {
            state.autocompleteBlurTimer = null;
            // Selecting a dropdown option may return focus to the control.
            // An outside click saves immediately and clears the active cell,
            // so the delayed blur handler must not submit it again.
            if (
                activeAutocompleteCell !== cell ||
                autocompleteInput === document.activeElement ||
                autocompleteInput.contains(document.activeElement)
            ) {
                return;
            }
            saveAutocompleteCell(cell, autocompleteInput);
        }, 200);
    }

    function saveAutocompleteCell(cell, autocompleteInput) {
        if (!cell || !autocompleteInput) return Promise.resolve();
        cancelAutocompleteBlurSave(cell);
        return runCellSave(
            cell,
            () => performAutocompleteCellSave(cell, autocompleteInput)
        );
    }

    async function performAutocompleteCellSave(cell, autocompleteInput) {
        const state = getCellState(cell);
        const hiddenInput = autocompleteInput.nextElementSibling;
        const rawValue = hiddenInput
            ? hiddenInput.value
            : autocompleteInput.innerText;
        const newValue = rawValue.trim().replace(/,\s*$/, '').trim();
        const originalValue = (cell.dataset.currentValue || '').trim();

        if (activeAutocompleteCell === cell) {
            activeAutocompleteCell = null;
            cell.removeAttribute('data-mode');
        }

        if (newValue === originalValue) {
            if (state.originalHTML !== undefined) {
                cell.innerHTML = state.originalHTML;
                state.originalHTML = undefined;
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

        if (!ok && state.originalHTML !== undefined) {
            cell.innerHTML = state.originalHTML;
        }
        state.originalHTML = undefined;
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
                        const state = getCellState(cell);
                        state.originalFormData = new URLSearchParams(
                            new FormData(form)
                        ).toString();
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
        customMetaDragState.armedRow = null;
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

    function saveInlineCell(cell) {
        if (!cell) return Promise.resolve();
        return runCellSave(cell, () => performInlineCellSave(cell));
    }

    async function performInlineCellSave(cell) {
        const state = getCellState(cell);

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
            state.originalFormData !== undefined &&
            currentData === state.originalFormData
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
        const activeFieldName = cell.querySelector(
            'input[name="active_field_name"]'
        )?.value;
        if (activeFieldName !== undefined) {
            formData.set('active_field_name', activeFieldName);
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
                cell.removeAttribute('data-validation-error');
                state.originalHTML = undefined;
                state.originalFormData = undefined;
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
                        errorEl.setAttribute(
                            'data-testid',
                            'table-inline-field-error'
                        );
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

    // --- Event handlers ---

    function handleEditModeToggle() {
        setEditMode(!editMode);
    }

    function handleMainClick(event) {
        if (!editMode) return;

        const addNodeHandle = event.target.closest(`[${ATTR_ADD_NODE_HANDLE}]`);
        if (addNodeHandle) {
            event.preventDefault();
            openAddNodeMenu(addNodeHandle.closest(`[${ATTR_ADD_NODE}]`));
            return;
        }

        const addNodeAction = event.target.closest(`[${ATTR_ADD_NODE_ACTION}]`);
        if (addNodeAction) {
            event.preventDefault();
            if (addNodeAction.disabled) {
                setAddNodeMessage(
                    addNodeAction.closest(`[${ATTR_ADD_NODE}]`),
                    addNodeAction.dataset.disabledReason || 'This action is disabled.'
                );
                return;
            }
            createTableNode(addNodeAction);
            return;
        }

        const addNodeUnblock = event.target.closest(
            `[${ATTR_ADD_NODE_UNBLOCK}]`
        );
        if (addNodeUnblock) {
            event.preventDefault();
            const resetSelector = addNodeUnblock.dataset.blocker === 'sorting'
                ? '[data-testid="table-toolbar-sort-reset"]'
                : '[data-testid="table-toolbar-rows-reset"]';
            addNodeUnblockInProgress = true;
            try {
                document.querySelector(resetSelector)?.click();
            } finally {
                addNodeUnblockInProgress = false;
            }
            renderAddNodeBlockedState(
                addNodeUnblock.closest(`[${ATTR_ADD_NODE}]`)
            );
            return;
        }

        const customMetaDeleteAction = event.target.closest(
            `[${ATTR_CUSTOM_META_DELETE_ACTION}]`
        );
        if (customMetaDeleteAction) {
            event.preventDefault();
            deleteCustomMetaRow(customMetaDeleteAction);
            return;
        }

        const customMetaDragHandle = event.target.closest(
            `[${ATTR_CUSTOM_META_DRAG_HANDLE}]`
        );
        if (customMetaDragHandle) {
            event.preventDefault();
            return;
        }

        // Add a comment or relation row without following the link.
        const addFieldLink = event.target.closest(`[${ATTR_ADD_FIELD}]`);
        if (addFieldLink) {
            event.preventDefault();
            fetchTurboStream(addFieldLink.href);
            return;
        }

        const editableField = event.target.closest(`[${ATTR_FIELD}]`);
        if (!editableField) return;

        const fieldType = editableField.getAttribute(ATTR_FIELD);
        if (fieldType === FIELD_AUTOCOMPLETE) {
            event.preventDefault();
            openAutocompleteCell(editableField);
            return;
        }
        if (INLINE_FIELD_TYPES.has(fieldType)) {
            event.preventDefault();
            openInlineCell(editableField);
        }
    }

    async function createTableNode(actionButton) {
        const addNode = actionButton.closest(`[${ATTR_ADD_NODE}]`);
        const blockedReason = getAddNodeBlockedReason();
        if (blockedReason) {
            setAddNodeMessage(addNode, blockedReason, true);
            return;
        }
        if (addNode?.dataset.pending === 'true') {
            return;
        }

        addNode.dataset.pending = 'true';
        setAddNodeMessage(addNode, '');
        addNode
            .querySelectorAll(`[${ATTR_ADD_NODE_ACTION}]`)
            .forEach(button => button.setAttribute('disabled', 'disabled'));

        const formData = new FormData();
        formData.append(
            'context_document_mid',
            actionButton.dataset.contextDocumentMid
        );
        formData.append('reference_mid', actionButton.dataset.referenceMid);
        formData.append('element_type', actionButton.dataset.elementType);
        formData.append('whereto', actionButton.dataset.whereto);

        const feedback = getAddNodeFeedback();
        if (feedback) {
            feedback.dataset.createdNodeMid = '';
        }
        const creationAnchor = captureViewportAnchor(
            getAddNodeMenu(addNode),
            true
        );
        try {
            const response = await fetch('/actions/table/add_node', {
                method: 'POST',
                headers: { Accept: TURBO_ACCEPT },
                body: formData,
            });
            const html = await response.text();
            if (response.ok) {
                renderTurboStream(html);
                closeAddNodeMenu();
                requestAnimationFrame(() => {
                    requestAnimationFrame(() => {
                        positionCreatedNodeFromFeedback(creationAnchor);
                    });
                });
                return;
            }
            console.error('Table add-node failed:', html);
            setAddNodeMessage(
                addNode,
                'Unable to create this node.',
                true
            );
        } catch (error) {
            console.error('Table add-node error:', error);
            setAddNodeMessage(
                addNode,
                'Unable to create this node.',
                true
            );
        } finally {
            addNode?.removeAttribute('data-pending');
            addNode
                ?.querySelectorAll(`[${ATTR_ADD_NODE_ACTION}]`)
                .forEach(button => {
                    if (button.dataset.disabledReason) {
                        button.setAttribute('disabled', 'disabled');
                    } else {
                        button.removeAttribute('disabled');
                    }
                });
        }
    }

    function handleCustomMetaDragStart(event) {
        if (!editMode || customMetaReorderPending) {
            event.preventDefault();
            return;
        }
        const row = customMetaDragState.armedRow;
        if (!row || !row.contains(event.target)) {
            event.preventDefault();
            return;
        }

        if (activeInlineCell) cancelInlineCell();
        if (activeAutocompleteCell) cancelAutocompleteCell();

        customMetaDragState.row = row;
        customMetaDragState.originalNextSibling = row.nextSibling;
        row.setAttribute('data-dragging', 'true');
        event.dataTransfer.effectAllowed = 'move';
        event.dataTransfer.setData('text/plain', row.dataset.formKey);
    }

    function handleCustomMetaPointerDown(event) {
        if (!editMode || customMetaReorderPending) return;
        const dragHandle = event.target.closest(
            `[${ATTR_CUSTOM_META_DRAG_HANDLE}]`
        );
        const row = dragHandle?.closest(`[${ATTR_CUSTOM_META_ROW}]`);
        if (!row) return;

        customMetaDragState.armedRow = row;
    }

    function handleCustomMetaPointerUp() {
        if (customMetaDragState.row) return;
        customMetaDragState.armedRow = null;
    }

    function handleCustomMetaDragOver(event) {
        const draggedRow = customMetaDragState.row;
        const targetRow = event.target.closest(`[${ATTR_CUSTOM_META_ROW}]`);
        if (!draggedRow || !targetRow || draggedRow === targetRow) {
            setCustomMetaDropTarget(null, null);
            return;
        }

        event.preventDefault();
        event.dataTransfer.dropEffect = 'move';
        const targetBounds = targetRow.getBoundingClientRect();
        const position =
            event.clientY < targetBounds.top + targetBounds.height / 2
                ? 'before'
                : 'after';
        setCustomMetaDropTarget(targetRow, position);
    }

    function handleCustomMetaDrop(event) {
        const row = customMetaDragState.row;
        const targetRow = customMetaDragState.targetRow;
        const position = customMetaDragState.position;
        const originalNextSibling = customMetaDragState.originalNextSibling;
        if (!row || !targetRow || !position) {
            clearCustomMetaDragState();
            return;
        }

        event.preventDefault();
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
    }

    function handleAutocompleteBlur(event) {
        if (!editMode) return;
        const cell = event.target.closest(
            `[${ATTR_FIELD}="${FIELD_AUTOCOMPLETE}"]`
        );
        if (!cell) return;
        const autocompleteInput = getAutocompleteInput(cell);
        if (
            !autocompleteInput ||
            !autocompleteInput.contains(event.target)
        ) {
            return;
        }
        scheduleAutocompleteBlurSave(cell, autocompleteInput);
    }

    function handleDocumentKeydown(event) {
        const addNodeHandle = event.target.closest?.(
            `[${ATTR_ADD_NODE_HANDLE}]`
        );
        if (
            editMode &&
            addNodeHandle &&
            (event.key === 'Enter' || event.key === ' ')
        ) {
            event.preventDefault();
            openAddNodeMenu(addNodeHandle.closest(`[${ATTR_ADD_NODE}]`));
            return;
        }
        if (event.key === 'Escape') {
            if (activeAddNode) {
                event.preventDefault();
                closeAddNodeMenu();
            }
            if (activeInlineCell) {
                event.preventDefault();
                cancelInlineCell();
            }
            if (activeAutocompleteCell) {
                event.preventDefault();
                cancelAutocompleteCell();
            }
            return;
        }
        if (
            (event.metaKey || event.ctrlKey) &&
            event.key === 'Enter' &&
            activeInlineCell
        ) {
            const fieldType = activeInlineCell.getAttribute(ATTR_FIELD);
            if (
                fieldType === FIELD_CONTENTEDITABLE ||
                fieldType === FIELD_COMMENTS
            ) {
                event.preventDefault();
                saveInlineCell(activeInlineCell);
            }
        }
    }

    function handleDocumentClick(event) {
        const eventPath = event.composedPath();
        const tableToolbar = event.target.closest?.(
            '[data-testid="table-toolbar"]'
        );
        if (
            activeAddNode &&
            !addNodeUnblockInProgress &&
            !tableToolbar &&
            !eventPath.includes(activeAddNode)
        ) {
            closeAddNodeMenu();
        }
        if (activeInlineCell && !eventPath.includes(activeInlineCell)) {
            saveInlineCell(activeInlineCell);
        }
        if (
            activeAutocompleteCell &&
            !eventPath.includes(activeAutocompleteCell)
        ) {
            saveAutocompleteCell(
                activeAutocompleteCell,
                getAutocompleteInput(activeAutocompleteCell)
            );
        }
    }

    function init() {
        const editButton = getHandler();
        if (!editButton) return;

        editButton.addEventListener('click', handleEditModeToggle);

        const main = getMainContainer();
        if (!main) return;

        // One delegated click handler for all editable fields in the main table view:
        // both regular table cells and document-level fields above the table.
        main.addEventListener('click', handleMainClick);
        main.addEventListener('dragstart', handleCustomMetaDragStart);
        main.addEventListener('pointerdown', handleCustomMetaPointerDown);
        main.addEventListener('pointerup', handleCustomMetaPointerUp);
        main.addEventListener('dragover', handleCustomMetaDragOver);
        main.addEventListener('drop', handleCustomMetaDrop);
        main.addEventListener('dragend', clearCustomMetaDragState);

        // Save autocomplete cell on blur (Stimulus handles the dropdown interaction).
        // Uses capture phase to catch blur events from contenteditable sdoc-autocompletable.
        main.addEventListener('blur', handleAutocompleteBlur, true);

        document.addEventListener('keydown', handleDocumentKeydown);
        document.addEventListener('click', handleDocumentClick);
        document.addEventListener(
            EVENT_BEFORE_TABLE_STATE_CHANGE,
            handleBeforeTableStateChange
        );
        document.addEventListener(
            EVENT_AFTER_TABLE_STATE_CHANGE,
            handleAfterTableStateChange
        );
    }

    window.addEventListener('load', init);
})();
