Stimulus.register("copy_to_clipboard_button", class extends Controller {
  connect() {
    this.element.className = 'copy_to_clipboard-field';

    const clip = this.element.innerText.trim();

    const copyIcon = this._createIcon(this._copyIconSVG());
    const doneIcon = this._createIcon(this._doneIconSVG());
    const button = this._createButton(copyIcon, doneIcon);
    const cover = this._createCover();
    cover.prepend(button);
    this.element.append(cover);

    // Add event listener
    button.addEventListener("click", function(event){
      event.preventDefault();
      _updateClipboard(clip, _confirm(button, copyIcon, doneIcon, cover))
    });
  }

  _createCover() {
    const cover = document.createElement("div");
    cover.className = 'copy_to_clipboard-cover';
    return cover;
  }

  _createButton(copyIcon, doneIcon) {
    const button = document.createElement("div");
    button.title = "Click to copy";
    button.className = 'action_button';
    doneIcon.style.display = 'none';
    button.append(copyIcon, doneIcon,);
    return button
  }

  _createIcon(iconSVG) {
    const icon = document.createElement('span');
    icon.style.display = 'contents';
    icon.innerHTML = iconSVG;
    return icon
  }

  _copyIconSVG() {
    return `<svg class="svg_icon" width="16px" height="16px" viewBox="0 0 16 16">
      <g id="copyIconSVG">
        <path d="M8,2 L12,2 C13,2 14,3 14,4 L14,8 C14,9 13,10 12,10 L8,10 C7,10 6,9 6,8 L6,4 C6,3 7,2 8,2 Z"/>
        <path d="M10,12 C10,13 9,14 8,14 L4,14 C3,14 2,13 2,12 L2,8 C2,7 3,6 4,6"/>
      </g>
    </svg>`
  }

  _doneIconSVG() {
    return `<svg class="svg_icon" width="16px" height="16px" viewBox="0 0 16 16">
      <path d="M2.5,8.5 C2.5,8.5 3.5,9.5 6,12 C11,7 13.5,4.5 13.5,4.5"/>
    </svg>`
  }
});

function _updateClipboard(newClip, callback) {
  navigator.clipboard.writeText(newClip).then(() => {
    /* clipboard successfully set */
    () => callback();
    console.info('clipboard successfully set: ', newClip);
  }, () => {
    /* clipboard write failed */
    console.warn('clipboard write failed');
  });
}

function _confirm(button, copyIcon, doneIcon, cover) {
  // initial opacity
  let op = 1;

  // make button visible
  button.style.opacity = 1;

  // initial cover
  cover.style.background = `rgba(242, 100, 42, ${op})`;

  // make DONE icon visible (instead of default COPY)
  copyIcon.style.display = 'none';
  doneIcon.style.display = 'contents';

  const fadeTimer = setInterval(() => {
      // update cover
      cover.style.background = `rgba(242, 100, 42, ${op})`;
      if (op <= 0.1){
          clearInterval(fadeTimer);

          // make button invisible
          button.style.opacity = '';

          // reset cover
          cover.style.background = `rgba(242, 100, 42, 0)`;

          // make COPY icon visible back
          copyIcon.style.display = 'contents';
          doneIcon.style.display = 'none';
      }
      op -= op * 0.1;
  }, 30);
}
