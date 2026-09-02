// HTML5 drag-and-drop for the TOC list. There is only ever one such list on
// a page, so dragState/dropIndicator/dragIndicator below are page-wide
// singletons.
//
// Each <li> gets its listeners wired directly (not through a delegated
// document listener) via StrictDoc.onInsert('[data-js-draggable-list] li',
// ...) - this fires once per <li>, both for the initial page render and for
// every fresh <li> that appears after a move (the server's response
// replaces the whole list's content via a Turbo Stream "update", so every
// <li> after a move is a newly-inserted node). Kept as direct per-item
// listeners, not full document delegation, because mouseleave does not
// bubble - delegating it would need capture-phase tricks for no real
// benefit here, since this control only ever has one list on the page.

(() => {

  const SEL_LIST = '[data-js-draggable-list]';
  const SEL_ITEM = 'li';
  const ZONE_CHILD_PX = 32;

  const CSS = `
${SEL_ITEM}[draggable="true"]:hover {
  cursor: -webkit-grab;
  cursor: -moz-grab;
  cursor: -o-grab;
  cursor: -ms-grab;
  cursor: grab;
}
${SEL_ITEM}[draggable="true"]:active {
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
${SEL_ITEM}[draggable="true"] .dragIndicator::before {
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

  // Injected once into <head> - the ruleset doesn't depend on any specific
  // render of the list, so there's no need to redo it on every re-render.
  const style = document.createElement('style');
  style.setAttribute('data-js-draggable-list-style', '');
  style.textContent = CSS;
  document.head.append(style);

  const dragState = {
    item: null,
    reference: null,
    option: null,
  };

  function resetDragState() {
    dragState.item = null;
    dragState.reference = null;
    dragState.option = null;
  }

  const dropIndicator = document.createElement('div');
  dropIndicator.className = 'dropIndicator';

  const dragIndicator = document.createElement('div');
  dragIndicator.className = 'dragIndicator';

  function updateDropIndication(target, option) {
    dragState.option = option;
    switch (option) {
      case 'child':
        target.append(dropIndicator);
        dropIndicator.style.paddingLeft = `${ZONE_CHILD_PX}px`;
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
        // dropIndicator is a page-wide singleton, so this also works when
        // called with no target/option.
        dropIndicator.remove();
    }
  }

  function dragStart(event) {
    event.stopImmediatePropagation();
    event.dataTransfer.dropEffect = 'move';
    event.dataTransfer.effectAllowed = 'move';

    dragState.item = this;

    setTimeout(() => {
      this.dataset.dragging = true;
    }, 0);
  }

  function dragEnd() {
    updateDropIndication();
    resetDragState();
    this.dataset.dragging = false;
  }

  function dragOver(event) {
    event.preventDefault();
    event.stopImmediatePropagation();
    event.dataTransfer.dropEffect = 'move';

    dragState.reference = this;

    // https://developer.mozilla.org/en-US/docs/Web/API/Node/contains
    // A node is contained inside itself, so
    // (dragState.item !== dragState.reference) is the same as
    // (dragState.item.contains(dragState.reference)).
    if (dragState.item.contains(dragState.reference)) {
      // We do not process the case when the item does not actually displace.
      updateDropIndication();
      return;
    }

    const bounding = this.getBoundingClientRect();

    if (event.clientY < bounding.top + (bounding.bottom - bounding.top) * 0.5) {
      // * BEFORE
      // The mouse is in the top half of the reference.
      if (dragState.item.nextElementSibling === dragState.reference) {
        // We do not process the case when the item does not actually displace.
        updateDropIndication();
      } else {
        updateDropIndication(this, 'before');
      }
    } else {
      // * AFTER
      // The mouse is in the bottom half of the reference.
      // The dragged element can become a child or just the next one.
      if (event.clientX > bounding.left + ZONE_CHILD_PX) {
        // * AFTER / child
        updateDropIndication(this, 'child');
      } else if (dragState.item.previousElementSibling === dragState.reference) {
        // We do not process the case when the item does not actually displace.
        updateDropIndication();
      } else {
        // * AFTER / just the next item
        updateDropIndication(this, 'after');
      }
    }
  }

  function dragDrop(event) {
    event.preventDefault();
    event.stopImmediatePropagation();
    dragState.option && fetchDroppedItemData(dragState.item, dragState.reference, dragState
      .option);
  }

  function mouseOver(event) {
    event.preventDefault();
    event.stopImmediatePropagation();
    if (event.target === this) {
      this.append(dragIndicator);
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
    console.assert(['before', 'after', 'child'].includes(whereto), 'whereto is', whereto);
    if (dragItem === dropReference) return;

    const formData = new FormData();
    formData.append('moved_node_mid', dragItem.dataset.nodeid);
    formData.append('target_mid', dropReference.dataset.nodeid);
    formData.append('whereto', whereto);

    fetch('/actions/document/move_node', {
        body: formData,
        method: 'post',
        headers: {
          'Accept': 'text/vnd.turbo-stream.html',
        },
      }).then((r) => r.text())
      .then((html) => Turbo.renderStreamMessage(html));
  }

  // [data-nodeid] excludes non-node <li>s that other scripts insert into
  // the same list later (e.g. collapsible_toc.js's bulk expand/collapse
  // controls panel, added on window "load" - after this list's items are
  // already wired). Those aren't real TOC entries and must not become
  // draggable.
  window.StrictDoc.onInsert(`${SEL_LIST} ${SEL_ITEM}[data-nodeid]`, (item) => {
    item.addEventListener('dragstart', dragStart);
    item.addEventListener('dragend', dragEnd);
    item.addEventListener('dragover', dragOver);
    item.addEventListener('drop', dragDrop);
    item.addEventListener('mouseover', mouseOver);
    item.addEventListener('mouseleave', mouseLeave);

    // Note: last_moved_node_id/last_moved use underscores, not hyphens, so
    // they are NOT camelCased by the browser's dataset API - matched here
    // exactly as the attribute names read in the DOM.
    const lastMovedNodeId = item.closest(SEL_LIST)?.dataset.last_moved_node_id;
    if (lastMovedNodeId && item.dataset.nodeid === lastMovedNodeId) {
      item.dataset.last_moved = 'true';
    }

    item.setAttribute('draggable', true);

    // Prevent drag for links inside the item.
    item.querySelectorAll('a').forEach((a) => a.setAttribute('draggable', false));
  });

})();
