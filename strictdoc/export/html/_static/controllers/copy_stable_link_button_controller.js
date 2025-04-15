Stimulus.register("copy_stable_link_button", class extends Controller {
  connect() {
    const button = this.element;

    button.addEventListener("click", (event) => {
      event.preventDefault();

      const clip = button.dataset.path;

      const copyIcon = this.element.querySelector(".copy_to_clipboard-copy_icon");
      const doneIcon = this.element.querySelector(".copy_to_clipboard-done_icon");
      _updateClipboard(
        clip,
        _confirm(button, copyIcon, doneIcon)
      )
    });
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

function _confirm(button, copyIcon, doneIcon) {
  // initial opacity
  let op = 1;

  // make button visible
  button.style.opacity = 1;

  // make DONE icon visible (instead of default COPY)
  copyIcon.style.display = 'none';
  doneIcon.style.display = 'contents';

  const fadeTimer = setInterval(() => {
      if (op <= 0.1){
          clearInterval(fadeTimer);

          // make button invisible
          button.style.opacity = '';

          // make COPY icon visible back
          copyIcon.style.display = 'contents';
          doneIcon.style.display = 'none';
      }
      op -= op * 0.1;
  }, 30);
}
