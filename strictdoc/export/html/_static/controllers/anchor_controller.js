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
      // this.element == sdoc-node
      // Processing node anchors and inline anchors in the text:
      const anchors = [...this.element.querySelectorAll(ANCHOR_SELECTOR)];
      anchors.forEach(anchor => {

        // Note: template already applies conditions whether an anchorBlock is rendered.
        // JS assumes that if anchorBlock exists, it is valid to process.
        const anchorBlock = anchor.querySelector(ANCHOR_BLOCK_SELECTOR);

        if (anchorBlock) {
          const anchorText = anchor.dataset.anchor;
          const anchorButton = anchor.querySelector(ANCHOR_BUTTON_SELECTOR);
          const anchorIcon = anchor.querySelector(ANCHOR_BASE_ICON_SELECTOR);
          const checkIcon = anchor.querySelector(ANCHOR_CHECK_ICON_SELECTOR);

          anchorButton.addEventListener("click", function (event) {
            event.preventDefault();
            updateClipboard(anchorText, confirmMessage(anchorButton, anchorIcon, checkIcon))
          });
        }
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
