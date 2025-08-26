(() => {

  const ANCHOR_SELECTOR = 'sdoc-anchor[data-anchor]';
  const ANCHOR_BLOCK_SELECTOR = '.anchor_block';
  const ANCHOR_BUTTON_SELECTOR = '.anchor_button';
  const ANCHOR_BASE_ICON_SELECTOR = '.anchor_base_icon';
  const ANCHOR_CHECK_ICON_SELECTOR = '.anchor_check_icon';
  const ANCHOR_BACK_LINKS_SELECTOR = '.anchor_back_links';
  const ANCHOR_BACK_LINKS_NUMBER_SELECTOR = '.anchor_back_links_number';

  class AnchorController extends Stimulus.Controller {
    initialize() {
      // this.element is the DOM element to which the controller is connected to.
      // e.g. sdoc-node or .content (The anchor must always be inside this.element)

      const anchors = [...this.element.querySelectorAll(ANCHOR_SELECTOR)];

      anchors.forEach(anchor => {

        // data-controller="anchor_controller" is set on both the content element
        // and sdoc-nodes. When editing/reloading a single node,
        // skip anchors already marked as visible to prevent re-processing.
        if (anchor.hasAttribute("visible")) { return };
        // In the other case, start processing the anchor.
        // This attribute triggers CSS:
        anchor.setAttribute("visible", "");

        // Anchors may appear on inline elements inside a node.
        // Then they render inside the text/content block instead of at the left margin.
        // Calculate shift = (anchor right edge – node left edge)
        // and move the any anchor block left so it aligns at the node margin.
        const translate = anchor.getBoundingClientRect().right - this.element.getBoundingClientRect().x;
        anchor.style.transform = `translate(-${translate}px,0)`;

        const anchorText = anchor.dataset.anchor;
        const anchorButton = anchor.querySelector(ANCHOR_BUTTON_SELECTOR);
        const anchorIcon = anchor.querySelector(ANCHOR_BASE_ICON_SELECTOR);
        const checkIcon = anchor.querySelector(ANCHOR_CHECK_ICON_SELECTOR);

        anchorButton.addEventListener("click", function (event) {
          event.preventDefault();
          updateClipboard(anchorText, confirmMessage(anchorButton, anchorIcon, checkIcon))
        });
      })
    }
  }

  Stimulus.application.register("anchor_controller", AnchorController);

  function updateClipboard(newClip, callback) {
    navigator.clipboard.writeText(newClip).then(() => {
      /* clipboard successfully set */
      () => callback();
      console.info('clipboard successfully set: ', newClip);
    }, () => {
      /* clipboard write failed */
      console.warn('clipboard write failed');
    });
  }

  function confirmMessage(anchorButton, anchorIcon, checkIcon) {
    const element = document.createElement('div');
    element.style.position = 'absolute';
    element.style.zIndex = 10;
    element.style.width = '100%';
    element.style.height = '100%';
    element.style.paddingLeft = '32px';
    element.style.left = 0;
    element.style.background = 'black';
    element.style.color = 'white';
    element.style.fontWeight = 'bold';
    element.style.display = 'flex';
    element.style.alignItems = 'center';
    element.style.justifyContent = 'flex-start';
    // element.innerHTML = '✔️ copied!';

    // initial opacity
    let op = 1;
    element.style.opacity = op;
    anchorButton.style.opacity = 1;

    anchorIcon.style.display = 'none';
    checkIcon.style.display = 'inline';
    const fadeTimer = setInterval(() => {
      if (op <= 0.1) {
        clearInterval(fadeTimer);
        element.remove();
        anchorIcon.style.display = 'inline';
        checkIcon.style.display = 'none';
        anchorButton.style.opacity = '';
      }
      element.style.opacity = op;
      op -= op * 0.1;
    }, 30);

    // return element;
    anchorButton.append(element);
  }
})();
