// Supports multiple menus (toggle/content pairs) per page.
// Toggle: [data-dropdown-handler] + aria-controls="id_of_content".
// Content: element with that id + aria-hidden.

window.addEventListener("load", () => {
  const toggles = document.querySelectorAll("[data-dropdown-handler]");
  const pairs = [];
  toggles.forEach((toggle) => {
    const contentId = toggle.getAttribute("aria-controls");
    if (!contentId) return;
    const content = document.getElementById(contentId);
    if (!content) return;
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

  // Header dropdown mode: when the header is too narrow, move some actions into a dropdown.
  const headerPlaceholder = document.getElementById("header-placeholder");
  const headerActions = document.getElementById("header-actions");

  if (headerPlaceholder && headerActions) {
    const headerActionsMenu = headerActions.querySelector(".header-actions__menu");
    const INLINE_FREE_SPACE_PX = 16; // px

    const measureInlineActionsWidth = () => {
      // Measure once in inline mode: this width is treated as stable on a given page
      // since the set of header action buttons does not change after initial render.
      if (!headerActionsMenu) {
        return 0;
      }

      const previousStyle = headerActionsMenu.getAttribute("style");
      headerActionsMenu.style.display = "flex";
      headerActionsMenu.style.flexDirection = "row";
      headerActionsMenu.style.position = "absolute";
      headerActionsMenu.style.right = "0";
      headerActionsMenu.style.top = "0";
      headerActionsMenu.style.visibility = "hidden";
      headerActionsMenu.style.pointerEvents = "none";

      const inlineActionsWidth = Math.ceil(headerActionsMenu.scrollWidth);

      if (previousStyle === null) {
        headerActionsMenu.removeAttribute("style");
      } else {
        headerActionsMenu.setAttribute("style", previousStyle);
      }

      return inlineActionsWidth;
    };

    let inlineActionsWidth = measureInlineActionsWidth();

    const updateHeaderDropdownMode = () => {
      const availableWidth =
        headerPlaceholder.offsetWidth + headerActions.offsetWidth;
      const hasDropdown =
        headerActions.getAttribute("data-has-dropdown") === "true";
      const requiredInlineWidth =
        inlineActionsWidth + INLINE_FREE_SPACE_PX;
      const shouldHaveDropdown = availableWidth < requiredInlineWidth;

      if (shouldHaveDropdown === hasDropdown) {
        return;
      }

      if (shouldHaveDropdown) {
        headerActions.setAttribute("data-has-dropdown", "true");
      } else {
        headerActions.removeAttribute("data-has-dropdown");
      }
    };

    window.addEventListener("resize", updateHeaderDropdownMode);
    updateHeaderDropdownMode();
    headerActions.setAttribute("data-dropdown-measure-state", "done");

    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(() => {
        inlineActionsWidth = measureInlineActionsWidth();
        updateHeaderDropdownMode();
      });
    }
  }

}, false);
