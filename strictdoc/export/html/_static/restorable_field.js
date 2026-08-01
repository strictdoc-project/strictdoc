// One delegated click listener for every "restore this field's previous
// value" button. Sets both the visible contenteditable and its hidden
// mirror input (editable_field.js keeps them in sync on user input, but a
// programmatic value change needs to update both explicitly), and clears
// the field's validation errors: they described why the rejected value
// was invalid, which no longer applies once the field is back to its
// known-good value.

(() => {

  document.addEventListener('click', (event) => {
    const btn = event.target.closest?.('[data-js-restore-field-action]');
    if (!btn) return;
    event.preventDefault();

    const row = btn.closest('sdoc-form-row');
    if (!row) return;
    const editable = row.querySelector('[data-js-editable-field]');
    if (!editable) return;

    const restoreValue = btn.dataset.restoreValue;
    const hidden = editable.nextElementSibling;

    editable.textContent = restoreValue;
    hidden.value = restoreValue;

    row.querySelectorAll('sdoc-form-error').forEach((errorEl) => errorEl.remove());
  });

})();
