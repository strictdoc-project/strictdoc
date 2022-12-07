import { Controller } from "/_static/stimulus.js";

Stimulus.register("hello", class extends Controller {
  static targets = ["name"];

  connect() {
    // this.element equal my form
    this.registerFormEvents();
  }

  registerFormEvents(params) {

    document.querySelectorAll('[data-editable]')
      .forEach(editable => {
        const hidden = editable.nextElementSibling;

        editable.addEventListener('paste', (event) => {
          event.preventDefault();

          const text = (event.clipboardData || window.clipboardData).getData('text');
          const selection = window.getSelection();

          if (selection.rangeCount) {
            selection.deleteFromDocument();
            selection.getRangeAt(0).insertNode(document.createTextNode(text));
          }

          hidden.value = editable.innerText;
        });
        editable.addEventListener('input', (event) => {
          hidden.value = editable.innerText;
        });

      });
  }
});
