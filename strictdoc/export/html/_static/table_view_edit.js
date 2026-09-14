(function () {
    // This file controls table editing from opening a cell through applying the
    // server response. Network responses can arrive after the user cancels,
    // reopens, or changes a cell. Each response is checked against the current
    // cell interaction before the response can change the DOM. Turbo Stream
    // actions are then applied without an animation-frame delay, so the user
    // cannot change the cell between that check and the DOM update.

    // --- Request settings and DOM contracts ---

    // Used in the Accept header to tell the server to return a Turbo Stream
    // response instead of a full HTML page.
    const TURBO_ACCEPT = 'text/vnd.turbo-stream.html';
    // Delay before an autocomplete blur triggers a save, giving a dropdown
    // selection time to update the value before the blur handler checks focus.
    // Without this delay, blur could save the old value before the option click
    // is processed.
    const AUTOCOMPLETE_BLUR_SAVE_DELAY_MS = 200;

    // Shared table-editing DOM contract:
    // - js-table_view_edit marks the stable container that receives delegated
    // events from controls replaced by Turbo Streams.
    // - js-table_view_edit-table marks the table whose editable mode is toggled.
    // - js-table_view_edit-toggle marks the button that enables editing.
    const ATTR_CONTAINER = 'js-table_view_edit';
    const ATTR_TABLE = 'js-table_view_edit-table';
    const ATTR_TOGGLE = 'js-table_view_edit-toggle';

    // Inline-editing DOM contract:
    // - js-table_view_edit-field marks each editable field. Its value selects
    // the handling path: "autocomplete", "contenteditable", "comments",
    // or "relations".
    // - js-table_view_edit-add-field marks links that add comment or relation
    // rows into an open inline form.
    // - js-table_view_edit-form marks the form submitted for a field. The
    // form may be nested inside that field or wrap several fields, as in the
    // document custom-metadata editor.
    // - js-table_view_edit-submit-unchanged marks creation fields whose initial
    // empty form state must still be submitted so backend validation can run.
    const ATTR_FIELD = 'js-table_view_edit-field';
    const ATTR_ADD_FIELD = 'js-table_view_edit-add-field';
    const ATTR_FORM = 'js-table_view_edit-form';
    const ATTR_SUBMIT_UNCHANGED = 'js-table_view_edit-submit-unchanged';

    // Add-node DOM contract:
    // - js-table_view_edit-add-node marks the complete control.
    // - js-table_view_edit-add-node-handle opens its menu.
    // - js-table_view_edit-add-node-menu marks the menu element.
    // - js-table_view_edit-add-node-action marks each node creation button.
    // - js-table_view_edit-add-node-actions groups the creation buttons.
    // - js-table_view_edit-add-node-blockers displays reasons why node creation
    // is unavailable.
    // - js-table_view_edit-add-node-state displays a status or error message.
    // - js-table_view_edit-add-node-unblock marks buttons that remove a blocker.
    const ATTR_ADD_NODE = 'js-table_view_edit-add-node';
    const ATTR_ADD_NODE_HANDLE = 'js-table_view_edit-add-node-handle';
    const ATTR_ADD_NODE_MENU = 'js-table_view_edit-add-node-menu';
    const ATTR_ADD_NODE_ACTION = 'js-table_view_edit-add-node-action';
    const ATTR_ADD_NODE_ACTIONS = 'js-table_view_edit-add-node-actions';
    const ATTR_ADD_NODE_BLOCKERS = 'js-table_view_edit-add-node-blockers';
    const ATTR_ADD_NODE_STATE = 'js-table_view_edit-add-node-state';
    const ATTR_ADD_NODE_UNBLOCK = 'js-table_view_edit-add-node-unblock';
    const ADD_NODE_FEEDBACK_ID = 'table-add-node-feedback';
    const ADD_NODE_CREATE_ERROR = 'Unable to create this node.';

    // Sorting and row filtering dispatch these events around their DOM changes.
    // Editing controls use them to preserve the viewport position.
    const EVENT_BEFORE_TABLE_STATE_CHANGE = 'strictdoc:table-view-before-state-change';
    const EVENT_AFTER_TABLE_STATE_CHANGE = 'strictdoc:table-view-after-state-change';

    // Custom-metadata DOM contract:
    // - js-table_view_edit-custom_meta-error associates a validation error with
    // one metadata row.
    // - js-table_view_edit-custom_meta-row marks one metadata row.
    // - js-table_view_edit-custom_meta-delete_action marks the delete button
    // inside a metadata row.
    // - js-table_view_edit-custom_meta-drag_handle starts row reordering.
    const ATTR_CUSTOM_META_ERROR = 'js-table_view_edit-custom_meta-error';
    const ATTR_CUSTOM_META_ROW = 'js-table_view_edit-custom_meta-row';
    const ATTR_CUSTOM_META_DELETE_ACTION = 'js-table_view_edit-custom_meta-delete_action';
    const ATTR_CUSTOM_META_DRAG_HANDLE = 'js-table_view_edit-custom_meta-drag_handle';

    const FIELD_AUTOCOMPLETE = 'autocomplete';
    const FIELD_CONTENTEDITABLE = 'contenteditable';
    const FIELD_COMMENTS = 'comments';
    const FIELD_RELATIONS = 'relations';
    const INLINE_FIELD_TYPES = new Set([
        FIELD_CONTENTEDITABLE,
        FIELD_COMMENTS,
        FIELD_RELATIONS,
    ]);

    // --- Runtime state ---

    // Save-response states used to decide whether to close the editor, preserve
    // newer user input, or ignore an error from an older editing session.
    const SAVE_SESSION_CURRENT = 'current';
    const SAVE_SESSION_REACTIVATED = 'reactivated';
    const SAVE_SESSION_CLOSED = 'closed';

    // Whether table editing controls are enabled.
    let editMode = false;

    // The cell DOM element containing the active inline form.
    let activeInlineFormCell = null;
    // The cell DOM element containing the active autocomplete editor.
    let activeAutocompleteCell = null;

    // The add-node container element whose menu is currently open.
    let activeAddNodeContainerElement = null;

    // Keep the add-node menu open while the result of a table toolbar action
    // (for example, reset sorting or reset row visibility)
    // is rendered and updates the DOM.
    let shouldKeepAddNodeMenuOpen = false;

    // The element and viewport coordinates captured before sorting or row
    // filtering changes the table. They are used to restore the same visible
    // position after the table is updated.
    let pendingTableStateAnchor = null;

    // The cell DOM element clicked while another inline form is active. Open it
    // only after the currently edited cell saves successfully.
    let pendingInlineFormCell = null;

    // Prevents another metadata drag operation while the current order is saving.
    let customMetaReorderPending = false;

    // Stores the metadata drag operation from pointer-down until drop or cancel.
    const customMetaDragState = {
        // The row DOM element whose drag handle was pressed.
        armedRow: null,
        // The row DOM element currently being dragged.
        row: null,
        // Its original next sibling, used to restore the row if saving fails.
        originalNextSibling: null,
        // The row DOM element currently selected as the drop target.
        targetRow: null,
        // Whether the dragged row will be inserted before or after the target.
        position: null,
    };

    // --- Form data and cell state ---

    // Stores the internal editing state for each cell. This state remains
    // available when the content inside the cell is replaced to show or hide
    // an editor.
    const cellStates = new WeakMap();

    // Normalize form data so opening and cancelling an editor does not create
    // false field differences. When the browser opens an editor, it can change
    // textarea line endings from CRLF to LF even when the user does not edit
    // the text. Without normalization, the comparison treats the unchanged
    // text as a user edit. URLSearchParams normalizes both form snapshots to
    // LF, matching the values that Turbo sends to the server.
    function createFormData(form) {
        return new URLSearchParams(new FormData(form));
    }

    // All custom metadata rows are submitted together in one HTML form. The server
    // rebuilds and saves the complete custom metadata list from that submission.
    // Therefore, every save request includes every row, even when the user changes
    // only one cell.
    //
    // Two hidden inputs identify the cell that started the save. active_form_key
    // identifies the metadata row. active_field_name identifies the name or
    // value field in that row. The server uses these values to return an updated
    // value or validation errors for that cell.
    //
    // When validation fails, the editable controls remain in the cell so the user
    // can correct the value later. The user can then open a different metadata
    // cell. Both cells belong to the same form, so the form contains
    // active_form_key and active_field_name inputs from both cells.
    //
    // Before sending the form, read active_form_key and active_field_name from the
    // cell being saved. URLSearchParams.set removes all other values with those
    // names and keeps only the values from that cell. The values of all metadata
    // rows remain unchanged. The server can then save the complete metadata list
    // and return a Turbo Stream that updates the correct cell.
    function buildCellSaveFormData(cell, form) {
        const formData = createFormData(form);
        const activeFormKey = cell.querySelector(
            'input[name="active_form_key"]'
        )?.value;
        if (activeFormKey !== undefined) {
            formData.set('active_form_key', activeFormKey);
        }
        const activeFieldName = cell.querySelector(
            'input[name="active_field_name"]'
        )?.value;
        if (activeFieldName !== undefined) {
            formData.set('active_field_name', activeFieldName);
        }
        return formData;
    }

    // A queued save must determine whether this cell changed while another save
    // was running. Serialize only inputs inside this cell. Serializing the whole
    // custom-metadata form would include edits from other rows and could cause
    // this cell to be submitted again even though its value did not change.
    function serializeCellFields(cell) {
        const serializedFields = new URLSearchParams();
        cell
            .querySelectorAll('input[name], textarea[name], select[name]')
            .forEach(field => {
                serializedFields.append(field.name, field.value);
            });
        return serializedFields.toString();
    }

    function getCellState(cell) {
        let state = cellStates.get(cell);
        if (!state) {
            state = {
                // Cell content used when an editor closes without a current
                // successful save. It starts with the displayed value and is
                // updated when an older pending save succeeds.
                displayHTML: undefined,
                // Form data received with the editor. An identical form does
                // not need a save request.
                loadedFormData: undefined,
                // Several event handlers can request a save for the same cell.
                // This promise allows only one request to run at a time. Later
                // save attempts wait for it instead of sending a duplicate.
                activeSavePromise: null,
                // Input values sent by the active save. After waiting, another
                // save compares the current values with this snapshot. It sends
                // another request only when the user entered a correction.
                submittedCellData: undefined,
                // Delayed blur save used by autocomplete dropdown interaction.
                autocompleteBlurTimer: null,
                // Incremented when loading an editor starts. The request keeps
                // this number and may update the cell only if it still matches
                // and the user has not closed the opening.
                editorOpeningNumber: 0,
                // Incremented when the user starts or resumes editing. A save
                // keeps this number to detect interaction that happened while
                // its response was pending.
                userInteractionNumber: 0,
            };
            cellStates.set(cell, state);
        }
        return state;
    }

    function isCellActive(cell) {
        return (
            activeInlineFormCell === cell
            || activeAutocompleteCell === cell
        );
    }

    // A save response may arrive after the user continues working with the
    // cell. Compare the interaction number recorded by the request with the
    // current interaction number before the response changes the DOM. Also
    // check whether the cell is still active.
    //
    // The response is current when the cell is active and its interaction
    // number has not changed. A successful response can close the input and
    // show the saved value. An error still describes the visible input and can
    // be shown there.
    //
    // The response is reactivated when the cell is active but its interaction
    // number has changed. The server processed an older value while the user
    // continued editing. Keep the current input visible. A successful response
    // updates only the display value restored by Escape. An error is ignored
    // because the error does not describe the current input.
    //
    // The response is closed when the cell is no longer active. A successful
    // response still updates the displayed value because the server saved it.
    // An error must not reopen or modify a cell that the user already closed.
    function classifySaveSession(cell, savedUserInteractionNumber) {
        const newerInteractionStarted =
            getCellState(cell).userInteractionNumber
            !== savedUserInteractionNumber;
        if (newerInteractionStarted && isCellActive(cell)) {
            return SAVE_SESSION_REACTIVATED;
        }
        if (!newerInteractionStarted && isCellActive(cell)) {
            return SAVE_SESSION_CURRENT;
        }
        return SAVE_SESSION_CLOSED;
    }

    // --- DOM helpers ---

    function getMainContainer() {
        return document.querySelector(`[${ATTR_CONTAINER}]`);
    }

    function getTable() {
        return document.querySelector(`[${ATTR_TABLE}]`);
    }

    function getEditModeButton() {
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
        // Custom metadata errors are placed as siblings after the field element
        // (via Turbo action="after"), not inside it. Match them by the row's
        // form-key attribute so only this row's errors are removed, not those
        // of other rows in the shared form.
        const customMetaRow = field.closest(`[${ATTR_CUSTOM_META_ROW}]`);
        if (customMetaRow) {
            const formKey = customMetaRow.dataset.formKey;
            if (formKey) {
                customMetaRow
                    .querySelectorAll(
                        `[${ATTR_CUSTOM_META_ERROR}="${formKey}"]`
                    )
                    .forEach(errorElement => errorElement.remove());
                return;
            }
        }
        field
            .querySelectorAll('sdoc-form-error')
            .forEach(errorElement => errorElement.remove());
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
        const editModeButton = getEditModeButton();
        if (on) {
            updateMode(main, 'edit');
            updateMode(table, 'editable');
            updateButtonState(editModeButton, true);
        } else {
            updateMode(main);
            updateMode(table);
            updateButtonState(editModeButton);
            pendingInlineFormCell = null;
            closeAddNodeMenu();
            cancelActiveCells();
            // Validation errors leave inactive editors open for correction.
            // Disabling edit mode restores every cell to display mode.
            document
                .querySelectorAll(`[${ATTR_FIELD}][data-mode="editing"]`)
                .forEach(cell => restoreCellDisplay(cell));
        }
    }

    // --- Table response handling ---

    // The response functions in this section keep the state check and the DOM
    // update in one browser task. This closes the animation-frame gap in which
    // a user action could make an already checked response obsolete.

    // Turbo normally waits for an animation frame before changing the DOM.
    // Table editing cannot use that delay: a click or Escape in that frame can
    // make the response stale. Apply its stream actions now, in the same task
    // that checked the editing state.
    function applyTableStream(html) {
        const streamMessage = document.createElement('template');
        streamMessage.innerHTML = html;
        streamMessage.content.querySelectorAll('turbo-stream').forEach(stream => {
            const streamTemplate = stream.querySelector('template');
            if (!streamTemplate) return;

            const targetId = stream.getAttribute('target');
            const targetsSelector = stream.getAttribute('targets');
            const targets = targetId
                ? [document.getElementById(targetId)].filter(Boolean)
                : targetsSelector
                    ? Array.from(document.querySelectorAll(targetsSelector))
                    : [];
            applyTableStreamAction(stream, streamTemplate, targets);
        });
    }

    // These are the standard Turbo Stream DOM actions used by StrictDoc.
    // Keeping them synchronous is the central protection against a user action
    // invalidating a response between its state check and its DOM update.
    function applyTableStreamAction(stream, streamTemplate, targets) {
        const action = stream.getAttribute('action');
        if (action === 'append' || action === 'prepend') {
            const newIds = new Set(
                Array.from(streamTemplate.content.children)
                    .map(element => element.id)
                    .filter(Boolean)
            );
            targets.forEach(target => {
                Array.from(target.children).forEach(child => {
                    if (newIds.has(child.id)) child.remove();
                });
            });
        }

        targets.forEach(target => {
            const content = streamTemplate.content.cloneNode(true);
            switch (action) {
                case 'after':
                    target.after(content);
                    break;
                case 'append':
                    target.append(content);
                    break;
                case 'before':
                    target.before(content);
                    break;
                case 'prepend':
                    target.prepend(content);
                    break;
                case 'remove':
                    target.remove();
                    break;
                case 'replace':
                    target.replaceWith(content);
                    break;
                case 'update':
                    target.replaceChildren(content);
                    break;
                default:
                    throw new Error(
                        `Unsupported table Turbo Stream action: ${action}`
                    );
            }
        });
    }

    // A successful response from an older session contains a value accepted by
    // the server. Apply its cell update to a clone instead of the live editor.
    // The clone becomes the display markup restored by Escape. Other targets,
    // such as the table of contents, are updated in the live document.
    function applySuccessfulSaveToReactivatedCell(html, cell) {
        const streamMessage = document.createElement('template');
        streamMessage.innerHTML = html;
        const confirmedCell = cell.cloneNode(true);
        let cellWasUpdated = false;

        streamMessage.content.querySelectorAll('turbo-stream').forEach(stream => {
            const targetId = stream.getAttribute('target');
            const liveTarget = targetId ? document.getElementById(targetId) : null;
            if (
                stream.getAttribute('action') !== 'update'
                || !liveTarget
                || (liveTarget !== cell && !cell.contains(liveTarget))
            ) {
                return;
            }
            const confirmedTarget = targetId === cell.id
                ? confirmedCell
                : confirmedCell.querySelector(`#${CSS.escape(targetId)}`);
            const streamTemplate = stream.querySelector('template');
            if (!confirmedTarget || !streamTemplate) {
                return;
            }
            applyTableStreamAction(stream, streamTemplate, [confirmedTarget]);
            cellWasUpdated = true;
            stream.remove();
        });

        if (cellWasUpdated) {
            getCellState(cell).displayHTML = confirmedCell.innerHTML;
        }
        if (streamMessage.innerHTML.trim()) {
            applyTableStream(streamMessage.innerHTML);
        }
    }

    // Submit a table-edit form and read its Turbo Stream response.
    async function postTurboStream(url, body) {
        const response = await fetch(url, {
            method: 'POST',
            headers: { Accept: TURBO_ACCEPT },
            body,
        });
        const html = await response.text();
        return { response, html };
    }

    // Fetch a Turbo Stream whose response is not tied to a cell opening or
    // save. Comment and relation forms use this path to add another row.
    async function fetchAndApplyTurboStream(url) {
        try {
            const response = await fetch(url, {
                headers: { Accept: TURBO_ACCEPT },
            });
            const html = await response.text();
            if (response.ok) {
                applyTableStream(html);
            } else {
                console.error('Table stream fetch failed:', html);
            }
        } catch (error) {
            console.error('Table stream fetch error:', error);
        }
    }

    // --- Add-node menu and viewport ---

    // Adding a node can change row order and table height. The functions in
    // this section keep the active menu visible, explain why an action is
    // blocked, and preserve the user's viewport while the table changes.

    // Wait for the DOM update to be laid out and painted before measuring or
    // restoring its viewport position. The second frame runs after the browser
    // has had an opportunity to paint the first frame.
    function afterNextRepaint(callback) {
        requestAnimationFrame(() => requestAnimationFrame(callback));
    }

    function getAddNodeFeedback() {
        return document.getElementById(ADD_NODE_FEEDBACK_ID);
    }

    function getAddNodeMenu(addNode) {
        return addNode?.querySelector(`[${ATTR_ADD_NODE_MENU}]`);
    }

    function getAddNodeState(addNode) {
        return addNode?.querySelector(`[${ATTR_ADD_NODE_STATE}]`);
    }

    function getAddNodeActions(addNode) {
        return addNode?.querySelector(`[${ATTR_ADD_NODE_ACTIONS}]`);
    }

    function getAddNodeBlockersContainer(addNode) {
        return addNode?.querySelector(`[${ATTR_ADD_NODE_BLOCKERS}]`);
    }

    function setAddNodeExpanded(addNode, expanded) {
        addNode
            ?.querySelector(`[${ATTR_ADD_NODE_HANDLE}]`)
            ?.setAttribute('aria-expanded', expanded ? 'true' : 'false');
    }

    // A create request temporarily disables every add-node action. Enable them
    // again when the request finishes, except for actions that were already
    // disabled by a document rule.
    function restoreAddNodeActionButtons(addNode) {
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

    // Keep an element at the same viewport position after table rows move.
    // Horizontal position is restored only for callers that request it.
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
        if (!activeAddNodeContainerElement) return;
        const menu = getAddNodeMenu(activeAddNodeContainerElement);
        menu?.setAttribute('hidden', '');
        activeAddNodeContainerElement.setAttribute('data-mode', 'closed');
        setAddNodeExpanded(activeAddNodeContainerElement, false);
        setAddNodeMessage(activeAddNodeContainerElement, '');
        activeAddNodeContainerElement = null;
    }

    function tableHasActiveSort() {
        return Boolean(
            document.querySelector('.content-view-table thead th[data-sort]')
        );
    }

    function tableHasHiddenRowTypes() {
        const rows = document.querySelectorAll(
            '.content-view-table tbody tr[data-row-type]'
        );
        // Stop as soon as one hidden row is found. Building an array of every
        // row would do unnecessary work on large tables.
        for (const row of rows) {
            if (row.style.display === 'none') return true;
        }
        return false;
    }

    function getAddNodeBlockers() {
        const blockers = [];
        if (tableHasActiveSort()) {
            blockers.push({
                type: 'sorting',
                message: 'Reset column sorting before adding nodes on TABLE screen.',
                buttonLabel: 'Reset sorting',
            });
        }
        if (tableHasHiddenRowTypes()) {
            blockers.push({
                type: 'rows',
                message: 'Show all node types before adding nodes on TABLE screen.',
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
        if (activeAddNodeContainerElement === addNode) {
            closeAddNodeMenu();
            return;
        }
        closeAddNodeMenu();
        activeAddNodeContainerElement = addNode;
        activeAddNodeContainerElement.setAttribute('data-mode', 'open');
        setAddNodeExpanded(activeAddNodeContainerElement, true);
        getAddNodeMenu(activeAddNodeContainerElement)?.removeAttribute('hidden');
        setAddNodeMessage(activeAddNodeContainerElement, '');
        renderAddNodeBlockedState(activeAddNodeContainerElement);
    }

    // Create the selected node and keep the menu unavailable until the server
    // responds. A successful response inserts the row and closes the menu. A
    // failed response keeps the menu open and shows an error, so the user can
    // retry the same action.
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

        // Block repeated clicks while the create request is running. All action
        // buttons share the same menu and must wait for that request.
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
        try {
            const { response, html } = await postTurboStream(
                '/actions/table/add_node',
                formData
            );
            if (response.ok) {
                applyTableStream(html);
                closeAddNodeMenu();
                // The response inserts the new row. Wait until it is painted
                // before finding it and applying the created-row marker.
                afterNextRepaint(positionCreatedNodeFromFeedback);
                return;
            }
            console.error('Table add-node failed:', html);
            setAddNodeMessage(addNode, ADD_NODE_CREATE_ERROR, true);
        } catch (error) {
            console.error('Table add-node error:', error);
            setAddNodeMessage(addNode, ADD_NODE_CREATE_ERROR, true);
        } finally {
            addNode?.removeAttribute('data-pending');
            restoreAddNodeActionButtons(addNode);
        }
    }

    function clearCreatedRowMarker() {
        document
            .querySelectorAll('tr[data-node-created="true"]')
            .forEach(row => row.removeAttribute('data-node-created'));
    }

    function positionCreatedNodeFromFeedback() {
        const feedback = getAddNodeFeedback();
        const createdNodeMid = feedback?.dataset.createdNodeMid;
        if (!createdNodeMid) return;

        clearCreatedRowMarker();

        const row = document.querySelector(
            `tr[data-node-mid="${createdNodeMid}"]`
        );
        if (!row) return;
        row.setAttribute('data-node-created', 'true');
        feedback.dataset.createdNodeMid = '';
    }

    // Save a viewport anchor before sorting or row filtering changes the table.
    // An open add-node menu takes priority because it is the control the user is
    // working with. During sorting, otherwise anchor the active table row.
    function handleBeforeTableStateChange(event) {
        const changeType = event.detail?.changeType;
        if (activeAddNodeContainerElement) {
            pendingTableStateAnchor = captureViewportAnchor(
                getAddNodeMenu(activeAddNodeContainerElement)
            );
            return;
        }
        if (changeType !== 'sorting') {
            pendingTableStateAnchor = null;
            return;
        }
        const activeCell = activeInlineFormCell || activeAutocompleteCell;
        pendingTableStateAnchor = captureViewportAnchor(
            activeCell?.closest('tr[data-row-type]')
        );
    }

    // Recalculate the add-node blockers after the table changes, then restore
    // the saved viewport position after the updated rows have been painted.
    function handleAfterTableStateChange() {
        const anchor = pendingTableStateAnchor;
        pendingTableStateAnchor = null;
        if (activeAddNodeContainerElement) {
            renderAddNodeBlockedState(activeAddNodeContainerElement);
        }
        afterNextRepaint(() => restoreViewportAnchor(anchor));
    }

    // --- Shared cell lifecycle ---

    // Inline forms and autocomplete fields use different input controls, but
    // both must ignore obsolete editor loads and serialize repeated saves for
    // the same cell.

    // Stop treating this cell as the active editor. This does not change its
    // markup. Callers decide whether to restore or preserve the visible editor.
    function clearActiveCellReference(cell) {
        if (activeInlineFormCell === cell) activeInlineFormCell = null;
        if (activeAutocompleteCell === cell) activeAutocompleteCell = null;
    }

    // Close an editor without saving. Restore the display markup captured when
    // editing started and discard validation errors and the form snapshot.
    function restoreCellDisplay(cell) {
        const state = getCellState(cell);
        updateMode(cell);
        cell.removeAttribute('data-validation-error');
        clearFieldErrors(cell);
        if (state.displayHTML !== undefined) {
            cell.innerHTML = state.displayHTML;
            state.displayHTML = undefined;
        }
        state.loadedFormData = undefined;
    }

    // Start opening an editor. Save the current display markup for cancellation
    // and assign a new opening number to the asynchronous request. Its response
    // is ignored if the user closes this opening or starts another one first.
    function startCellEditorLoad(cell) {
        const state = getCellState(cell);
        state.displayHTML = cell.innerHTML;
        state.loadedFormData = undefined;
        const editorOpeningNumber = ++state.editorOpeningNumber;
        cell.removeAttribute('data-validation-error');
        updateMode(cell, 'editing');
        loadCellEditor(cell, editorOpeningNumber);
    }

    function isEditorLoadCurrent(cell, editorOpeningNumber) {
        return (
            getCellState(cell).editorOpeningNumber === editorOpeningNumber
            && isCellActive(cell)
        );
    }

    // Restore display mode only when the failed request still belongs to the
    // active opening. A failure from an older opening must not change the cell.
    function recoverFromEditorLoadFailure(cell, editorOpeningNumber) {
        if (!isEditorLoadCurrent(cell, editorOpeningNumber)) return;
        clearActiveCellReference(cell);
        restoreCellDisplay(cell);
    }

    async function loadCellEditor(cell, editorOpeningNumber) {
        try {
            const response = await fetch(cell.dataset.url, {
                headers: { Accept: TURBO_ACCEPT },
            });
            const html = await response.text();
            if (!isEditorLoadCurrent(cell, editorOpeningNumber)) return;
            if (!response.ok) {
                console.error('Table editor load failed:', html);
                recoverFromEditorLoadFailure(cell, editorOpeningNumber);
                return;
            }

            // Apply the editor immediately after confirming that this opening
            // is still active. Deferring the DOM update would allow a user
            // action to make the response stale between the check and update.
            applyTableStream(html);
            const form = getFieldForm(cell);
            if (form) {
                getCellState(cell).loadedFormData = createFormData(
                    form
                ).toString();
            }
        } catch (error) {
            console.error('Table editor load error:', error);
            recoverFromEditorLoadFailure(cell, editorOpeningNumber);
        }
    }

    // Run no more than one save request for this cell. A second save attempt
    // waits for the active request. It stops if that request closed the editor
    // or sent the same input, and saves again if the user changed this cell
    // while waiting.
    async function runCellSaveInOrder(cell, saveOperation) {
        const state = getCellState(cell);
        if (state.activeSavePromise) {
            await state.activeSavePromise;
            if (cell.getAttribute('data-mode') !== 'editing') {
                return;
            }
            const submittedCellData = state.submittedCellData;
            const currentCellData = serializeCellFields(cell);
            if (
                submittedCellData !== undefined &&
                currentCellData === submittedCellData
            ) {
                return;
            }
            return runCellSaveInOrder(cell, saveOperation);
        }

        state.activeSavePromise = saveOperation();
        try {
            return await state.activeSavePromise;
        } finally {
            state.activeSavePromise = null;
        }
    }

    // --- Autocomplete cells ---

    // Autocomplete cells save when focus leaves the cell. A short blur delay
    // gives a dropdown selection time to update the value before saving. Save
    // responses follow the shared cell-session rules above.

    function getAutocompleteInput(cell) {
        // The editable marker belongs to the cell, while the selected value
        // belongs to the nested autocomplete control and its hidden input.
        // Return that control so the save path can read the normalized value.
        return cell.querySelector('sdoc-autocompletable');
    }

    function openAutocompleteCell(cell) {
        // Record every click, including a click on an editor that is already
        // open. A pending save uses this number to detect that the user resumed
        // editing before its response arrived.
        getCellState(cell).userInteractionNumber++;
        if (activeAutocompleteCell === cell) return;
        if (activeAutocompleteCell) cancelAutocompleteCell();
        if (activeInlineFormCell) saveInlineCell(activeInlineFormCell);

        activeAutocompleteCell = cell;
        if (cell.getAttribute('data-mode') === 'editing') return;
        startCellEditorLoad(cell);
    }

    function cancelAutocompleteCell() {
        if (!activeAutocompleteCell) return;
        const cell = activeAutocompleteCell;
        activeAutocompleteCell = null;
        cancelAutocompleteBlurSave(cell);
        restoreCellDisplay(cell);
    }

    function cancelAutocompleteBlurSave(cell) {
        const state = getCellState(cell);
        if (state.autocompleteBlurTimer !== null) {
            clearTimeout(state.autocompleteBlurTimer);
            state.autocompleteBlurTimer = null;
        }
    }

    function deactivateAutocompleteCell(cell) {
        if (activeAutocompleteCell === cell) {
            activeAutocompleteCell = null;
            updateMode(cell);
        }
    }

    function scheduleAutocompleteBlurSave(cell, autocompleteInput) {
        const state = getCellState(cell);
        cancelAutocompleteBlurSave(cell);
        state.autocompleteBlurTimer = setTimeout(function () {
            state.autocompleteBlurTimer = null;
            // Selecting an option may return focus to the autocomplete control.
            // In that case the user is still editing and blur must not save.
            // An outside click saves immediately, so this delayed handler must
            // also stop after another handler has finished the same edit.
            if (
                activeAutocompleteCell !== cell ||
                autocompleteInput === document.activeElement ||
                autocompleteInput.contains(document.activeElement)
            ) {
                return;
            }
            saveAutocompleteCell(cell, autocompleteInput);
        }, AUTOCOMPLETE_BLUR_SAVE_DELAY_MS);
    }

    function saveAutocompleteCell(cell, autocompleteInput) {
        if (!cell || !autocompleteInput) return Promise.resolve();
        cancelAutocompleteBlurSave(cell);
        return runCellSaveInOrder(
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

        if (newValue === originalValue) {
            // The normalized value is unchanged. Restore display mode without
            // sending a request.
            deactivateAutocompleteCell(cell);
            cell.removeAttribute('data-validation-error');
            if (state.displayHTML !== undefined) {
                cell.innerHTML = state.displayHTML;
                state.displayHTML = undefined;
            }
            return;
        }

        cell.dataset.currentValue = newValue;

        const formData = new FormData();
        formData.append('node_mid', cell.dataset.nodeMid);
        formData.append('field_name', cell.dataset.fieldName);
        formData.append('field_value', newValue);

        const savedUserInteractionNumber = state.userInteractionNumber;

        try {
            const { response, html } = await postTurboStream(
                '/actions/table/update_node_field',
                formData
            );
            const saveSession = classifySaveSession(
                cell,
                savedUserInteractionNumber
            );
            if (response.ok) {
                if (saveSession === SAVE_SESSION_REACTIVATED) {
                    // The server accepted the value sent by an older user
                    // interaction. Keep the current input visible. Store the
                    // accepted value as the display restored by Escape.
                    applySuccessfulSaveToReactivatedCell(html, cell);
                    return;
                }
                deactivateAutocompleteCell(cell);
                cell.removeAttribute('data-validation-error');
                state.displayHTML = undefined;
                applyTableStream(html);
            } else {
                cell.dataset.currentValue = originalValue;
                if (saveSession !== SAVE_SESSION_CURRENT) return;
                // This error belongs to the input that is still visible. Keep
                // the editor active so the user can correct the value or retry
                // by clicking outside again.
                cell.setAttribute('data-validation-error', 'true');
                clearFieldErrors(cell);
                const wrapperDiv = cell.querySelector(
                    '[wrapper-field-type="autocomplete"]'
                );
                if (wrapperDiv) {
                    parseErrorLines(
                        response,
                        html,
                        'Table autocomplete save error:'
                    ).forEach(line => {
                        wrapperDiv.appendChild(createFormErrorElement(line));
                    });
                }
            }
        } catch (error) {
            console.error('Table autocomplete save error:', error);
            cell.dataset.currentValue = originalValue;
            if (
                classifySaveSession(cell, savedUserInteractionNumber)
                !== SAVE_SESSION_CURRENT
            ) {
                return;
            }
            cell.setAttribute('data-validation-error', 'true');
            clearFieldErrors(cell);
            const wrapperDiv = cell.querySelector(
                '[wrapper-field-type="autocomplete"]'
            );
            if (wrapperDiv) {
                wrapperDiv.appendChild(
                    createFormErrorElement('Unable to save this field.')
                );
            }
        }
    }

    // --- Inline-form cells (contenteditable / comments / relations) ---

    // An inline form stays open until its value is saved, cancelled, or rejected.
    // When the user selects another cell, the current form saves first. The next
    // cell opens only after that save succeeds.

    function openInlineCell(cell) {
        if (activeInlineFormCell === cell) {
            // Clicking an already open editor means the user has resumed work
            // in that cell. Increment the interaction number so a pending save
            // cannot close the editor or replace the newer input.
            getCellState(cell).userInteractionNumber++;
            return;
        }
        if (activeInlineFormCell) {
            // The user clicked another inline-form cell. Save the current cell
            // first and remember the clicked cell. Keeping the current cell
            // active tells its response that this is a requested switch, not a
            // cancelled editor.
            const previousCell = activeInlineFormCell;
            pendingInlineFormCell = cell;
            saveInlineCell(previousCell);
            return;
        }
        pendingInlineFormCell = null;
        activeInlineFormCell = cell;
        getCellState(cell).userInteractionNumber++;
        // Validation leaves the existing editor visible but inactive. Reuse it
        // so the user's input and errors are not replaced by another fetch.
        if (cell.getAttribute('data-mode') === 'editing') return;
        startCellEditorLoad(cell);
    }

    // Open the cell that the user clicked while the previous cell was active.
    // Continue only after the previous value was saved, was unchanged, or had
    // no loaded editor to save.
    function openPendingCell() {
        if (pendingInlineFormCell) {
            const next = pendingInlineFormCell;
            pendingInlineFormCell = null;
            openInlineCell(next);
        }
    }

    function cancelInlineCell() {
        if (!activeInlineFormCell) return;
        pendingInlineFormCell = null;
        const cell = activeInlineFormCell;
        activeInlineFormCell = null;
        restoreCellDisplay(cell);
    }

    function cancelActiveCells() {
        if (activeInlineFormCell) cancelInlineCell();
        if (activeAutocompleteCell) cancelAutocompleteCell();
    }

    // --- Custom metadata row actions ---

    // Custom metadata rows share one form. Reordering and deletion therefore
    // submit the complete metadata list. The browser changes the row immediately
    // and restores the previous DOM position when the server rejects the change.

    function clearCustomMetaDragState() {
        customMetaDragState.row?.removeAttribute('data-dragging');
        customMetaDragState.targetRow?.removeAttribute('data-drop-position');
        customMetaDragState.armedRow = null;
        customMetaDragState.row = null;
        customMetaDragState.originalNextSibling = null;
        customMetaDragState.targetRow = null;
        customMetaDragState.position = null;
    }

    // Mark the row and insertion side currently under the dragged row. Clear
    // the previous marker first so only one drop position is visible.
    function setCustomMetaDropTarget(row, position) {
        customMetaDragState.targetRow?.removeAttribute('data-drop-position');
        customMetaDragState.targetRow = row;
        customMetaDragState.position = position;
        row?.setAttribute('data-drop-position', position);
    }

    // Save the order after a row is moved in the DOM. If the server rejects the
    // new order or the request fails, put the row back before the sibling that
    // originally followed it.
    async function saveCustomMetaReorder(row, originalNextSibling) {
        const form = row.closest(`[${ATTR_FORM}]`);
        if (!form) return;

        customMetaReorderPending = true;
        const formData = createFormData(form);
        formData.set('action', 'reorder');
        formData.set('active_form_key', row.dataset.formKey);

        try {
            const { response, html } = await postTurboStream(form.action, formData);
            if (response.ok) {
                applyTableStream(html);
                return;
            }
            console.error('Custom metadata reorder failed:', html);
        } catch (error) {
            console.error('Custom metadata reorder error:', error);
        } finally {
            customMetaReorderPending = false;
        }

        form.insertBefore(row, originalNextSibling);
    }

    // Remove the row immediately, then ask the server to delete it. Restore the
    // same DOM element at its original position if the request does not succeed.
    async function deleteCustomMetaRow(deleteAction) {
        const row = deleteAction.closest(`[${ATTR_CUSTOM_META_ROW}]`);
        const form = row?.closest(`[${ATTR_FORM}]`);
        if (!row || !form) return;

        cancelActiveCells();

        const formKey = row.dataset.formKey;
        const nextSibling = row.nextSibling;
        row.remove();

        const formData = createFormData(form);
        formData.set('action', 'delete');
        formData.set('active_form_key', formKey);

        try {
            const { response, html } = await postTurboStream(form.action, formData);
            if (response.ok) {
                applyTableStream(html);
                return;
            }
            console.error('Custom metadata delete failed:', html);
        } catch (error) {
            console.error('Custom metadata delete error:', error);
        }

        form.insertBefore(row, nextSibling);
    }

    // --- Inline-form saving and errors ---

    // Inline forms keep invalid input visible for correction. Save responses
    // update the cell only when the shared session classification permits it.

    // Validation responses contain one message per line. Server errors may
    // contain an HTML error page, so replace that body with one user-facing
    // message and write the original response to the console.
    function parseErrorLines(response, html, label) {
        if (response.status >= 500) {
            console.error(label, html);
            return ['Unable to save this field.'];
        }
        return html.trim().split('\n').filter(Boolean);
    }

    function createFormErrorElement(text) {
        const errorElement = document.createElement('sdoc-form-error');
        errorElement.setAttribute('data-testid', 'table-inline-field-error');
        errorElement.textContent = text.trim();
        return errorElement;
    }

    // Insert save errors into the open form. Place them before the final form
    // row when it exists so action controls remain below the messages.
    function renderInlineFieldErrors(form, cell, response, html) {
        cell.setAttribute('data-validation-error', 'true');
        const insertBeforeElement = form.querySelector(
            'sdoc-form-row:last-of-type'
        ) || null;
        parseErrorLines(response, html, 'Inline cell server error:').forEach(line => {
            const errorElement = createFormErrorElement(line);
            if (insertBeforeElement) {
                form.insertBefore(errorElement, insertBeforeElement);
            } else {
                form.appendChild(errorElement);
            }
        });
    }

    function saveInlineCell(cell) {
        if (!cell) return Promise.resolve();
        return runCellSaveInOrder(cell, () => performInlineCellSave(cell));
    }

    async function performInlineCellSave(cell) {
        const state = getCellState(cell);

        const form = getFieldForm(cell);
        // Most editable cells contain their own form. Custom metadata cells
        // share an ancestor form that exists before the editor is loaded.
        // Finding a form therefore does not prove that this cell contains an
        // editor.
        // Check for a form inside the cell or the hidden input that identifies
        // an open custom metadata field.
        const ownContentLoaded = Boolean(
            cell.querySelector(`[${ATTR_FORM}]`)
            || cell.querySelector('input[name="active_form_key"]')
        );
        if (!form || !ownContentLoaded) {
            // A click outside can request a save before the editor response
            // arrives. There is no user input to save, so restore display mode
            // and continue the requested cell switch.
            clearActiveCellReference(cell);
            restoreCellDisplay(cell);
            openPendingCell();
            return;
        }

        // Avoid a save request when the loaded form did not change. A new-row
        // editor is the exception: its empty value must reach the server so
        // required-field validation can decide whether the row may be created.
        const currentData = createFormData(form).toString();
        if (
            !cell.hasAttribute(ATTR_SUBMIT_UNCHANGED) &&
            state.loadedFormData !== undefined &&
            currentData === state.loadedFormData
        ) {
            if (activeInlineFormCell === cell) activeInlineFormCell = null;
            restoreCellDisplay(cell);
            openPendingCell();
            return;
        }

        // Remove errors from the previous attempt for this field. Errors in
        // other rows of a shared form must remain visible.
        clearFieldErrors(cell);

        const formData = buildCellSaveFormData(cell, form);
        // Save the exact input values sent by this request. Another save attempt
        // may already be waiting and uses this snapshot to decide whether it is
        // a duplicate or contains a correction.
        state.submittedCellData = serializeCellFields(cell);
        const savedUserInteractionNumber = state.userInteractionNumber;

        try {
            const { response, html } = await postTurboStream(form.action, formData);
            const saveSession = classifySaveSession(
                cell,
                savedUserInteractionNumber
            );
            if (response.ok) {
                if (saveSession === SAVE_SESSION_REACTIVATED) {
                    // The server accepted the value sent by an older user
                    // interaction. Keep the current input visible. Store the
                    // accepted value as the display restored by Escape.
                    pendingInlineFormCell = null;
                    applySuccessfulSaveToReactivatedCell(html, cell);
                } else {
                    // No newer interaction is active. Close this editor and
                    // show the value accepted by the server. If the user was
                    // switching cells, the requested cell can now be opened.
                    clearActiveCellReference(cell);
                    updateMode(cell);
                    cell.removeAttribute('data-validation-error');
                    state.displayHTML = undefined;
                    state.loadedFormData = undefined;
                    applyTableStream(html);
                    openPendingCell();
                }
            } else {
                pendingInlineFormCell = null;
                if (saveSession !== SAVE_SESSION_CURRENT) return;
                // This error belongs to the input that is still visible. Leave
                // its editor open for correction and cancel the requested
                // switch to another cell.
                clearActiveCellReference(cell);
                const contentType = response.headers.get('Content-Type') || '';
                if (contentType.includes('turbo-stream')) {
                    applyTableStream(html);
                } else {
                    renderInlineFieldErrors(form, cell, response, html);
                }
            }
        } catch (error) {
            console.error('Inline cell save error:', error);
            if (
                classifySaveSession(cell, savedUserInteractionNumber)
                !== SAVE_SESSION_CURRENT
            ) {
                return;
            }
            // The network failed while saving the visible input. Keep the
            // editor and its input available for another attempt.
            clearActiveCellReference(cell);
            pendingInlineFormCell = null;
            clearFieldErrors(cell);
            renderInlineFieldErrors(form, cell, { status: 500 }, '');
        }
    }

    // --- User input and document event handlers ---

    // The stable table container delegates events for controls that Turbo
    // Streams can replace. Document handlers manage keyboard commands and
    // clicks outside active controls.

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
            shouldKeepAddNodeMenuOpen = true;
            try {
                // Clicking the toolbar reset button immediately dispatches the
                // table-state-change event. That event recalculates the blockers
                // for the open menu. Do not recalculate them a second time here.
                document.querySelector(resetSelector)?.click();
            } finally {
                shouldKeepAddNodeMenuOpen = false;
            }
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

        // The link URL returns a Turbo Stream that inserts a new form row.
        // Fetch that stream without navigating away from the table.
        const addFieldLink = event.target.closest(`[${ATTR_ADD_FIELD}]`);
        if (addFieldLink) {
            event.preventDefault();
            fetchAndApplyTurboStream(addFieldLink.href);
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

        // Dragging changes row order, so close any editor whose saved display
        // markup belongs to the current order before moving the row.
        cancelActiveCells();

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
        // Move the row immediately so the drag interaction feels direct. Keep
        // the old order to avoid a server request when the row did not move.
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
            if (activeAddNodeContainerElement) {
                event.preventDefault();
                closeAddNodeMenu();
            }
            if (activeInlineFormCell) {
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
            activeInlineFormCell
        ) {
            const fieldType = activeInlineFormCell.getAttribute(ATTR_FIELD);
            if (
                fieldType === FIELD_CONTENTEDITABLE ||
                fieldType === FIELD_COMMENTS
            ) {
                event.preventDefault();
                saveInlineCell(activeInlineFormCell);
            }
        }
    }

    // A document-level handler closes controls when the user clicks outside
    // them. Cell saves are serialized, so a blur handler and this click handler
    // can safely request the same save.
    function handleDocumentClick(event) {
        const eventPath = event.composedPath();
        const tableToolbar = event.target.closest?.(
            '[data-testid="table-toolbar"]'
        );
        if (
            activeAddNodeContainerElement &&
            !shouldKeepAddNodeMenuOpen &&
            !tableToolbar &&
            !eventPath.includes(activeAddNodeContainerElement)
        ) {
            closeAddNodeMenu();
        }
        if (activeInlineFormCell && !eventPath.includes(activeInlineFormCell)) {
            saveInlineCell(activeInlineFormCell);
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
        const createdRow = document.querySelector(
            'tr[data-node-created="true"]'
        );
        if (createdRow && !eventPath.includes(createdRow)) {
            clearCreatedRowMarker();
        }
    }

    // --- Initialization ---

    // Register listeners on stable containers. Turbo Streams replace controls
    // inside the table, but these listeners must continue to handle the new
    // controls.
    function init() {
        const editButton = getEditModeButton();
        if (!editButton) return;

        editButton.addEventListener('click', handleEditModeToggle);

        const main = getMainContainer();
        if (!main) return;

        // The table replaces cell contents with Turbo Streams, so listeners on
        // individual controls would be lost. Delegate events from regular table
        // cells and document fields to their stable parent container.
        main.addEventListener('click', handleMainClick);
        main.addEventListener('dragstart', handleCustomMetaDragStart);
        main.addEventListener('pointerdown', handleCustomMetaPointerDown);
        main.addEventListener('pointerup', handleCustomMetaPointerUp);
        main.addEventListener('dragover', handleCustomMetaDragOver);
        main.addEventListener('drop', handleCustomMetaDrop);
        main.addEventListener('dragend', clearCustomMetaDragState);

        // Blur does not bubble. Capture it on the parent so dynamically loaded
        // autocomplete controls can still request a save. The autocomplete
        // component itself manages dropdown selection.
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
