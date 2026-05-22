(function () {

  // Lightweight UI behaviors for server-interactive pages.
  //
  // Requires Turbo (hotwired/turbo) to be loaded on the page.
  // Turbo dispatches its lifecycle events as standard DOM CustomEvents on
  // document, so no Turbo API is called directly — but without Turbo the
  // reset listeners below never fire. This is safe because without Turbo
  // form submissions trigger a full page reload, which resets the DOM anyway.
  // In StrictDoc this file is only loaded inside the is_running_on_server
  // block, alongside the Turbo script, so Turbo is always present.

  // Prevent double-clicks on action buttons from sending repeated requests.
  // Uses capture phase to intercept before Turbo sees the event.
  document.addEventListener('click', function (event) {
    const btn = event.target.closest('.action_button');
    if (!btn) return;
    if (!btn.matches('[data-turbo-method], [type="submit"]')) return;
    if (btn.dataset.pending) {
      event.preventDefault();
      event.stopImmediatePropagation();
      return;
    }
    btn.dataset.pending = 'true';
    btn.classList.add('pending');
  }, true);

  // Reset pending state when a request ends, so buttons in forms that
  // remain open after an error response become clickable again.
  function resetPending() {
    document.querySelectorAll('.action_button.pending').forEach(function (btn) {
      btn.classList.remove('pending');
      delete btn.dataset.pending;
    });
  }

  document.addEventListener('turbo:submit-end', resetPending);
  document.addEventListener('turbo:frame-render', resetPending);

})();
