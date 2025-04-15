(() => {

  const DL_SELECTOR = 'js-draggable_list';
  const DL_ITEM_SELECTOR = 'li';
  const DL_ZONE_CHILD = 32;

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
  position: absolute;
  left: 0; right: 0;
  z-index: 2;
}
.dropIndicator::before {
  position: absolute;
  content: '';
  top: -2px;
  left: 0; right: 0;
  height: 4px;
  background: rgb(242,100,42);
  opacity: 0.3;
  pointer-events: none;
}
.dropIndicator::after {
  position: absolute;
  content: '';
  top: -2px;
  height: 4px;
  width: 100%;
  background: rgb(242,100,42);
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

  const dragState = {
    item: null,
    reference: null,
    option: null,
  }

  function resetDragState() {
    dragState.item = null;
    dragState.reference = null;
    dragState.option = null;
  }

  function setDragItem(item) {
    dragState.item = item;
  }
  function setDropReference(reference) {
    dragState.reference = reference;
  }
  function setDropOption(option) {
    dragState.option = option;
  }

  const dropIndicator = createDropIndicator();
  const dragIndicator = createDragIndicator();

  class DraggableList extends Stimulus.Controller {
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
  }

  Stimulus.application.register("draggable_list", DraggableList);

  function addStyle(target, css, attr = 'style') {
    const style = document.createElement('style');
    style.setAttribute(`${DL_SELECTOR}-${attr}`, '');
    style.textContent = css;
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

    setDragItem(this);

    setTimeout(() => {
      this.dataset.dragging = true;
    }, 0);
  }

  function dragEnd(event) {
    updateDropIndication();
    resetDragState();
    this.dataset.dragging = false;
  }

  function updateDropIndication(target, option) {
    setDropOption(option);
    switch (option) {
      case 'child':
        target.append(dropIndicator);
        dropIndicator.style.paddingLeft = `${DL_ZONE_CHILD}px`;
        dropIndicator.style.top = '';
        dropIndicator.style.bottom = 0;
        break;
      case 'after':
        target.append(dropIndicator);
        dropIndicator.style.paddingLeft = '';
        dropIndicator.style.top = '';
        dropIndicator.style.bottom = 0;
        break;
      case 'before':
        target.append(dropIndicator);
        dropIndicator.style.paddingLeft = '';
        dropIndicator.style.top = 0;
        dropIndicator.style.bottom = '';
        break;
      default:
        // dropIndicator is declared in the global scope,
        // so this case works if there are no parameters:
        dropIndicator.remove();
    }
  }

  function isDropMatter() {
    return
  }

  function dragOver(event) {
    event.preventDefault();
    event.stopImmediatePropagation();
    event.dataTransfer.dropEffect = "move";

    setDropReference(this);

    // https://developer.mozilla.org/en-US/docs/Web/API/Node/contains
    // A node is contained inside itself,
    // so (dragState.item !== dragState.reference)
    // is the same as (dragState.item.contains(dragState.reference)).

    if (dragState.item.contains(dragState.reference)) {
      // We do not process the case when the item does not actually displace.
      updateDropIndication();
    } else {

      const bounding = this.getBoundingClientRect();

      // We do not process the case when the item
      // does not actually displace.

      if (event.clientY < bounding.top + (bounding.bottom - bounding.top) * 0.5) {
        // * BEFORE
        // The mouse is in the top half of the Reference.

        if (dragState.item.nextElementSibling === dragState.reference) {
          // We do not process the case when the item
          // does not actually displace.
          updateDropIndication();
        } else {
          updateDropIndication(this, 'before');
        }

      } else {
        // * AFTER
        // The mouse is in the bottom half of the Reference.
        // The dragged element can become a child or just the next one.

        if (event.clientX > bounding.left + DL_ZONE_CHILD) {
          // * AFTER / child
          // The mouse is shifted to the right of the boundary,
          // which indicates the intention to insert the item as a child.

          updateDropIndication(this, 'child');

        } else {
          // * AFTER / just the next item
          // The mouse is to the left of the DL_ZONE_CHILD boundary, which points
          // to the intention to insert just the next one in the list.

          if (dragState.item.previousElementSibling === dragState.reference) {
            // We do not process the case when the item
            // does not actually displace.
            updateDropIndication();
          } else {
            updateDropIndication(this, 'after');
          }
        }
      }
    }
  }

  function dragEnter() { }
  function dragLeave() { }

  function dragDrop(event) {
    event.preventDefault();
    event.stopImmediatePropagation();
    dragState.option && fetchDroppedItemData(dragState.item, dragState.reference, dragState.option);
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

  function fetchDroppedItemData(dragItem, dropReference, whereto) {
    console.assert(['before', 'after', 'child'].includes(whereto), 'whereto is', whereto)
    if (dragItem !== dropReference) {
      // Build formData object.
      let formData = new FormData();
      formData.append('moved_node_mid', dragItem.dataset.nodeid);
      formData.append('target_mid', dropReference.dataset.nodeid);
      formData.append('whereto', whereto);

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
    // The real insertion of the moved node is done by the server,
    // so this functionality is not implemented.
    //// dropReference.parentNode.insertBefore(dragItem, dropReference);
    //// dragItem.dataset.last_moved = 'true';
  }

})();
