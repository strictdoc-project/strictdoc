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

    // A field can carry more than one <sdoc-form-error> (e.g. a UID field
    // failing both the uniqueness check and the rename-with-relations
    // check at once). The badge must count invalid fields, not messages,
    // so errors are deduplicated by their closest field-owning ancestor.
    const FIELD_WRAPPER_SELECTOR = 'sdoc-form-row, sdoc-form-field-group, sdoc-form-field';

    sdocTabContent.forEach((contentEl, index) => {
      const key = contentEl.id;
      const errorFields = new Set(
        [...contentEl.querySelectorAll('sdoc-form-error')].map(
          (errorEl) => errorEl.closest(FIELD_WRAPPER_SELECTOR) || errorEl
        )
      );

      const tabEl = document.createElement('sdoc-tab');
      tabEl.style.order = index;
      tabEl.innerHTML = key;
      tabEl.setAttribute('data-testid', `form-tab-${key}`);
      tabEl.addEventListener('mouseup', () => activateTab(tabs, key));
      if (contentEl.hasAttribute('active')) tabEl.setAttribute('active', '');
      if (errorFields.size) {
        tabEl.setAttribute('data-errors', errorFields.size);
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
