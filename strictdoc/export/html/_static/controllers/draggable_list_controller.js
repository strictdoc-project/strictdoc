import { Controller } from "/_static/stimulus.js";

const DL_SELECTOR = 'js-draggable_list';
const DL_ITEM_SELECTOR = 'li';

const CSS = `
${DL_ITEM_SELECTOR}[draggable="true"] {
}
${DL_ITEM_SELECTOR}[draggable="true"]:hover {
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
.dropIndicator {
  display: block;
  border: 2px solid blue;
  pointer-events: none;
}
.dragIndicator {
  position: absolute;
  top: 0; right: 0;
  transition: 0.3s;
}
${DL_ITEM_SELECTOR}[draggable="true"] .dragIndicator::before {
  position: absolute;
  width: 8px;
  height: 24px;
  top: 0; left: 100%;
  content: "⋮⋮";
}
[data-last_moved="true"] {
  position: relative;
}
[data-last_moved="true"]::after {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  pointer-events: none;
  animation-name: last_moved;
  animation-duration: 1s;
}
@keyframes last_moved {
  from {
    background: rgba(255,255,255,0.5);
  }
  to {
    background: rgba(255,255,255,0);
  }
}
[data-dragging="true"] {
  background: rgba(255,255,255,0.5) !important;
}

`;

let dragItem = null;
const dropIndicator = createDropIndicator();
const dragIndicator = createDragIndicator();

Stimulus.register("draggable_list", class extends Controller {
  static targets = ["name"];

  initialize() {
    // this.element.style.paddingRight = '10px';

    const last_moved_node_id = this.element.dataset.last_moved_node_id;

    addStyle(this.element, CSS, 'style');

    // Add event listeners.
    const draggableList = [...this.element.querySelectorAll(DL_ITEM_SELECTOR)];
    draggableList.forEach((item) => {
      item.addEventListener('dragstart', dragStart);
      item.addEventListener('dragend', dragEnd);
      item.addEventListener('dragover', dragOver);
      item.addEventListener('dragenter', dragEnter);
      item.addEventListener('dragleave', dragLeave);
      item.addEventListener('drop', dragDrop);

      item.addEventListener("mouseover", mouseOver);
      item.addEventListener("mouseleave", mouseLeave);

      last_moved_node_id
      && (item.dataset.nodeid === last_moved_node_id)
      && (item.dataset.last_moved = 'true');

      item.setAttribute('draggable', true);
    });

    // Prevent drag for links inside the list.
    [...this.element.querySelectorAll('a')].forEach((item) => {
      item.setAttribute('draggable', false);
    })
  }
})

function addStyle (target, css, attr = 'style') {
  const style = document.createElement('style');
  style.setAttribute(`${DL_SELECTOR}-${attr}`, '');
  style.textContent = css;
  // document.head.append(style);
  // target.prepend(style);
  target.parentNode.insertBefore(style, target);
}

function createDropIndicator() {
  const dropIndicator = document.createElement('div');
  dropIndicator.className = 'dropIndicator';
  return dropIndicator
}

function createDragIndicator() {
  const dragIndicator = document.createElement('div');
  dragIndicator.className = 'dragIndicator';
  return dragIndicator
}

function dragStart(event) {
  event.stopImmediatePropagation();
  event.dataTransfer.dropEffect = "move";
  event.dataTransfer.effectAllowed = 'move';

  dragItem = this;
  setTimeout(() => {
    this.dataset.dragging = true;
  }, 0);
}

function dragEnd(event) {
  dropIndicator.remove();
  dragItem = null;
  this.dataset.dragging = false;
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
  fetchDroppedItemData(dragItem, this);
}

function mouseOver(event) {
  event.preventDefault();
  event.stopImmediatePropagation();
  if (event.target === this) {
    event.target.append(dragIndicator);
  }
}
function mouseLeave(event) {
  event.preventDefault();
  event.stopImmediatePropagation();
  if (event.target === this) {
    dragIndicator.remove();
  }
}

function fetchDroppedItemData(dragItem, dropReference) {
  if (dragItem !== dropReference) {
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

function moveNodeBefore(dragItem, dropReference) {
  // dropReference.parentNode.insertBefore(dragItem, dropReference);
  // dragItem.dataset.last_moved = 'true';
}
