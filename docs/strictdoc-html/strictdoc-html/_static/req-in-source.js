
// TODO
// 2
// сделать article relative
// и считать общую позицию ссылки, складывая позицию карточки и ссылки внутри карточки

// 3
// ДВОЙНЫЕ СТРОКИ?
// считать не высоте строки а на текущей позиции первой строки ренджа

// 4
// что если карточек много и прокрутка левой части?

// init:
const topSourceScrollLimit = 200;
let bottomSourceScrollLimit; // TODO update on window resize
let mainContainer;
let referContainer;
let sourceContainer;
let sourceContainerHeight; // TODO update on window resize
let sourceBlock;
let sourceBlockHeight; // TODO update on window resize
let translateSourceBlockTo;
let stringHeight = 24;
let highlightBlock;
let requirements = [];
let requirementsPositions = {};
let pointers = [];
let pointersPositions = {};

function prepareDOMElements() {
  // get Containers
  mainContainer = document.getElementById('mainContainer');
  referContainer = document.getElementById('referContainer');
  sourceContainer = document.getElementById('sourceContainer');
  // get sourceBlock
  sourceBlock = document.getElementById('source');
  // get highlightBlock
  highlightBlock = sourceBlock.querySelector('.source_highlight');

  // get requirements NodeList; convert it to array:
  requirements = [...document.querySelectorAll('.requirement')];
  // get pointers NodeList; convert it to array:
  pointers = [...document.querySelectorAll('.pointer')];

  // add MouseWheelHandler
  sourceContainer.addEventListener("wheel", MouseWheelHandler);
}

function getParamsFromDOMElements() {
  // get current parameters
  sourceContainerHeight = sourceContainer.offsetHeight;
  sourceBlockHeight = sourceBlock.offsetHeight;
  bottomSourceScrollLimit = sourceContainerHeight - sourceBlockHeight - topSourceScrollLimit;
}

function preparePointersPositions() {
  requirements.map((element) => {
    // set requirementsPositions
    requirementsPositions = {
      ...requirementsPositions,
      // ID format of DOM element is 'requirement:ID'
      [element.id]: element.offsetTop
    };
  })

  pointers.map((element) => {
    // set pointersPositions
    pointersPositions = {
      ...pointersPositions,
      // ID format of DOM element is 'pointer:ID'
      [element.id]: element.offsetTop
    };
    // add addEventListener on click
    element.addEventListener("click",
      function () {
        // ID format of DOM element is 'pointer:ID'
        toggleRequirement(this.id);
      }
    );
  })
}

function MouseWheelHandler(e) {
  // reset sourceContainer scroll limit indicator
  sourceContainer.classList.remove('limit-top');
  sourceContainer.classList.remove('limit-bottom');

  const delta = e.deltaY;

  const isScrollBottom = delta < 0;
  // console.log('delta: ', delta);

  const style = window.getComputedStyle(sourceBlock);
  const matrix = new WebKitCSSMatrix(style.transform);
  const currTranslate = Math.round(matrix.m42);
  let nextTranslate = Math.round(currTranslate - delta);

  if (isScrollBottom && currTranslate > topSourceScrollLimit) {
    nextTranslate = currTranslate;
    sourceContainer.classList.add('limit-top');
  }

  if (!isScrollBottom && currTranslate < bottomSourceScrollLimit) {
    nextTranslate = currTranslate;;
    sourceContainer.classList.add('limit-bottom');
  }

  sourceBlock.style.transform = 'translateY(' + nextTranslate + 'px)';
  return false;
}

function toggleRequirement(pointerID) {

  // prepare params
  if (!pointerID) {
    // get params from URL:
    pointerID = `pointer:${window.location.hash.substring(1)}`;
  }
  // ['pointer', hashId, rangeStart, rangeEnd]:
  [_, hashId, rangeStart, rangeEnd] = pointerID.split(':');

  // toggle active requirement
  requirements.map((element) => {
    element.classList.remove('active');
    // ID format of DOM element is 'requirement:ID'
    if (element.id === `requirement:${hashId}`) {
      element.classList.add('active');
    }
  })

  // toggle active pointer
  pointers.map((element) => {
    element.classList.remove('active');
    // ID format of DOM element is 'pointer:ID'
    if (element.id === pointerID) {
      element.classList.add('active');
    }
  })

  // prepare variables for translate
  const rangeSize = (rangeEnd - rangeStart + 1) || 0;
  const rangeAmend = (rangeStart - 1) * stringHeight || 0;

  translateSourceBlockTo = pointersPositions[pointerID] - rangeAmend;

  // translate
  sourceBlock.style.transform = 'translateY(' + translateSourceBlockTo + 'px)';
  highlightBlock.style.top = rangeAmend + 'px';
  highlightBlock.style.height = rangeSize * stringHeight + 'px';
  // reset sourceContainer scroll limit indicator
  sourceContainer.classList.remove('limit-top');
  sourceContainer.classList.remove('limit-bottom');
}

// update params on window resize
var resizeTimeout;
function resizeThrottler() {
  // ignore resize events as long as an resizeHandler execution is in the queue
  if (!resizeTimeout) {
    resizeTimeout = setTimeout(function () {
      resizeTimeout = null;
      resizeHandler();

      // The resizeHandler will execute at a rate of 15fps
    }, 66);
  }
}
function resizeHandler() {
  getParamsFromDOMElements();
}

// update params on scroll
let last_known_scroll_position = 0;
let ticking = false;
function referContainerScrollHandler(scroll_pos) {
  console.log(scroll_pos);
  sourceBlock.style.marginTop = `-${scroll_pos}px`;
}

// FIRE
window.onload = function () {

  // TODO relative pos = REQ pos - LINE pos
  stringHeight = document.getElementById('line-2').offsetTop;

  prepareDOMElements();
  getParamsFromDOMElements();
  preparePointersPositions();

  // for update params on scroll
  referContainer.addEventListener('scroll', function (e) {

    if (!ticking) {
      window.requestAnimationFrame(function () {
        referContainerScrollHandler(referContainer.scrollTop);
        ticking = false;
      });

      ticking = true;
    }
  });

  // for update params on window resize
  window.addEventListener("resize", resizeThrottler, false);

  // fire on load:
  toggleRequirement();

  console.log('pointers: ', pointers);
  console.log('requirementsPositions: ', requirementsPositions);
  console.log('pointersPositions: ', pointersPositions);

};
