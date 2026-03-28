(function () {
  const ROOT_SELECTOR = "[data-work-planner-root]";
  const MONTH_WIDTH_DEFAULT = 160;
  const MONTH_WIDTH_STEP = 20;
  const MODE_STORAGE_KEY = "strictdoc.work_planner.mode";
  const ZOOM_STORAGE_KEY = "strictdoc.work_planner.month_width.v2";

  function getRoot() {
    return document.querySelector(ROOT_SELECTOR);
  }

  function getMonthWidth(root) {
    const computed = getComputedStyle(root)
      .getPropertyValue("--work-planner-month-width")
      .replace("px", "")
      .trim();
    const parsed = Number.parseFloat(computed);
    return Number.isFinite(parsed) ? parsed : MONTH_WIDTH_DEFAULT;
  }

  function activateMode(root, mode) {
    root.querySelectorAll("[data-work-planner-view]").forEach((view) => {
      view.hidden = view.dataset.workPlannerView !== mode;
    });
    root.querySelectorAll("[data-work-planner-mode-button]").forEach((button) => {
      button.toggleAttribute(
        "active",
        button.dataset.workPlannerModeButton === mode
      );
    });
    localStorage.setItem(MODE_STORAGE_KEY, mode);
  }

  function updateAddLinks(root) {
    const documentSelector = root.querySelector("[data-work-planner-default-document]");
    if (!documentSelector) {
      return;
    }
    const currentDocumentMid = documentSelector.value;
    root.querySelectorAll("[data-work-planner-add-template]").forEach((link) => {
      link.href = link.dataset.workPlannerAddTemplate.replace(
        "__DOCUMENT_MID__",
        currentDocumentMid
      );
    });
  }

  function applyMonthWidth(root, monthWidth) {
    const clampedWidth = Math.max(120, Math.min(320, monthWidth));
    root.style.setProperty("--work-planner-month-width", `${clampedWidth}px`);
    localStorage.setItem(ZOOM_STORAGE_KEY, `${clampedWidth}`);
  }

  function postMove(endpoint, nodeMid, monthDelta) {
    const formData = new FormData();
    formData.append("node_mid", nodeMid);
    formData.append("month_delta", `${monthDelta}`);

    fetch(endpoint, {
      method: "POST",
      headers: {
        "Accept": "text/vnd.turbo-stream.html",
      },
      body: formData,
    })
      .then((response) => response.text())
      .then((html) => Turbo.renderStreamMessage(html));
  }

  function bindDragAndDrop(root) {
    const scrollContainer = root.querySelector("[data-work-planner-canvas-scroll]");
    if (!scrollContainer) {
      return;
    }

    let dragPayload = null;

    root.querySelectorAll("[data-work-planner-draggable]").forEach((card) => {
      card.addEventListener("dragstart", () => {
        dragPayload = {
          nodeMid: card.dataset.nodeMid,
          startMonthIndex: Number.parseInt(card.dataset.startMonthIndex, 10),
          endpoint: card.dataset.moveEndpoint,
        };
      });
      card.addEventListener("dragend", () => {
        dragPayload = null;
        root.querySelectorAll("[data-work-planner-dropzone]").forEach((dropzone) => {
          dropzone.removeAttribute("data-work-planner-drop-active");
        });
      });
    });

    root.querySelectorAll("[data-work-planner-dropzone]").forEach((dropzone) => {
      dropzone.addEventListener("dragover", (event) => {
        if (!dragPayload) {
          return;
        }
        event.preventDefault();
        dropzone.setAttribute("data-work-planner-drop-active", "true");
      });

      dropzone.addEventListener("dragleave", () => {
        dropzone.removeAttribute("data-work-planner-drop-active");
      });

      dropzone.addEventListener("drop", (event) => {
        if (!dragPayload) {
          return;
        }

        event.preventDefault();
        dropzone.removeAttribute("data-work-planner-drop-active");

        const rootRect = dropzone.getBoundingClientRect();
        const monthWidth = getMonthWidth(root);
        const monthCount = Number.parseInt(
          root.style.getPropertyValue("--work-planner-month-count"),
          10
        );

        const relativeX =
          event.clientX - rootRect.left + scrollContainer.scrollLeft;
        const targetMonthIndex = Math.max(
          0,
          Math.min(monthCount - 1, Math.floor(relativeX / monthWidth))
        );
        const monthDelta = targetMonthIndex - dragPayload.startMonthIndex;
        if (monthDelta === 0) {
          return;
        }

        postMove(dragPayload.endpoint, dragPayload.nodeMid, monthDelta);
      });
    });
  }

  function initialize() {
    const root = getRoot();
    if (!root) {
      return;
    }
    if (root.dataset.workPlannerInitialized === "true") {
      return;
    }
    root.dataset.workPlannerInitialized = "true";

    const storedMode = localStorage.getItem(MODE_STORAGE_KEY) || "person";
    activateMode(root, storedMode);

    const storedMonthWidth = Number.parseFloat(
      localStorage.getItem(ZOOM_STORAGE_KEY) || `${MONTH_WIDTH_DEFAULT}`
    );
    applyMonthWidth(root, storedMonthWidth);

    root.querySelectorAll("[data-work-planner-mode-button]").forEach((button) => {
      button.addEventListener("click", () => {
        activateMode(root, button.dataset.workPlannerModeButton);
      });
    });

    const documentSelector = root.querySelector("[data-work-planner-default-document]");
    if (documentSelector) {
      documentSelector.addEventListener("change", () => updateAddLinks(root));
      updateAddLinks(root);
    }

    const zoomInButton = root.querySelector("[data-work-planner-zoom-in]");
    const zoomOutButton = root.querySelector("[data-work-planner-zoom-out]");
    const zoomResetButton = root.querySelector("[data-work-planner-zoom-reset]");

    zoomInButton &&
      zoomInButton.addEventListener("click", () => {
        applyMonthWidth(root, getMonthWidth(root) + MONTH_WIDTH_STEP);
      });

    zoomOutButton &&
      zoomOutButton.addEventListener("click", () => {
        applyMonthWidth(root, getMonthWidth(root) - MONTH_WIDTH_STEP);
      });

    zoomResetButton &&
      zoomResetButton.addEventListener("click", () => {
        applyMonthWidth(root, MONTH_WIDTH_DEFAULT);
      });

    bindDragAndDrop(root);
  }

  function scheduleInitialize() {
    requestAnimationFrame(initialize);
  }

  document.addEventListener("DOMContentLoaded", initialize);
  document.addEventListener("turbo:render", initialize);
  document.addEventListener("turbo:frame-render", scheduleInitialize);
  document.addEventListener("turbo:load", scheduleInitialize);
})();
