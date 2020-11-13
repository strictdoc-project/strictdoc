
let tocToggle;
let tocLayout;

function switchTOC(currState) {

  if(currState == 'open') {

    tocToggle.dataset.state = 'close';
    tocLayout.dataset.state = 'close';
    console.log('layout: ' + tocLayout.dataset.state);
    console.log('toggle: ' + tocToggle.dataset.state);

  } else {

    tocToggle.dataset.state = 'open';
    tocLayout.dataset.state = 'open';
    console.log('layout: ' + tocLayout.dataset.state);
    console.log('toggle: ' + tocToggle.dataset.state);

  }
}

window.onload = function() {

  // tocToggle = document.getElementById('toc_toggle');
  // tocLayout = document.getElementById('toc_layout');

  tocToggle = document.getElementById('layout_toggle');
  tocLayout = document.getElementById('layout');

  tocToggle.dataset.state = 'open';
  tocLayout.dataset.state = 'open';

  tocToggle.addEventListener('click', () => {
    switchTOC(tocToggle.dataset.state);
  });

};