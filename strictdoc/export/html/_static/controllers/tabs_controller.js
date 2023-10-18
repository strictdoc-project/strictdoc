Stimulus.register("tabs", class extends Controller {
  initialize() {

    // ** Tab buttons like this:
    // <sdoc-tabs>
    //  <sdoc-tab style="order: 0;" active>Id1</sdoc-tab>
    //  <sdoc-tab style="order: 1;">Id2</sdoc-tab>
    // </sdoc-tab>
    const sdocTabs = document.createElement('sdoc-tabs');
    const sdocTabContent = [...this.element.querySelectorAll('sdoc-tab-content')];
    const tabsData = sdocTabContent.reduce(
      (accumulator, currentSdocTabContentElement, currentIndex) => {
      // get data from the contents of the tab element in the DOM:
      const key = currentSdocTabContentElement.id;
      const state = currentSdocTabContentElement.hasAttribute('active');

      const errors =[...currentSdocTabContentElement.querySelectorAll('sdoc-form-error')];

      // create and prepare tab element:
      const sdocTab = document.createElement('sdoc-tab');
      sdocTab.style.order = currentIndex;
      sdocTab.innerHTML = key;
      sdocTab.addEventListener("mouseup", () => {
        this._activateTab(tabsData.tabs, key)
      });
      sdocTabs.append(sdocTab);
      sdocTab.setAttribute('data-testid', `form-tab-${key}`);
      state && sdocTab.setAttribute('active', '');

      if(errors.length) {
        sdocTab.setAttribute('data-errors', errors.length);
        accumulator.errors.push(key);
      }

      // update accumulator (form state):
      accumulator.tabs[key] = {};
      accumulator.tabs[key].element = currentSdocTabContentElement;
      accumulator.tabs[key].order = currentIndex;
      accumulator.tabs[key].state = state;
      accumulator.tabs[key].handler = sdocTab;
      accumulator.tabs[key].errors = errors.length;

      return accumulator;
    }, {
      tabs:{},
      errors:[]
    });

    // put tab handlers to the DOM
    sdocTabContent.length && this.element.prepend(sdocTabs);

    // activate first tab with errors
    tabsData.errors.length && this._activateTab(tabsData.tabs, tabsData.errors[0]);
  }

  _activateTab(tabs, tabName) {
    for (const {element, handler} of Object.values(tabs)) {
      element.removeAttribute('active');
      handler.removeAttribute('active');
    }
    // activate the tab:
    tabs[tabName].element.setAttribute('active', '');
    tabs[tabName].handler.setAttribute('active', '');
  }
});
