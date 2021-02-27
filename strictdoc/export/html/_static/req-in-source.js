
// TODO
// 2
// сделать article relative
// и считать общую позицию ссылки, складывая позицию карточки и ссылки внутри карточки

// init:
let sourceBlock;
let highlightBlock;
let requirements = [];
let requirementsPositions = {};
let pointers = [];
let pointersPositions = {};
let stringHeight = 24;

window.onload = function () {

  // TODO relative pos = REQ pos - LINE pos
  stringHeight = document.getElementById('line-2').offsetTop;

  // get sourceBlock
  sourceBlock = document.getElementById('source');
  // get highlightBlock
  highlightBlock = sourceBlock.querySelector('.source_highlight');

  // get requirements NodeList; convert it to array:
  requirements = [...document.querySelectorAll('.requirement')];
  // get pointers NodeList; convert it to array:
  pointers = [...document.querySelectorAll('.pointer')];

  requirements.map((element) => {
    // ID format of DOM element is 'requirement:ID'
    const id = element.id.split(':')[1];
    // set requirementsPositions
    requirementsPositions = {
      ...requirementsPositions,
      [id]: element.offsetTop
    };
  })

  pointers.map((element) => {
    // set pointersPositions
    pointersPositions = {
      ...pointersPositions,
      [element.id]: element.offsetTop
    };
    // add addEventListener on click
    element.addEventListener("click",
      function () {
        toggleRequirement(this.id);
      }
    );
  })

  console.log('pointers: ', pointers);
  console.log('requirementsPositions: ', requirementsPositions);
  console.log('pointersPositions: ', pointersPositions);

  // fire on load:
  toggleRequirement();

};

function toggleRequirement(pointerID) {

  // prepare params
  if (!pointerID) {
    // get params from URL:
    pointerID = window.location.hash.substring(1);
  }
  [reqId, rangeStart, rangeEnd] = pointerID.split(':');

  // toggle active requirement
  requirements.map((element) => {
    element.classList.remove('active');
    // ID format of DOM element is 'requirement:ID'
    if (element.id === `requirement:${reqId}`) {
      element.classList.add('active');
    }
  })

  // toggle active pointer
  pointers.map((element) => {
    element.classList.remove('active');
    if (element.id === pointerID) {
      element.classList.add('active');
    }
  })

  // prepare variables for translate
  const rangeSize = (rangeEnd - rangeStart + 1) || 0;
  const rangeAmend = (rangeStart - 1) * stringHeight || 0;
  const translateTo = pointersPositions[pointerID] - rangeAmend;
  // translate
  sourceBlock.style.transform = 'translateY(' + translateTo + 'px)';
  highlightBlock.style.top = rangeAmend + 'px';
  highlightBlock.style.height = rangeSize * stringHeight + 'px';
}
