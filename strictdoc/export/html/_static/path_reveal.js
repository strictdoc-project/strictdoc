(() => {
  const revealPathPrefix = (pathRevealControl) => {
    const pathReveal = pathRevealControl.closest('[data-js-path-reveal]');
    if (!pathReveal) return;
    const pathIsRevealed = pathReveal.classList.toggle('revealed');
    pathRevealControl.setAttribute('aria-expanded', String(pathIsRevealed));
  };

  document.addEventListener('click', (event) => {
    const pathRevealControl = event.target.closest?.(
      '[data-js-path-reveal-control]',
    );
    if (!pathRevealControl) return;
    revealPathPrefix(pathRevealControl);
  });

  document.addEventListener('keydown', (event) => {
    if (event.key !== 'Enter' && event.key !== ' ') return;
    const pathRevealControl = event.target.closest?.(
      '[data-js-path-reveal-control]',
    );
    if (!pathRevealControl) return;
    event.preventDefault();
    revealPathPrefix(pathRevealControl);
  });
})();
