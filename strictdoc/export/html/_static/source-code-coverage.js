

console.log('%c coverage ', 'background:yellow;color:black');

const __log = (...payload) => {
  console.log('%c cov ', 'background:yellow;color:black',
    ...payload
  );
}

// CONSTANTS
const hashSplitter = '#';
const lineIdPattern = 'line-';
// COLORS
const rangeVisibleBG = 'rgba(75,255,0,0.2)';
const rangeInvisibleBG = 'rgba(75,255,0,0)';
const rangeHighlighterBG = 'rgba(255,255,155,1)';


// DOM
const dom = {
  ranges: null,
  requirements: null,
  highlighter: null,
};

const getHighlighterFromDom = () => dom.highlighter;
const getRequirementFromDom = (reqid) => dom.requirements[reqid];
const getRangeFromDom = (rangeBegin, rangeEnd) => dom.ranges[rangeAlias(rangeBegin, rangeEnd)].element;
const getPointersFromDom = (rangeBegin, rangeEnd) => Object.values(dom.ranges[rangeAlias(rangeBegin, rangeEnd)].pointers);

// STATE
const state = {
  range: null,
  requirement: null,
  pointers: null,
};

const changeState = ({
  range,
  requirement,
  pointers,
}) => {

  // remove old 'active'
  state.requirement?.classList.remove('active');
  state.pointers?.forEach(pointer => pointer?.classList.remove('active'));

  // make changes to state
  state.range = range;
  state.requirement = requirement;
  state.pointers = pointers;

  // add new 'active'
  state.requirement.classList.add('active');
  state.pointers.forEach(pointer => pointer.classList.add('active'));

  // nake changes to dom (highlight and scroll)
  moveElement(getHighlighterFromDom(), state.range.offsetTop, state.range.offsetHeight);
  state.range.scrollIntoView({ block: "center", behavior: "smooth" });

};

function usePointer(pointer) {

  const rangeBegin = pointer.dataset.begin;
  const rangeEnd = pointer.dataset.end;
  const reqid = pointer.dataset.reqid;

  changeState({
    range: getRangeFromDom(rangeBegin, rangeEnd),
    requirement: getRequirementFromDom(reqid),
    pointers: getPointersFromDom(rangeBegin, rangeEnd),
  })
}

function useHash() {

  const [_, reqId, rangeBegin, rangeEnd] = window.location.hash.split(hashSplitter);

  changeState({
    range: getRangeFromDom(rangeBegin, rangeEnd),
    requirement: getRequirementFromDom(reqId),
    pointers: getPointersFromDom(rangeBegin, rangeEnd),
  })
}

const rangeAlias = (begin, end) => `${begin}:${end}`;

function createCoverageToggler(dom) {
  const element = document.getElementById('sorceCodeCoverageToggler');
  element.addEventListener('change', function () {
    toggleRangesVisibility(dom.ranges, element.checked);
  })
  element.checked = true;
  return element
}

function toggleRangesVisibility(ranges, toggler) {
  for (key in ranges) {
    ranges[key].element.style.background = toggler ? rangeVisibleBG : rangeInvisibleBG;
  }
}

function prepareSourceBlock() {
  const element = document.getElementById('source');
  element.style.position = 'relative';
  element.style.zIndex = '1';
  return element
}

function createRangeHighlighter() {
  const element = document.createElement('div');
  element.style.position = 'absolute';
  element.style.left = '0';
  element.style.right = '0';
  element.style.background = rangeHighlighterBG;
  element.style.zIndex = '-1';
  element.style.transition = 'height 0.3s ease-in, top 0.3s ease-in';
  return element
}

function moveElement(element, top, height) {
  element.style.top = top + 'px';
  element.style.height = height + 'px';
}

function createRangeElement(begin, end, container) {
  const rangeElement = document.createElement('div');
  const beginLine = document.getElementById(`${lineIdPattern}${begin}`);
  const endLine = document.getElementById(`${lineIdPattern}${end}`);
  const top = beginLine.offsetTop;
  const height = endLine.offsetTop + endLine.offsetHeight - top;

  rangeElement.style.position = 'absolute';
  rangeElement.style.zIndex = '-1';
  rangeElement.style.left = '0px';
  rangeElement.style.right = '0px';
  rangeElement.style.top = top + 'px';
  rangeElement.style.height = height + 'px';
  rangeElement.style.transition = 'background 0.15s ease-in';
  rangeElement.style.background = rangeVisibleBG;

  container.prepend(rangeElement);
  return rangeElement;
}

// prepare DOM elements
function prepareDOMElements(dom) {


  const source = prepareSourceBlock();
  const rangeHighlighter = createRangeHighlighter();
  dom.highlighter = rangeHighlighter;
  source.prepend(rangeHighlighter);

  const requirementsList = [...document.querySelectorAll('.requirement')];
  const pointersList = [...document.querySelectorAll('.pointer')];

  dom.requirements = requirementsList
    .reduce((acc, requirement) => {
      acc[requirement.dataset.reqid] = requirement;
      return acc
    }, {});

  // dom.pointers = pointersList
  // .

  dom.ranges = pointersList
    .reduce((acc, pointer) => {
      const rangeBegin = pointer.dataset.begin;
      const rangeEnd = pointer.dataset.end;

      const range = rangeAlias(rangeBegin, rangeEnd);
      acc[range] = {
        ...acc[range],
        pointers: {
          ...acc[range]?.pointers,
          [pointer.dataset.reqid]: pointer
        }
      };

      // add Event Listener
      pointer.addEventListener("click",
        function () {
          usePointer(pointer);
        }
      );
      // make elem
      !acc[range].element
        && (acc[range].element = createRangeElement(
          rangeBegin,
          rangeEnd,
          source
        ));

      return acc
    }, {});

  const coverageToggler = createCoverageToggler(dom);
  toggleRangesVisibility(dom.ranges, coverageToggler.checked);

}

window.addEventListener("load", function () {
  __log(
    window.location.hash
  )

  prepareDOMElements(dom);
  useHash();

  __log(
    'dom', dom
  )

});