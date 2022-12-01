import { Controller } from "/_static/stimulus.js";

Stimulus.register("hello", class extends Controller {
  static targets = ["name"];

  connect() {
    // this.element equal my form
    this.registerFormEvents();
  }

  registerFormEvents(params) {

    document.querySelectorAll('.std-input-editable')
      .forEach(editable => {
        const hidden = editable.nextElementSibling;
        editable.addEventListener('input', (event) => {
          hidden.value = event.target.innerText;
        });

      });
  }
});
