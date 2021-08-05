
// **
// Place this code right after the opening BODY tag:

// <script>document.body.dataset.state = sessionStorage.getItem('tocState') || 'open';</script>

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
  document.body.dataset.state = sessionStorage.getItem('tocState');
}

window.onload = function () {
  document.body.dataset.state = sessionStorage.getItem('tocState');
  document.getElementById('layout_toggle').addEventListener('click', () => {
    switchTOC();
  });
};
