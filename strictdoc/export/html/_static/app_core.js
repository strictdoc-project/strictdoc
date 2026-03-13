/*
app_core.js
Shared runtime contract for plain-script modules (no bundler required).
*/

(function (global) {
  const strictDoc = global.StrictDoc || (global.StrictDoc = {});

  // Shared event names used across feature scripts.
  strictDoc.events = strictDoc.events || {};
  strictDoc.config = strictDoc.config || {};
  if (!strictDoc.events.TOC_STATE_CHANGED) {
    strictDoc.events.TOC_STATE_CHANGED = 'toc:state-changed';
  }

  // Minimal event bus wrapper over document-level CustomEvent transport.
  if (!strictDoc.bus) {
    strictDoc.bus = {
      on(eventName, handler) {
        document.addEventListener(eventName, handler);
        return function unsubscribe() {
          document.removeEventListener(eventName, handler);
        };
      },
      emit(eventName, detail) {
        document.dispatchEvent(new CustomEvent(eventName, { detail: detail }));
      },
    };
  }
})(window);
