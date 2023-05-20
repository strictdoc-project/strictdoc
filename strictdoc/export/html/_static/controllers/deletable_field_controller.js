Stimulus.register("deletable_field", class extends Controller {
  connect() {
    // this.element is the DOM element to which the controller is connected to.
    const thisElement = this.element;
    const commentLinks = thisElement.querySelectorAll("[data-js-delete-field-action]");
    commentLinks.forEach(link => {
        link.addEventListener("click", function(event){
            event.preventDefault();
            thisElement.remove();
        });
    });
  }
});
