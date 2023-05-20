Stimulus.register("modal_controller", class extends Controller {
  initialize() {
    // this.element is the DOM element to which the controller is connected to.
    const thisElement = this.element;

    // Cancel button selector: [stimulus-modal-cancel-button]
    const cancelButton = thisElement.querySelector('[stimulus-modal-cancel-button]');

    // Clicking on the backdrop in this implementation
    // does not close the modal window:
    // const backdrop = thisElement.querySelector('sdoc-backdrop');

    // Removing a modal window code added using Turbo:
    const removeModal = () => {
      thisElement.remove()
    }

    // Removing the Escape listener:
    const removeEscapeListener = () => {
      document.removeEventListener("keydown", listenEscape);
    }

    // Listening to Escape:
    const listenEscape = (event) => {
      if (event.key === 'Escape') {
        removeModal();
        removeEscapeListener();
      }
    };

    // Add Listeners:

    document.addEventListener("keydown", listenEscape);

    cancelButton.addEventListener("click", function(event){
      event.preventDefault();
      removeModal();
    });

  }
});
