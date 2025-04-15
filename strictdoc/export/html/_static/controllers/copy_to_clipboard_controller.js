(() => {

  class CopyToClipboard extends Stimulus.Controller {
    connect() {
      const button = this.element.querySelector(".copy_to_clipboard-button");

      // Add event listener
      button.addEventListener("click", (event) => {
        event.preventDefault();

        const clip = this.element.querySelector("sdoc-field-content").innerText.trim();
        const copyIcon = this.element.querySelector(".copy_to_clipboard-copy_icon");
        const doneIcon = this.element.querySelector(".copy_to_clipboard-done_icon");
        const cover = this.element.querySelector(".copy_to_clipboard-cover");
        _updateClipboard(
          clip,
          _confirm(button, copyIcon, doneIcon, cover)
        )
      });
    }
  }

  Stimulus.application.register("copy_to_clipboard", CopyToClipboard);

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
      if (op <= 0.1) {
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

})();
