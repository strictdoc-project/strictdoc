// One delegated click listener for every "delete this field" button.
// sdoc-form-row (components/form/row/index.jinja) is the row boundary
// that gets removed.

(() => {

  document.addEventListener('click', (event) => {
    const btn = event.target.closest?.('[data-js-delete-field-action]');
    if (!btn) return;
    const row = btn.closest('sdoc-form-row');
    // Not every data-js-delete-field-action button lives inside a
    // sdoc-form-row (e.g. table_view_edit.js's custom-metadata rows handle
    // their own delete action) - leave those alone.
    if (!row) return;
    event.preventDefault();
    row.remove();
  });

})();
