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

        cell.classList.add('cell--editing');

        const input = document.createElement('input');
        input.type = 'text';
        input.className = 'cell-edit-input';
        input.value = activeCell._originalValue;

        const generation = ++editGeneration;

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

    function cancelEdit() {
        if (!activeCell) return;
        const cell = activeCell;
        activeCell = null;
        cell.classList.remove('cell--editing');
        cell.innerHTML = cell._originalHTML;
        delete cell._originalHTML;
        delete cell._originalValue;
    }

    async function submitEdit() {
        if (!activeCell) return;
        const cell = activeCell;
        const input = cell.querySelector('.cell-edit-input');
        const newValue = input ? input.value.trim() : '';
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
        }
    }

    function openMultilinePopup(cell) {
        const fieldName = cell.dataset.fieldName || '';
        const confirmSlot = document.getElementById('confirm');
        if (!confirmSlot) return;
        confirmSlot.innerHTML = `
<turbo-frame data-controller="modal_controller">
  <sdoc-backdrop>
    <sdoc-modal>
      <sdoc-modal-container>
        <p>Edit: <strong>${fieldName}</strong></p>
        <p>(form coming soon)</p>
      </sdoc-modal-container>
      <button stimulus-modal-cancel-button type="button" class="action_button" data-action-type="cancel" data-testid="form-cancel-action">Close</button>
    </sdoc-modal>
  </sdoc-backdrop>
</turbo-frame>`;
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
            }
        });

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
