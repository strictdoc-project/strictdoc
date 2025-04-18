(() => {

  class CopyStableLinkController extends Stimulus.Controller {
    connect() {
      const button = this.element;

      button.addEventListener("click", (event) => {
        event.preventDefault();

        const link = button.dataset.path;

        const copyIcon = this.element.querySelector(".copy_to_clipboard-copy_icon");
        const doneIcon = this.element.querySelector(".copy_to_clipboard-done_icon");

        // Resolve any relative URLs with respect to current URL.
        const resolved = (
          this._isAbsoluteURL(link)
          ? link
          : new URL(link, window.location.href).href
        );

        // Expand folder to index if we run from the local file system.
        const expanded = (
          (window.location.protocol === 'file:')
          ? resolved.replace(/#/, 'index.html#')
          : resolved
        );

        this._updateClipboard(expanded, this._confirmCopy(button, copyIcon, doneIcon));
      });
    }

    _isAbsoluteURL(url) {
      try {
        new URL(url); // throws if it's relative
        return true;
      } catch {
        return false;
      }
    }

    _updateClipboard(newClip, callback) {
      navigator.clipboard.writeText(newClip).then(() => {
        /* clipboard successfully set */
        () => callback();
        console.info('Clipboard successfully set: ', newClip);
      }, () => {
        /* clipboard write failed */
        console.warn('Clipboard write failed');
      });
    }

    _confirmCopy(button, copyIcon, doneIcon) {
      // initial opacity
      let op = 1;

      // make button visible
      button.style.opacity = 1;

      // make DONE icon visible (instead of default COPY)
      copyIcon.style.display = 'none';
      doneIcon.style.display = 'contents';

      const fadeTimer = setInterval(() => {
        if (op <= 0.1) {
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
  }

  Stimulus.application.register("copy_stable_link_button", CopyStableLinkController);

})();
