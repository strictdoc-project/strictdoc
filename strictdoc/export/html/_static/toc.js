
let tocToggle;
let tocLayout;

let setTocState = sessionStorage.getItem('tocState');
sessionStorage.setItem('tocState', (setTocState ? setTocState : 'close'));

function switchTOC() {

  const currTocState = sessionStorage.getItem('tocState');

  console.log('switchTOC 1: ', sessionStorage.getItem('tocState'));

  if (currTocState == 'open') {
    tocToggle.dataset.state = 'close';
    tocLayout.dataset.state = 'close';
    console.log('layout: ' + tocLayout.dataset.state);
    console.log('toggle: ' + tocToggle.dataset.state);

    sessionStorage.setItem('tocState', 'close');
  } else {
    tocToggle.dataset.state = 'open';
    tocLayout.dataset.state = 'open';
    console.log('layout: ' + tocLayout.dataset.state);
    console.log('toggle: ' + tocToggle.dataset.state);

    sessionStorage.setItem('tocState', 'open');
  }

  console.log('switchTOC 2: ', sessionStorage.getItem('tocState'));
}

window.onload = function () {

  console.log('onload 1: ', sessionStorage.getItem('tocState'));

  tocToggle = document.getElementById('layout_toggle');
  tocLayout = document.getElementById('layout');

  const tocState = sessionStorage.getItem('tocState');
  tocToggle.dataset.state = tocState;
  tocLayout.dataset.state = tocState;

  tocToggle.addEventListener('click', () => {
    switchTOC();
  });

  console.log('onload 2: ', sessionStorage.getItem('tocState'));

};