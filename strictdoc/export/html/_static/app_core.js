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

Bus contract (event name -> emitter -> listener(s) -> payload):
- TOC_STATE_CHANGED ('toc:state-changed')
    emitted by: collapsible_toc.js, after any collapse/expand change
      (manual click, bulk action, undo).
    listened by: toc_highlighting.js, to recompute which TOC items are
      currently visible/highlighted.
    payload: none.
    Note: unrelated to navigation. collapsible_toc.js reacts to URL
    navigation on its own (a plain `hashchange` listener, mirroring how
    toc_highlighting.js already reacts to `hashchange` independently) -
    it does not derive that from this event. Keeping these reactions on
    their own native triggers, instead of chaining them through each
    other's recompute cycle, is what avoids a feedback loop (a manual
    collapse triggering this event must never be able to re-expand
    itself via some other listener's reaction to it).
- TOC_FRAGMENT_RESOLVED ('toc:fragment-resolved')
    emitted by: toc_highlighting.js, only for the edge case where the
      URL hash points at a renamed/renumbered anchor: it resolves the
      new id and silently corrects the URL via history.replaceState(),
      which - unlike a real navigation - does not fire `hashchange`.
    listened by: collapsible_toc.js, to expand collapsed ancestor
      branches up to (not including) the corrected anchor (its own
      `hashchange` listener could not have seen this correction).
    payload: { anchor: string } - the corrected anchor id (matches the
      TOC link's `anchor` attribute), not a DOM reference, so this event
      is safe to log/replay without reaching into either module's
      internal state.
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
  if (!strictDoc.events.TOC_FRAGMENT_RESOLVED) {
    strictDoc.events.TOC_FRAGMENT_RESOLVED = 'toc:fragment-resolved';
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
