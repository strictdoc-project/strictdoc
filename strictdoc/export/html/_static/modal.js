// One delegated click listener for the cancel button, one delegated
// click listener for opening a template-based static modal, and one
// delegated keydown listener for Escape, covering every modal - nothing
// is registered or needs cleanup per modal instance.

(() => {

  const SEL_MODAL = '[data-js-modal]';
  const SEL_CANCEL = '[data-js-modal-cancel-button]';
  const SEL_TRIGGER = '[data-js-modal-template-trigger]';

  document.addEventListener('click', (event) => {
    const btn = event.target.closest?.(SEL_CANCEL);
    if (!btn) return;
    const modal = btn.closest(SEL_MODAL);
    if (!modal) return;
    event.preventDefault();
    modal.remove();
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
    document.querySelectorAll(SEL_MODAL).forEach((modal) => modal.remove());
  });

})();
