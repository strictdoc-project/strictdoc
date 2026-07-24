// Supports multiple dropdown menus (toggle/content pairs) anywhere on the
// page - view-type menu, header actions, per-node "Add node" menu - each
// independent by id.
// Toggle: [data-dropdown-handler] + aria-controls="id_of_content".
// Content: element with that id + aria-hidden.
//
// Uses the shared StrictDoc.onInsert (app_core.js): a toggle inserted
// anywhere later (Turbo Stream/Frame response, a dynamically added node)
// is wired up automatically, no extra registration needed.

(() => {

  // Every registered toggle. Content is resolved on demand (not cached at
  // registration time) for two reasons: during the initial page parse, a
  // toggle can be inserted (and its onInsert callback fire) slightly before
  // its sibling content element with the matching id exists yet; and a
  // Turbo Stream update can later replace the content element outright,
  // which would leave a cached reference pointing at a detached node.
  const toggles = [];

  function contentOf(toggle) {
    const id = toggle.getAttribute('aria-controls');
    return id ? document.getElementById(id) : null;
  }

  // Opening one hides every other pair on the page - not just pairs of the
  // same kind - so only one dropdown is ever open at a time.
  function show(toggle) {
    toggles.forEach((t) => {
      const content = contentOf(t);
      if (!content) return;
      const isThis = t === toggle;
      t.setAttribute('aria-expanded', isThis);
      content.setAttribute('aria-hidden', !isThis);
    });
  }

  function hide(toggle) {
    const content = contentOf(toggle);
    toggle.setAttribute('aria-expanded', false);
    if (content) content.setAttribute('aria-hidden', true);
  }

  window.StrictDoc.onInsert('[data-dropdown-handler]', (toggle) => {
    toggles.push(toggle);
  });

  document.addEventListener('click', (event) => {
    const toggle = event.target.closest?.('[data-dropdown-handler]');
    if (toggle) {
      JSON.parse(toggle.getAttribute('aria-expanded')) ? hide(toggle) : show(toggle);
      return;
    }

    // Close every toggle whose content wasn't the click target - either the
    // click landed fully outside the toggle+content, or it was a link/action
    // inside an open menu's content (e.g. "Add node" menu items), which
    // should close that menu right away rather than wait to navigate away.
    toggles.forEach((t) => {
      const content = contentOf(t);
      if (!content) return;
      const clickedLink = event.target.closest?.('a');
      const clickedContentLink = clickedLink && content.contains(clickedLink);
      const clickedOutside = !t.contains(event.target) && !content.contains(event.target);
      if (clickedContentLink || clickedOutside) hide(t);
    });
  });

  // Close on focus moving outside both the toggle and the content (keyboard
  // navigation away from an open menu).
  document.addEventListener('focusin', (event) => {
    toggles.forEach((t) => {
      const content = contentOf(t);
      if (!content) return;
      if (!t.contains(event.target) && !content.contains(event.target)) hide(t);
    });
  });

})();
