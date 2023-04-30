const DL_SELECTOR = 'js-draggable_list';
const DL_LIST_SELECTOR = `[${DL_SELECTOR}="list"]`;
const DL_ITEM_SELECTOR = 'li';

const CSS = `
${DL_ITEM_SELECTOR}[draggable="true"] {
  background: rgba(0,0,0,0.02);
  border: 1px solid rgba(0,0,0,0.02);
}
${DL_ITEM_SELECTOR}[draggable="true"]:hover {
  background: rgba(0,0,0,0.02);
  border: 1px solid rgba(0,0,0,0.05);
}
[data-dragging="true"] {
  opacity: 0.5;
  border: 1px dotted red!important;
}
[data-appended="true"] {
  border: 2px dotted green!important;
}
.test-container {
  display: block;
  padding: 20px 0;
  border: 3px solid red;
}
`;

function addStyle (css, attr) {
  const style = document.createElement('style');
  style.setAttribute(`${DL_SELECTOR}-${attr}`, '');
  style.textContent = css;
  document.head.append(style);
}

addStyle (CSS, 'style');

// event.dataTransfer.setData("text/plain", event.target.id);
// event.dataTransfer.getData("text/plain");
// Log all the transferred data items to the console.
// for (let type of event.dataTransfer.types) {
//   console.log({ type, data: event.dataTransfer.getData(type) });
// }
let dragItem = null;

function dragStart(event) {
  console.log('drag started');
  // e.preventDefault();
  // to prevent from activating on the parents:
  event.stopPropagation();
  dragItem = this;
  setTimeout(() => {
    // this.className = 'invisible';
    this.dataset.dragging = true;
    // this.style.cursor = 'move';
  }, 0);
}
function dragEnd(event) {
  console.log('drag ended', event.target);
  this.dataset.dragging = false;
  dragItem = null;
}

function dragOver(event) {
  event.preventDefault();
}
function dragEnter() {
  console.log('drag entered');
}
function dragLeave() {
  console.log('drag left');
}
function dragDrop(event) {
  event.preventDefault();
  console.log('drag dropped', this);
  this.append(dragItem);
  dragItem.dataset.appended = 'true';
}

function addTestContainer(element) {
  const testContainer = document.createElement('div');
  testContainer.className = 'test-container';
  element.append(testContainer);
  return testContainer
}

window.addEventListener('load', function () {
  const draggable = document.querySelector(`[${DL_SELECTOR}]`);
  console.log('draggable list is here', draggable);

  // Prevent drag for links inside the list
  [...draggable.querySelectorAll('a')].forEach((item) => {
    item.setAttribute('draggable', false);
  })

  const draggableList = [...draggable.querySelectorAll(DL_ITEM_SELECTOR)];
  console.log('draggableList', draggableList);

  draggableList.forEach((item) => {
    item.setAttribute('draggable', true);

    item.addEventListener('dragstart', dragStart)
    item.addEventListener('dragend', dragEnd)
  })

  const testContainer = addTestContainer(draggable);
  testContainer.addEventListener('dragover', dragOver);
  testContainer.addEventListener('dragenter', dragEnter);
  testContainer.addEventListener('dragleave', dragLeave);
  testContainer.addEventListener('drop', dragDrop);

})
