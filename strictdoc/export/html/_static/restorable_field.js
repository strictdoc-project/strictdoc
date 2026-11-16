// One delegated click listener for every "restore this field's previous
// value" button. Writes the value into the visible contenteditable with
// setText() of editable_field.js: the write is one step of the undo history
// of the field, and its 'input' event syncs the hidden input. The listener
// also clears the field's validation errors: they described why the
// rejected value was invalid, which no longer applies once the field is
// back to its known-good value.

(() => {

  const editableField = window.StrictDoc.editableField;

  document.addEventListener('click', (event) => {
    const btn = event.target.closest?.('[data-js-restore-field-action]');
    if (!btn) return;
    event.preventDefault();

    const row = btn.closest('sdoc-form-row');
    if (!row) return;
    const editable = row.querySelector('[data-js-editable-field]');
    if (!editable) return;

    editableField.setText(editable, btn.dataset.restoreValue);

    row.querySelectorAll('sdoc-form-error').forEach((errorEl) => errorEl.remove());
  });

})();
