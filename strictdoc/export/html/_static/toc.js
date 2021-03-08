let tocToggle;
let tocLayout;

let setTocState = sessionStorage.getItem('tocState');
sessionStorage.setItem('tocState', (setTocState ? setTocState : 'close'));

function switchTOC() {

  const currTocState = sessionStorage.getItem('tocState');

  if (currTocState == 'open') {
    tocToggle.dataset.state = 'close';
    tocLayout.dataset.state = 'close';

    sessionStorage.setItem('tocState', 'close');
  } else {
    tocToggle.dataset.state = 'open';
    tocLayout.dataset.state = 'open';

    sessionStorage.setItem('tocState', 'open');
  }
}

window.addEventListener("load", function (event) {

  tocToggle = document.getElementById('layout_toggle');
  tocLayout = document.getElementById('layout');

  const tocState = sessionStorage.getItem('tocState');
  tocToggle.dataset.state = tocState;
  tocLayout.dataset.state = tocState;

  tocToggle.addEventListener('click', () => {
    switchTOC();
  });
});