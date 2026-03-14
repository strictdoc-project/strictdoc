/*
app_core.js

window.StrictDoc is the shared runtime root for plain frontend scripts.
Supported shared namespaces:
- StrictDoc.events
- StrictDoc.bus
- StrictDoc.config
- StrictDoc.search
- StrictDoc.project

Feature scripts should keep their own logic in local scope and only use
StrictDoc.* for intentional cross-script contracts and shared runtime data.
*/

(function (global) {
  const strictDoc = global.StrictDoc || (global.StrictDoc = {});

  // Shared event names used across feature scripts.
  strictDoc.events = strictDoc.events || {};
  strictDoc.config = strictDoc.config || {};
  strictDoc.search = strictDoc.search || {};
  strictDoc.project = strictDoc.project || {};
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
