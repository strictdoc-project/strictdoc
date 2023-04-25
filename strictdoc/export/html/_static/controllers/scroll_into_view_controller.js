import { Controller } from "/_static/stimulus.js";

Stimulus.register("scroll_into_view", class extends Controller {
  connect() {
    // console.log(this.element)
    // this.element.scrollIntoViewIfNeeded()
    this.element.scrollIntoView()
  }
});
