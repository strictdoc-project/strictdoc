// Scrolls a newly inserted [data-js-scroll-into-view] element into view.
// Used by forms delivered via Turbo Stream (edit config, add/edit
// section/requirement) so the form is visible as soon as it appears.
// Uses the shared StrictDoc.onInsert (app_core.js) instead of its own
// MutationObserver - see the onInsert contract there for why.

(() => {
  window.StrictDoc.onInsert('[data-js-scroll-into-view]', (el) => el.scrollIntoView());
})();
