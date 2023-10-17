Stimulus.register("tabs", class extends Controller {
  initialize() {

    // ** Tab buttons like this:
    // <sdoc-tabs>
    //  <sdoc-tab style="order: 0;" active>Id1</sdoc-tab>
    //  <sdoc-tab style="order: 1;">Id2</sdoc-tab>
    // </sdoc-tab>
    const sdocTabs = document.createElement('sdoc-tabs');

    const tabs =[...this.element.querySelectorAll('sdoc-tab-content')]
    .reduce((accumulator, currentSdocTabContentElement, currentIndex) => {
      // get data from the content element in DOM:
      const key = currentSdocTabContentElement.id;
      const state = currentSdocTabContentElement.hasAttribute('active');

      // create and prepare tab element:
      const sdocTab = document.createElement('sdoc-tab');
      sdocTab.style.order = currentIndex;
      sdocTab.innerHTML = key;
      sdocTab.addEventListener("mouseup",() => {
        // deactivate all tabs:
        for (const {element, handler} of Object.values(tabs)) {
          element.removeAttribute('active');
          handler.removeAttribute('active');
        }
        // activate the tab:
        tabs[key].element.setAttribute('active', '');
        tabs[key].handler.setAttribute('active', '');
      });
      sdocTabs.append(sdocTab);
      sdocTab.setAttribute('data-testid', `form-tab-${key}`);
      state && sdocTab.setAttribute('active', '');

      // update accumulator (form state):
      accumulator[key] = {};
      accumulator[key].element = currentSdocTabContentElement;
      accumulator[key].order = currentIndex;
      accumulator[key].state = state;
      accumulator[key].handler = sdocTab;

      return accumulator;
    }, {});

    // put tab handlers to the DOM
    this.element.prepend(sdocTabs);
  }
});
