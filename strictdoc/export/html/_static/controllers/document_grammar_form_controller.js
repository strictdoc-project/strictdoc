import { Controller } from "/_static/stimulus.js";

// Swap any nodes, not siblings, not adjecent siblings, no temp nodes, no cloning, no jquery... IE9+
// https://stackoverflow.com/a/44562952/598057
function swapNodes(n1, n2) {
  if (!n2) {
    return;
  }
  var p1 = n1.parentNode;
  var p2 = n2.parentNode;
  var i1, i2;
  if (!p1 || !p2 || p1.isEqualNode(n2) || p2.isEqualNode(n1)) {
    return;
  };

  for (var i = 0; i < p1.children.length; i++) {
    if (p1.children[i].isEqualNode(n1)) {
      i1 = i;
    }
  }
  for (var i = 0; i < p2.children.length; i++) {
    if (p2.children[i].isEqualNode(n2)) {
      i2 = i;
    }
  }

  if ( p1.isEqualNode(p2) && i1 < i2 ) {
    i2++;
  }
  p1.insertBefore(n2, p1.children[i1]);
  p2.insertBefore(n1, p2.children[i2]);
}

Stimulus.register("document_grammar_form", class extends Controller {
  connect() {
    // this.element is the DOM element to which the controller is connected to.
    const thisElement = this.element;

    const removeLinks = thisElement.querySelectorAll("[data-js-remove-field]");
    removeLinks.forEach(link => {
        link.addEventListener("click", function(event){
            event.preventDefault();
            event.target.closest('editable-grammar-field').remove();
        });
    });

    const moveUpLinks = thisElement.querySelectorAll("[data-js-move-field-up]");
      moveUpLinks.forEach(link => {
        link.addEventListener("click", function(event){
            event.preventDefault();
            const grammarFieldNode = event.target.closest('editable-grammar-field');
            swapNodes(grammarFieldNode, grammarFieldNode.previousElementSibling);
        });
    });

    const moveDownLinks = thisElement.querySelectorAll("[data-js-move-field-down]");
      moveDownLinks.forEach(link => {
        link.addEventListener("click", function(event){
          event.preventDefault();
          const grammarFieldNode = event.target.closest('editable-grammar-field');
          swapNodes(grammarFieldNode, grammarFieldNode.nextElementSibling);
        });
    });
  }
});
