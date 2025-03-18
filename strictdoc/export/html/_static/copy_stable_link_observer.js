// Fallback implementation for `copying stable links` without Stimulus.
// Uses MutationObserver to handle dynamically inserted .copy_stable_link-button elements.
// Works in static/offline HTML where ES modules and Stimulus are not available.
(function () {
  function handleButton(button) {
    if (button.dataset._copyInitialized === "1") return;
    button.dataset._copyInitialized = "1";

    button.addEventListener("click", (event) => {
      event.preventDefault();

      const link = button.dataset.path;
      const copyIcon = button.querySelector(".copy_to_clipboard-copy_icon");
      const doneIcon = button.querySelector(".copy_to_clipboard-done_icon");

      // resolve any relative urls with respect to current URL
      const resolved = isAbsoluteUrl(link)
      ? link
      : new URL(link, window.location.href).href;

      // expand folder to index if we run from the local file system
      const expanded = (window.location.protocol === 'file:')
      ? resolved.replace(/#/, 'index.html#')
      : resolved

      updateClipboard(expanded, confirmCopy(button, copyIcon, doneIcon));
    });
  }

  function isAbsoluteUrl(url) {
    try {
      new URL(url); // throws if it's relative
      return true;
    } catch {
      return false;
    }
  }

  function updateClipboard(newClip, callback) {
    navigator.clipboard.writeText(newClip).then(() => {
      callback();
      console.info("clipboard successfully set:", newClip);
    }, () => {
      console.warn("clipboard write failed");
    });
  }

  function confirmCopy(button, copyIcon, doneIcon) {
    return () => {
      let op = 1;

      button.style.opacity = 1;
      copyIcon.style.display = "none";
      doneIcon.style.display = "contents";

      const fadeTimer = setInterval(() => {
        if (op <= 0.1) {
          clearInterval(fadeTimer);
          button.style.opacity = "";
          copyIcon.style.display = "contents";
          doneIcon.style.display = "none";
        }
        op -= op * 0.1;
      }, 30);
    };
  }

  function initializeButtons(root = document) {
    const buttons = root.querySelectorAll(".copy_stable_link-button");
    buttons.forEach(handleButton);
  }

  // Initial setup on page load
  window.addEventListener("DOMContentLoaded", () => {
    initializeButtons();
    // Observe future changes (e.g., from Turbo)
    const observer = new MutationObserver((mutationsList) => {
      for (const mutation of mutationsList) {
        for (const node of mutation.addedNodes) {
          if (!(node instanceof HTMLElement)) continue;

          if (node.matches(".copy_stable_link-button")) {
            handleButton(node);
          } else {
            initializeButtons(node);
          }
        }
      }
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true
    });
  });

})();
