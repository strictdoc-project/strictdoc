const anchorIconSVG = `
<svg class="svg_icon" width="16px" height="16px" viewBox="0 0 16 16">
  <g class="svg_icon_not_hover_visible" id="anchorIconSVG">
    <circle cx="8" cy="3" r="1"></circle>
    <line x1="8" y1="4" x2="8" y2="14.5"></line>
    <path d="M5.5,6 C5.5,6 7,6 10.5,6 C10.5,6 5.5,6 5.5,6 Z"></path>
    <path d="M2,11 C3,10 3.5,9.5 3.5,9.5 C3.5,12 5,13 8,13 C11,13 12.5,12 12.5,9.5 C12.5,9.5 13,10 14,11"></path>
  </g>
  <g class="svg_icon_hover_visible" id="copyIconSVG">
    <path d="M0 6.75C0 5.784.784 5 1.75 5h1.5a.75.75 0 0 1 0 1.5h-1.5a.25.25 0 0 0-.25.25v7.5c0 .138.112.25.25.25h7.5a.25.25 0 0 0 .25-.25v-1.5a.75.75 0 0 1 1.5 0v1.5A1.75 1.75 0 0 1 9.25 16h-7.5A1.75 1.75 0 0 1 0 14.25Z"></path>
    <path d="M5 1.75C5 .784 5.784 0 6.75 0h7.5C15.216 0 16 .784 16 1.75v7.5A1.75 1.75 0 0 1 14.25 11h-7.5A1.75 1.75 0 0 1 5 9.25Zm1.75-.25a.25.25 0 0 0-.25.25v7.5c0 .138.112.25.25.25h7.5a.25.25 0 0 0 .25-.25v-7.5a.25.25 0 0 0-.25-.25Z"></path>
  </g>
  </svg>`;

// TODO copyIconSVG
// TODO checkIconSVG

const checkIconSVG = `
<svg class="svg_icon" width="16px" height="16px" viewBox="0 0 16 16">
  <path d="M13.78 4.22a.75.75 0 0 1 0 1.06l-7.25 7.25a.75.75 0 0 1-1.06 0L2.22 9.28a.751.751 0 0 1 .018-1.042.751.751 0 0 1 1.042-.018L6 10.94l6.72-6.72a.75.75 0 0 1 1.06 0Z"></path>
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
      const anchorIcon = createIcon(anchorIconSVG);
      const checkIcon = createIcon(checkIconSVG);
      checkIcon.style.display = 'none';
      anchorButton.append(anchorIcon, checkIcon,);
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
        updateClipboard(anchorText, confirmMessage(anchorButton, anchorIcon, checkIcon))
      });

    })

  }
});

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

    anchorIcon.style.display = 'none';
    checkIcon.style.display = 'inline';
    const fadeTimer = setInterval(() => {
        if (op <= 0.1){
            clearInterval(fadeTimer);
            element.remove();
            anchorIcon.style.display = 'inline';
            checkIcon.style.display = 'none';
        }
        element.style.opacity = op;
        op -= op * 0.1;
    }, 30);

    // return element;
    anchorButton.append(element);
  }
