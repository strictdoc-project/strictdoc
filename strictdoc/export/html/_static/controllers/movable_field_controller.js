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
  var parentNode = n1.parentNode;

  var i1 = -1;
  for (var i = 0; i < parentNode.children.length; i++) {
    if (parentNode.children[i].isEqualNode(n1)) {
      i1 = i;
    }
  }
  var i2 = -1;
  for (var i = 0; i < parentNode.children.length; i++) {
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

Stimulus.register("movable_field", class extends Controller {
  initialize() {
    // this.element is the DOM element to which the controller is connected to.
    const thisElement = this.element;

    const moveUpLinks = thisElement.querySelectorAll("[data-js-move-up-field-action]");
      moveUpLinks.forEach(link => {
        link.addEventListener("click", function(event){
            event.preventDefault();
            swapNodes(thisElement, thisElement.previousElementSibling);
        });
    });

    const moveDownLinks = thisElement.querySelectorAll("[data-js-move-down-field-action]");
      moveDownLinks.forEach(link => {
        link.addEventListener("click", function(event){
          event.preventDefault();
          swapNodes(thisElement, thisElement.nextElementSibling);
        });
    });
  }
});
