// One delegated click listener for the cancel button, one delegated
// click listener for opening a template-based static modal, and one
// delegated keydown listener for Escape, covering every modal - nothing
// is registered or needs cleanup per modal instance.

(() => {

  const SEL_MODAL = '[data-js-modal]';
  const SEL_CANCEL = '[data-js-modal-cancel-button]';
  const SEL_TRIGGER = '[data-js-modal-template-trigger]';

  const requestClose = (modal) => {
    // A settings reload keeps the old in-memory project active until the new
    // state is ready. Closing the modal would make that transition invisible
    // and let the user continue against a state that is about to be replaced.
    if (modal.querySelector('[data-js-project-settings-reload-blocking]')) {
      return;
    }
    if (modal.querySelector('[data-js-project-settings-form]')) {
      modal.dispatchEvent(new CustomEvent('settings:close-requested'));
      return;
    }
    modal.remove();
  };

  document.addEventListener('click', (event) => {
    const btn = event.target.closest?.(SEL_CANCEL);
    if (!btn) return;
    const modal = btn.closest(SEL_MODAL);
    if (!modal) return;
    event.preventDefault();
    requestClose(modal);
  });

  document.addEventListener('click', (event) => {
    const trigger = event.target.closest?.(SEL_TRIGGER);
    if (!trigger) return;
    const template = document.getElementById(
      trigger.dataset.jsModalTemplateTrigger,
    );
    if (!(template instanceof HTMLTemplateElement)) return;
    document.getElementById('modal').innerHTML = template.innerHTML;
  });

  document.addEventListener('keydown', (event) => {
    if (event.key !== 'Escape') return;
    document.querySelectorAll(SEL_MODAL).forEach((modal) => {
      requestClose(modal);
    });
  });

})();
