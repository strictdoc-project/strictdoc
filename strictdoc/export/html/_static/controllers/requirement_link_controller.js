import { Controller } from "/_static/stimulus.js";

Stimulus.register("requirement_link", class extends Controller {
  connect() {
    // this.element is the DOM element to which the controller is connected to.
    const thisElement = this.element;
    const linksLinks = thisElement.querySelectorAll("[data-js-delete-link]");
    linksLinks.forEach(link => {
        link.addEventListener("click", function(event){
            event.preventDefault();
            thisElement.remove();
        });
    });
  }
});
