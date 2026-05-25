(function () {
    let editMode = false;
    let activeCell = null;
    let editGeneration = 0;

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
        if (!on && activeCell) {
            cancelEdit();
        }
    }

    function activateCell(cell) {
        if (activeCell === cell) return;
        if (activeCell) cancelEdit();

        activeCell = cell;
        activeCell._originalHTML = cell.innerHTML;
        activeCell._originalValue = (cell.dataset.currentValue || '').trim();

        cell.removeAttribute('data-validation-error');
        cell.classList.add('cell--editing');

        const generation = ++editGeneration;

        const input = document.createElement('input');
        input.type = 'text';
        input.className = 'cell-edit-input';
        input.value = activeCell._originalValue;

        input.addEventListener('keydown', function (e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                e.stopPropagation();
                submitEdit();
            } else if (e.key === 'Escape') {
                e.preventDefault();
                e.stopPropagation();
                cancelEdit();
            }
        });

        input.addEventListener('blur', function () {
            setTimeout(function () {
                if (activeCell === cell && editGeneration === generation) {
                    submitEdit();
                }
            }, 150);
        });

        input.addEventListener('click', function (e) {
            e.stopPropagation();
        });

        cell.innerHTML = '';
        cell.appendChild(input);
        input.focus();
        input.select();
    }

    async function saveAutocompleteCell(cell, ac) {
        const hiddenInput = ac.nextElementSibling;
        const rawValue = hiddenInput ? hiddenInput.value : ac.innerText;
        const newValue = rawValue.trim().replace(/,\s*$/, '').trim();
        const originalValue = (cell.dataset.currentValue || '').trim();
        if (newValue === originalValue) return;

        cell.dataset.currentValue = newValue;

        const formData = new FormData();
        formData.append('node_mid', cell.dataset.nodeMid);
        formData.append('field_name', cell.dataset.fieldName);
        formData.append('field_value', newValue);

        try {
            const response = await fetch('/actions/table/update_node_field', {
                method: 'POST',
                headers: { 'Accept': 'text/vnd.turbo-stream.html' },
                body: formData,
            });
            const html = await response.text();
            if (response.ok) {
                if (typeof Turbo !== 'undefined' && typeof Turbo.renderStreamMessage === 'function') {
                    Turbo.renderStreamMessage(html);
                }
            } else {
                console.error('Table autocomplete save failed:', html);
                cell.dataset.currentValue = originalValue;
                cell.setAttribute('data-validation-error', 'true');
            }
        } catch (err) {
            console.error('Table autocomplete save error:', err);
            cell.dataset.currentValue = originalValue;
        }
    }

    function cancelEdit() {
        if (!activeCell) return;
        const cell = activeCell;
        activeCell = null;
        cell.classList.remove('cell--editing');
        cell.innerHTML = cell._originalHTML;
        delete cell._originalHTML;
        delete cell._originalValue;
    }

    function getEditValue(cell) {
        const input = cell.querySelector('.cell-edit-input');
        if (!input) return '';
        return input.value.trim();
    }

    async function submitEdit() {
        if (!activeCell) return;
        const cell = activeCell;
        const newValue = getEditValue(cell);
        const originalValue = cell._originalValue;

        activeCell = null;
        cell.classList.remove('cell--editing');

        if (newValue === originalValue) {
            cell.innerHTML = cell._originalHTML;
            delete cell._originalHTML;
            delete cell._originalValue;
            return;
        }

        cell.innerHTML = cell._originalHTML;
        cell.dataset.currentValue = newValue;

        const formData = new FormData();
        formData.append('node_mid', cell.dataset.nodeMid);
        formData.append('field_name', cell.dataset.fieldName);
        formData.append('field_value', newValue);

        delete cell._originalHTML;
        delete cell._originalValue;

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
                if (typeof Turbo !== 'undefined' && typeof Turbo.renderStreamMessage === 'function') {
                    Turbo.renderStreamMessage(html);
                }
            } else {
                console.error('Table cell update failed:', html);
            }
        } catch (err) {
            console.error('Table cell update error:', err);
        }

        if (!ok) {
            cell.dataset.currentValue = originalValue;
            cell.setAttribute('data-validation-error', 'true');
        }
    }

    async function openMultilinePopup(cell) {
        const nodeMid = cell.dataset.nodeMid || '';
        const fieldName = cell.dataset.fieldName || '';
        if (!nodeMid || !fieldName) return;

        try {
            const response = await fetch(
                `/actions/table/get_node_field_form?node_mid=${encodeURIComponent(nodeMid)}&field_name=${encodeURIComponent(fieldName)}`,
                { headers: { 'Accept': 'text/vnd.turbo-stream.html' } }
            );
            const html = await response.text();
            if (response.ok && typeof Turbo !== 'undefined' && typeof Turbo.renderStreamMessage === 'function') {
                Turbo.renderStreamMessage(html);
            }
        } catch (err) {
            console.error('Table multiline popup error:', err);
        }
    }

    async function openRelationsPopup(cell) {
        const nodeMid = cell.dataset.nodeMid || '';
        if (!nodeMid) return;

        try {
            const response = await fetch(
                `/actions/table/get_node_relations_form?node_mid=${encodeURIComponent(nodeMid)}`,
                { headers: { 'Accept': 'text/vnd.turbo-stream.html' } }
            );
            const html = await response.text();
            if (response.ok && typeof Turbo !== 'undefined' && typeof Turbo.renderStreamMessage === 'function') {
                Turbo.renderStreamMessage(html);
            }
        } catch (err) {
            console.error('Table relations popup error:', err);
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
            const autocompleteCell = e.target.closest('[data-field-type="autocomplete"]');
            if (autocompleteCell) {
                e.stopPropagation();
                return;
            }
            const singlelineCell = e.target.closest('[data-field-type="singleline"]');
            if (singlelineCell) {
                e.stopPropagation();
                activateCell(singlelineCell);
                return;
            }
            const multilineCell = e.target.closest('[data-field-type="multiline"]');
            if (multilineCell) {
                e.stopPropagation();
                openMultilinePopup(multilineCell);
                return;
            }
            const relationsCell = e.target.closest('[data-field-type="relations"]');
            if (relationsCell) {
                e.stopPropagation();
                openRelationsPopup(relationsCell);
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

        document.addEventListener('click', function (e) {
            if (!activeCell) return;
            const table_ = getTable();
            if (table_ && !table_.contains(e.target)) {
                submitEdit();
            }
        });
    }

    window.addEventListener('load', init);
})();
