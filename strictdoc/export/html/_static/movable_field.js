// One pair of delegated click listeners for every "move this field up/down"
// button. sdoc-form-row (components/form/row/index.jinja) is the element
// swapped.

(() => {

  // Swap any nodes, not siblings, not adjecent siblings, no temp nodes, no cloning, no jquery... IE9+
  // https://stackoverflow.com/a/44562952/598057
  function swapNodes(n1, n2) {
    if (!n1 || !n2) {
      return;
    }
    console.assert(
      n1 != n2,
      "swapNodes() only works on nodes that are not the same."
    );
    console.assert(
      n1.parentNode === n2.parentNode,
      "swapNodes() only works on nodes that have a parent."
    );
    const parentNode = n1.parentNode;

    let i1 = -1;
    for (let i = 0; i < parentNode.children.length; i++) {
      if (parentNode.children[i].isEqualNode(n1)) {
        i1 = i;
      }
    }
    let i2 = -1;
    for (let i = 0; i < parentNode.children.length; i++) {
      if (parentNode.children[i].isEqualNode(n2)) {
        i2 = i;
      }
    }

    if (i1 < i2) {
      parentNode.insertBefore(n2, n1);
    } else if (i1 > i2) {
      parentNode.insertBefore(n1, n2);
    } else {
      console.assert(false, "Must not reach here!");
    }
  }

  document.addEventListener('click', (event) => {
    const upBtn = event.target.closest?.('[data-js-move-up-field-action]');
    if (upBtn) {
      const row = upBtn.closest('sdoc-form-row');
      if (!row) return;
      event.preventDefault();
      swapNodes(row, row.previousElementSibling);
      return;
    }

    const downBtn = event.target.closest?.('[data-js-move-down-field-action]');
    if (downBtn) {
      const row = downBtn.closest('sdoc-form-row');
      if (!row) return;
      event.preventDefault();
      swapNodes(row, row.nextElementSibling);
    }
  });

})();
