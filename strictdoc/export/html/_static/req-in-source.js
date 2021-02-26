
// TODO
// 1
// сделать для рекв ID
// а для ссылки без параметров какой-то свой, например 'REQ:'
// и делать активной карточку каким-то образом
// 2
// сделать article relative
// и считать общую позицию ссылки, складывая позицию карточки и ссылки внутри карточки

// init:
let sourceBlock;
let highlightBlock;
let targetsPositions = {};
let stringHeight = 24;

window.onload = function () {

  // console.log('pathname: ', window.location.pathname);
  // console.log('hash: ', window.location.hash);

  // TODO relative pos = REQ pos - LINE pos
  stringHeight = document.getElementById('line-2').offsetTop;

  // get sourceBlock
  sourceBlock = document.getElementById('source');
  // get highlightBlock
  highlightBlock = sourceBlock.querySelector('.source_highlight');
  console.log(highlightBlock);

  // get targetsPositions
  const requirementTogglers = document.querySelectorAll('.requirementToggler');

  for (var link of requirementTogglers) {
    const id = link.id;
    const x = link.offsetTop;

    // console.log(id);
    // console.log(x);

    targetsPositions = {
      ...targetsPositions,
      [id]: x
    };
  }

  // fire on load:
  toggleRequirement();

};

function toggleRequirement(reqId, rangeStart, rangeEnd) {

  if (!reqId) {
    // get params from URL:
    [reqId, rangeStart, rangeEnd] = window.location.hash.substring(1).split(':');
  }

  const targetId =
    rangeStart
      ? (
        rangeEnd
          ? reqId + ':' + rangeStart + ':' + rangeEnd
          : reqId + ':' + rangeStart
      )
      : reqId;

  const rangeSize = (rangeEnd - rangeStart + 1) || 0;
  const rangeAmend = (rangeStart - 1) * stringHeight || 0;

  const translateTo = targetsPositions[targetId] - rangeAmend;

  sourceBlock.style.transform = 'translateY(' + translateTo + 'px)';
  highlightBlock.style.top = rangeAmend + 'px';
  highlightBlock.style.height = rangeSize * stringHeight + 'px';
}




// console.log(`
// targetId: ${targetId},
// reqId: ${reqId},
// rangeStart: ${rangeStart},
// rangeEnd: ${rangeEnd}
//   `)
