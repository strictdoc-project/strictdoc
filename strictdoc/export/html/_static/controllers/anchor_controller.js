const anchorIcon = `
<svg class="svg_icon" width="16px" height="16px" viewBox="0 0 16 16">
  <circle cx="8" cy="3" r="1"></circle>
  <line x1="8" y1="4" x2="8" y2="14.5"></line>
  <path d="M5.5,6 C5.5,6 7,6 10.5,6 C10.5,6 5.5,6 5.5,6 Z"></path>
  <path d="M2,11 C3,10 3.5,9.5 3.5,9.5 C3.5,12 5,13 8,13 C11,13 12.5,12 12.5,9.5 C12.5,9.5 13,10 14,11"></path>
</svg>`;

Stimulus.register("anchor_controller", class extends Controller {
  initialize() {
    // this.element is the DOM element to which the controller is connected to.

    // The content boundary is needed for correct positioning of anchors,
    // not depending on the display type of the parent elements, i.e. "left".
    // If triggered on a node,
    // the result is expected to be the same as on the content flow.
    const contentLeft = this.element.getBoundingClientRect().x;

    const anchors = [...this.element.querySelectorAll('sdoc-anchor')];

    anchors.forEach(anchor => {

      // We add data-controller="anchor_controller"
      // on both the entire content element and a node.
      // When editing a node, only the single node is reloaded,
      // so to avoid duplicate anchor processing
      // on nodes not affected by the edit,
      // we do the check:
      if (anchor.hasAttribute("visible")) { return };

      // In the other case, start processing the anchor.

      // This attribute triggers CSS:
      anchor.setAttribute("visible", "");

      const anchorText = anchor.dataset.anchor || anchor.id;

      // Add an always visible button:
      const anchorButton = document.createElement('div');
      anchorButton.classList.add('anchor_button');
      anchorButton.title = "Click to copy";
      anchorButton.innerHTML = anchorIcon;
      anchor.append(anchorButton);
      // Now position the anchor, considering the added button:
      const translate = anchor.getBoundingClientRect().right - contentLeft;
      anchor.style.transform = `translate(-${translate}px,0)`;

      // Add content block
      const anchorContentBlock = document.createElement('span');
      anchorContentBlock.classList.add('anchor_button_text');
      anchorContentBlock.innerHTML = anchorText;
      anchorButton.append(anchorContentBlock);

      // Add event listener
      anchorButton.addEventListener("click", function(event){
        event.preventDefault();
        navigator.clipboard.writeText(anchorText);
        // copied to clipboard
      });

    })

  }
});
