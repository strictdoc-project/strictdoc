import { Controller } from "./stimulus.js";

Stimulus.register("document", class extends Controller {
  connect() {
    console.log("DocumentController connected: ", this.element);
  }
  editSection() {
    console.log("DocumentController#editSection", this.element);
  }
});
