// Builds the <sdoc-tabs> tab bar from a form's <sdoc-tab-content> children,
// once when the form is inserted (StrictDoc.onInsert).

(() => {

  function activateTab(tabs, tabName) {
    for (const {
        element,
        handler
      }
      of Object.values(tabs)) {
      element.removeAttribute('active');
      handler.removeAttribute('active');
    }
    tabs[tabName].element.setAttribute('active', '');
    tabs[tabName].handler.setAttribute('active', '');
  }

  function initTabs(root) {
    // Defensive: a given root should only ever be processed once, but this
    // function prepends DOM (not naturally idempotent) - guard just in case.
    if (root.dataset.jsTabsInitialized) return;
    root.dataset.jsTabsInitialized = 'true';

    const sdocTabContent = [...root.querySelectorAll('sdoc-tab-content')];
    if (!sdocTabContent.length) return;

    const sdocTabs = document.createElement('sdoc-tabs');
    const tabs = {};
    const errorTabs = [];

    sdocTabContent.forEach((contentEl, index) => {
      const key = contentEl.id;
      const errors = contentEl.querySelectorAll('sdoc-form-error');

      const tabEl = document.createElement('sdoc-tab');
      tabEl.style.order = index;
      tabEl.innerHTML = key;
      tabEl.setAttribute('data-testid', `form-tab-${key}`);
      tabEl.addEventListener('mouseup', () => activateTab(tabs, key));
      if (contentEl.hasAttribute('active')) tabEl.setAttribute('active', '');
      if (errors.length) {
        tabEl.setAttribute('data-errors', errors.length);
        errorTabs.push(key);
      }

      sdocTabs.append(tabEl);
      tabs[key] = {
        element: contentEl,
        handler: tabEl
      };
    });

    root.prepend(sdocTabs);

    if (errorTabs.length) activateTab(tabs, errorTabs[0]);
  }

  window.StrictDoc.onInsert('[data-js-tabs]', initTabs);

})();
