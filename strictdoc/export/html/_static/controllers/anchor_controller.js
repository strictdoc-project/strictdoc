(() => {

  const anchorIconSVG = `
  <svg class="svg_icon" width="16px" height="16px" viewBox="0 0 16 16">
    <g class="svg_icon_not_hover_visible" id="anchorIconSVG">
      <circle cx="8" cy="3" r="1"></circle>
      <line x1="8" y1="4" x2="8" y2="14.5"></line>
      <path d="M5.5,6 C5.5,6 7,6 10.5,6 C10.5,6 5.5,6 5.5,6 Z"/>
      <path d="M2,11 C3,10 3.5,9.5 3.5,9.5 C3.5,12 5,13 8,13 C11,13 12.5,12 12.5,9.5 C12.5,9.5 13,10 14,11"/>
    </g>
    <g class="svg_icon_hover_visible" id="copyIconSVG">
      <path d="M8,2 L12,2 C13,2 14,3 14,4 L14,8 C14,9 13,10 12,10 L8,10 C7,10 6,9 6,8 L6,4 C6,3 7,2 8,2 Z"/>
      <path d="M10,12 C10,13 9,14 8,14 L4,14 C3,14 2,13 2,12 L2,8 C2,7 3,6 4,6"/>
    </g>
    </svg>`;

  const checkIconSVG = `
  <svg class="svg_icon" width="16px" height="16px" viewBox="0 0 16 16">
    <path d="M2.5,8.5 C2.5,8.5 3.5,9.5 6,12 C11,7 13.5,4.5 13.5,4.5"/>
  </svg>`;

  class AnchorController extends Stimulus.Controller {
    initialize() {
      // this.element is the DOM element to which the controller is connected to.

      // The content boundary is needed for correct positioning of anchors,
      // not depending on the display type of the parent elements, i.e. "left".
      // If triggered on a node,
      // the result is expected to be the same as on the content flow.
      const contentLeft = this.element.getBoundingClientRect().x;

      // ** 1) if a node does not have [data-uid] parameter,
      // ** we don't want to show anchors
      const anchors = [...this.element.querySelectorAll('sdoc-anchor[data-uid]')];

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

        const anchorText = anchor.dataset.anchor || anchor.dataset.uid;

        // Create anchor content block:
        const anchorBlock = document.createElement('div');
        anchorBlock.classList.add('anchor_block');
        anchorBlock.setAttribute('data-testid', 'anchor_hover_button');

        // Create the button:
        const anchorButton = document.createElement('div');
        anchorButton.classList.add('anchor_button');
        anchorButton.title = "Click to copy";
        const anchorIcon = createIcon(anchorIconSVG);
        const checkIcon = createIcon(checkIconSVG);
        checkIcon.style.display = 'none';
        anchorButton.append(anchorIcon, checkIcon,);

        // Append button:
        anchorBlock.append(anchorButton);

        // Add anchor back links IF EXIST:
        let template = anchor.querySelector("template");
        if (template) {
          // Create anchor back links block:
          const anchorBackLinks = document.createElement('div');
          anchorBackLinks.classList.add('anchor_back_links');
          anchorBackLinks.append(template.content.cloneNode(true));

          // Calculate back links:
          let linksNumber = anchorBackLinks.querySelectorAll('a').length;

          const anchorBackLinksNumber = document.createElement('div');
          anchorBackLinksNumber.classList.add('anchor_back_links_number');
          anchorBackLinksNumber.setAttribute('data-testid', 'anchor_links_number');
          anchorBackLinksNumber.innerText = linksNumber;

          anchor.classList.add('anchor_has_links');

          // Append links block:
          anchorBlock.append(anchorBackLinks, anchorBackLinksNumber);
        }

        // Append anchor content block:
        anchor.append(anchorBlock);

        // Now position the anchor, considering the added button:
        const translate = anchor.getBoundingClientRect().right - contentLeft;
        anchor.style.transform = `translate(-${translate}px,0)`;

        // Add button content block
        const anchorButtonText = document.createElement('span');
        anchorButtonText.classList.add('anchor_button_text');
        anchorButtonText.innerHTML = anchorText;
        anchorButton.append(anchorButtonText);
        anchorButton.setAttribute('data-testid', 'section-anchor-button');

        // Add event listener
        anchorButton.addEventListener("click", function (event) {
          event.preventDefault();
          updateClipboard(anchorText, confirmMessage(anchorButton, anchorIcon, checkIcon))
        });

      })
    }
  }

  Stimulus.application.register("anchor_controller", AnchorController);

  function createIcon(iconSVG) {
    const icon = document.createElement('span');
    icon.style.lineHeight = .1;
    icon.innerHTML = iconSVG;
    return icon
  }

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
