(() => {

  class EditableField extends Stimulus.Controller {
    static targets = ["name"];

    connect() {
      // this.element is the DOM element to which the controller is connected to.
      const editable = this.element;

      const isSingle = (editable.dataset.editable == 'single') ? true : false;
      const hidden = editable.nextElementSibling;

      editable.addEventListener('paste', (event) => {
        event.preventDefault();

        const clipboardText = (event.clipboardData || window.clipboardData).getData('text');
        const text = isSingle ? filterSingleLine(clipboardText) : clipboardText;

        const selection = window.getSelection();

        if (selection.rangeCount) {
          selection.deleteFromDocument();
          selection.getRangeAt(0).insertNode(document.createTextNode(text));
        }

        hidden.value = editable.innerText;
      });

      editable.addEventListener('input', (event) => {
        const editedText = editable.innerText;
        const text = isSingle ? filterSingleLine(editedText) : editedText;

        hidden.value = text;
      });

      if (isSingle) {
        editable.addEventListener('keydown', (event) => {
          if (event.key === 'Enter') {
            event.preventDefault();
          }
        });
      }
    }
  }

  Stimulus.application.register("editablefield", EditableField);

  function filterSingleLine(text) {
    return text.replace(/\s/g, ' ').replace(/\s\s+/g, ' ')
  }

})();
