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
  cursor: -webkit-grab;
  cursor: -moz-grab;
  cursor: -o-grab;
  cursor: -ms-grab;
  cursor: grab;
}
${DL_ITEM_SELECTOR}[draggable="true"]:active {
  cursor: -webkit-grabbing;
  cursor: -moz-grabbing;
  cursor: -o-grabbing;
  cursor: -ms-grabbing;
  cursor: grabbing;
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
.dropIndicator {
  display: block;
  border: 2px solid blue;
  pointer-events: none;
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

function createDropIndicator() {
  const dropIndicator = document.createElement('div');
  dropIndicator.className = 'dropIndicator';
  return dropIndicator
}
const dropIndicator = createDropIndicator();

function dragStart(event) {
  event.stopImmediatePropagation();
  dragItem = this;
  setTimeout(() => {
    this.dataset.dragging = true;
  }, 0);
  event.dataTransfer.dropEffect = "move";
  event.dataTransfer.effectAllowed = 'move';
  // event.dataTransfer.setData('text/html', dragItem.dataset.nodeid);
}
function dragEnd(event) {
  this.dataset.dragging = false;
  dragItem = null;
  dropIndicator.remove();
}

function dragOver(event) {
  event.preventDefault();
  event.stopImmediatePropagation();
  this.parentNode.insertBefore(dropIndicator, this);
  event.dataTransfer.dropEffect = "move";
}

function dragEnter() {}
function dragLeave() {}

function dragDrop(event) {
  event.preventDefault();
  event.stopImmediatePropagation();

  const dropReference = this;

  if (dragItem !== dropReference) {
    // dropReference.parentNode.insertBefore(dragItem, dropReference);
    // dragItem.dataset.appended = 'true';

    // const aaa = event.dataTransfer.getData('text/html');
    console.log('drag dropped', dropReference);
    // this.innerHTML = e.dataTransfer.getData('text/html');
    // console.log('drag dropped', aaa);
    console.log('--- NEW PLACE ---');

    // Build formData object.
    let formData = new FormData();
    formData.append('moved_node_mid', dragItem.dataset.nodeid);
    formData.append('target_mid', dropReference.dataset.nodeid);
    formData.append('whereto', 'before');

    fetch("/actions/document/move_node",
    {
        body: formData,
        method: "post",
        headers: {
          "Accept": "text/vnd.turbo-stream.html",
      },
    }).then(r => r.text())
    .then(html => Turbo.renderStreamMessage(html));




  }
}

window.addEventListener('load', function () {
  const draggable = document.querySelector(`[${DL_SELECTOR}]`);

  // Prevent drag for links inside the list
  [...draggable.querySelectorAll('a')].forEach((item) => {
    item.setAttribute('draggable', false);
  })

  const draggableList = [...draggable.querySelectorAll(DL_ITEM_SELECTOR)];

  draggableList.forEach((item) => {
    item.setAttribute('draggable', true);

    item.addEventListener('dragstart', dragStart);
    item.addEventListener('dragend', dragEnd);
    item.addEventListener('dragover', dragOver);
    item.addEventListener('dragenter', dragEnter);
    item.addEventListener('dragleave', dragLeave);
    item.addEventListener('drop', dragDrop);
  })

})
