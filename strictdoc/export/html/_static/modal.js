// One delegated click listener for the cancel button, and one delegated
// keydown listener for Escape, covering every modal - nothing is
// registered or needs cleanup per modal instance.

(() => {

  const SEL_MODAL = '[data-js-modal]';
  const SEL_CANCEL = '[data-js-modal-cancel-button]';

  document.addEventListener('click', (event) => {
    const btn = event.target.closest?.(SEL_CANCEL);
    if (!btn) return;
    const modal = btn.closest(SEL_MODAL);
    if (!modal) return;
    event.preventDefault();
    modal.remove();
  });

  document.addEventListener('keydown', (event) => {
    if (event.key !== 'Escape') return;
    document.querySelectorAll(SEL_MODAL).forEach((modal) => modal.remove());
  });

})();
