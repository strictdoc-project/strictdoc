// Drag-and-drop placement for genuinely-new (auto-merged, non-conflicting)
// nodes on the Git conflicts screen -- SDOC-SRS-215 sub-scenario 2.
//
// Native HTML5 drag-and-drop only: a node made draggable="true" by the
// server (conflict_node.jinja, left/incoming column only) is dragged onto
// one of the drop zones rendered in the right/target column
// (conflicts_main.jinja, one before each parent's first child and one
// after every node). On drop, the single hidden #git-conflicts-place-node
// form is filled in and submitted -- a normal full-page POST-redirect-GET,
// matching every other action on this screen (no fetch/AJAX).

(() => {
  const SEL_DRAGGABLE = '[data-testid="git-conflicts-node"][draggable="true"]';
  const SEL_DROP_ZONE = '[data-testid="git-conflicts-drop-zone"]';
  const SEL_FORM = '[data-testid="git-conflicts-place-node-form"]';
  const ACTIVE_CLASS = 'git_conflicts_drop_zone--active';

  let draggedKey = null;

  document.addEventListener('dragstart', (event) => {
    const node = event.target.closest(SEL_DRAGGABLE);
    if (!node) {
      return;
    }
    draggedKey = node.getAttribute('data-node-key');
    if (event.dataTransfer) {
      event.dataTransfer.effectAllowed = 'move';
      event.dataTransfer.setData('text/plain', draggedKey || '');
    }
  });

  document.addEventListener('dragover', (event) => {
    if (draggedKey === null) {
      return;
    }
    const zone = event.target.closest(SEL_DROP_ZONE);
    if (!zone) {
      return;
    }
    event.preventDefault();
    zone.classList.add(ACTIVE_CLASS);
  });

  document.addEventListener('dragleave', (event) => {
    const zone = event.target.closest(SEL_DROP_ZONE);
    if (!zone) {
      return;
    }
    zone.classList.remove(ACTIVE_CLASS);
  });

  document.addEventListener('drop', (event) => {
    const zone = event.target.closest(SEL_DROP_ZONE);
    if (!zone || draggedKey === null) {
      return;
    }
    event.preventDefault();
    zone.classList.remove(ACTIVE_CLASS);

    const form = document.querySelector(SEL_FORM);
    if (!form) {
      return;
    }
    form.querySelector('[name="node_key"]').value = draggedKey;
    form.querySelector('[name="after_key"]').value =
      zone.getAttribute('data-after-key') || '';
    draggedKey = null;
    form.submit();
  });

  document.addEventListener('dragend', () => {
    draggedKey = null;
    document
      .querySelectorAll(`${SEL_DROP_ZONE}.${ACTIVE_CLASS}`)
      .forEach((zone) => zone.classList.remove(ACTIVE_CLASS));
  });
})();
