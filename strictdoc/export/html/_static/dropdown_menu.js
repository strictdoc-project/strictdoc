// Supports multiple menus (toggle/content pairs) per page.
// Toggle: [data-dropdown-handler] + aria-controls="id_of_content".
// Content: element with that id + aria-hidden.

(function () {
  function initDropdowns() {
    const toggles = document.querySelectorAll(
      "[data-dropdown-handler]:not([data-dropdown-initialized])"
    );
    const pairs = [];
    toggles.forEach((toggle) => {
      const contentId = toggle.getAttribute("aria-controls");
      if (!contentId) return;
      const content = document.getElementById(contentId);
      if (!content) return;
      toggle.setAttribute("data-dropdown-initialized", "true");
      pairs.push({ toggle, content });
    });

    pairs.forEach((pair) => {
      const { toggle, content } = pair;

      const show = () => {
        pairs.forEach((p) => {
          if (p === pair) return;
          p.toggle.setAttribute("aria-expanded", false);
          p.content.setAttribute("aria-hidden", true);
        });
        toggle.setAttribute("aria-expanded", true);
        content.setAttribute("aria-hidden", false);
      };

      const hide = () => {
        toggle.setAttribute("aria-expanded", false);
        content.setAttribute("aria-hidden", true);
      };

      toggle.addEventListener("click", (event) => {
        event.stopPropagation();
        JSON.parse(toggle.getAttribute("aria-expanded")) ? hide() : show();
      });

      // Close when click/focus is outside both the toggle and the content.
      const handleClosure = (event) => {
        const target = event.target;
        if (!toggle.contains(target) && !content.contains(target)) hide();
      };

      window.addEventListener("click", handleClosure);
      window.addEventListener("focusin", handleClosure);
    });
  }

  // On initial page load, wire up all dropdowns found in the DOM.
  window.addEventListener("load", () => {
    initDropdowns();

    // When a turbo-stream replaces the frame content, the old DOM nodes and
    // their event listeners are gone. MutationObserver re-initializes any
    // fresh toggle that appears — the :not([data-dropdown-initialized])
    // selector makes it a no-op if nothing new arrived.
    const frame = document.getElementById("frame-viewtype-menu");
    if (frame) {
      new MutationObserver(initDropdowns).observe(frame, { childList: true });
    }
  });

})();
