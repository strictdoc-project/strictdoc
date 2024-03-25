const ROOT_SELECTOR = 'js-collapsible_tree';

window.addEventListener("DOMContentLoaded", function(){

  const tree = document.querySelector(`[${ROOT_SELECTOR}]`);
  if (!tree) { return }

  const summaries = tree.querySelectorAll('summary');

  summaries.forEach(summary => {
    summary.addEventListener('dblclick', () => {
      const details = summary.parentElement;
      if (details.nodeName !== 'DETAILS') {
        console.warn('The DETAILS tag has an unexpected structure.');
        return
      }
      const open = details.hasAttribute("open");

      const innerSummaries = details.querySelectorAll('summary');

      innerSummaries.forEach(summary => {
        const details = summary.parentElement;
        if (open) {
          details.removeAttribute("open")
        } else (
          details.setAttribute("open", "")
        )
      })
    });
  })

},false);
