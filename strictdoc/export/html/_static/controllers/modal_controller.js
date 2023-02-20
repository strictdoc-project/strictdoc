import { Controller } from "/_static/stimulus.js";

Stimulus.register("modal_controller", class extends Controller {
  initialize() {
    // this.element is the DOM element to which the controller is connected to.
    const thisElement = this.element;

    console.log(thisElement)

    const cancelButton = thisElement.querySelector('[stimulus-modal-cancel-button]');
    cancelButton.addEventListener("click", function(event){
      event.preventDefault();
      thisElement.closest('#modal').innerHTML = "";
    });
  }
});
