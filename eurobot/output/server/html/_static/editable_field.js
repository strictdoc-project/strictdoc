// Three delegated document-level listeners (paste, input, keydown) for
// every contenteditable field. All three event types bubble, so no
// per-element registration (StrictDoc.onInsert) is needed - unlike the
// click-only controls, these only ever need to know about the element an
// event already fired on.

(() => {

  const SEL_EDITABLE = '[data-js-editable-field]';

  function filterSingleLine(text) {
    return text.replace(/\s/g, ' ').replace(/\s\s+/g, ' ');
  }

  document.addEventListener('paste', (event) => {
    const editable = event.target.closest?.(SEL_EDITABLE);
    if (!editable) return;
    event.preventDefault();

    const isSingle = editable.dataset.fieldType === 'singleline';
    const hidden = editable.nextElementSibling;

    const clipboardText = (event.clipboardData || window.clipboardData).getData('text');
    const text = isSingle ? filterSingleLine(clipboardText) : clipboardText;

    const selection = window.getSelection();
    if (selection.rangeCount) {
      selection.deleteFromDocument();
      selection.getRangeAt(0).insertNode(document.createTextNode(text));
    }

    hidden.value = editable.innerText;
  });

  document.addEventListener('input', (event) => {
    const editable = event.target.closest?.(SEL_EDITABLE);
    if (!editable) return;

    const isSingle = editable.dataset.fieldType === 'singleline';
    const hidden = editable.nextElementSibling;

    const editedText = editable.innerText;
    hidden.value = isSingle ? filterSingleLine(editedText) : editedText;
  });

  document.addEventListener('keydown', (event) => {
    if (event.key !== 'Enter') return;
    const editable = event.target.closest?.(SEL_EDITABLE);
    if (!editable) return;
    if (editable.dataset.fieldType !== 'singleline') return;
    event.preventDefault();
  });

})();
