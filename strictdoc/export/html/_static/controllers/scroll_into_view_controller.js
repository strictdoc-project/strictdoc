(() => {

  class ScrollIntoView extends Stimulus.Controller {
    connect() {
      this.element.scrollIntoView()
    }
  }

  Stimulus.application.register("scroll_into_view", ScrollIntoView);

})();
