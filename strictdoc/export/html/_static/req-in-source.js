let sourceBlock;
let requirementsPos = {};

function toggleRequirement(id) {
  const reqId = id || window.location.hash.substring(1);
  sourceBlock.style.transform = 'translateY(' + requirementsPos[reqId] + 'px)';
}

window.onload = function () {

  // console.log('pathname: ', window.location.pathname);
  // console.log('hash: ', window.location.hash);

  // TODO relative pos = REQ pos - LINE pos
  console.log(document.getElementById('line-1').offsetTop);

  // get sourceBlock
  sourceBlock = document.getElementById('source');

  // get requirementsPos
  const requirements = document.querySelectorAll('article.requirement');

  for (var req of requirements) {
    const id = req.id;
    const x = req.offsetTop;
    requirementsPos = {
      ...requirementsPos,
      [id]: x
    };
  }

  toggleRequirement();

};