
// **
// Place this code right after the opening BODY tag:

// <script>document.body.dataset.toc_state = sessionStorage.getItem('tocState') || 'open';</script>

// This ensures that the status of the sidebar is preserved when the page is reloaded.
// **

let setTocState = sessionStorage.getItem('tocState');
sessionStorage.setItem('tocState', (setTocState ? setTocState : 'open'));

function switchTOC() {
  sessionStorage.setItem('tocState', (
    sessionStorage.getItem('tocState') === 'open'
      ? 'close'
      : 'open'
  ));
  document.body.dataset.toc_state = sessionStorage.getItem('tocState');
}

window.addEventListener("load",function(){
  document.body.dataset.toc_state = sessionStorage.getItem('tocState');
  document.querySelector('[js-toc-handler]').addEventListener('click', () => {
    switchTOC();
  });
},false);
