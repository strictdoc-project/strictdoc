(function () {
  const ROOT_SELECTOR = "[data-work-planner-root]";
  const SCALE_DEFAULT = 1;
  const BASE_MONTH_WIDTH_DEFAULT = 160;
  const ZOOM_SCALE_FACTOR = 1.25;
  const ZOOM_STORAGE_KEY = "strictdoc.work_planner.zoom_scale.v1";
  const GLOBAL_BIND_FLAG = "__strictdocWorkPlannerGlobalBound";

  function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
  }

  function getRoot() {
    return document.querySelector(ROOT_SELECTOR);
  }

  function normalizeTarget(target) {
    if (target instanceof Element) {
      return target;
    }
    if (target instanceof Node) {
      return target.parentElement;
    }
    return null;
  }

  function getRootFromElement(element) {
    const normalizedElement = normalizeTarget(element);
    if (!normalizedElement) {
      return getRoot();
    }
    return normalizedElement.closest(ROOT_SELECTOR);
  }

  function getScrollContainer(root) {
    return root.querySelector("[data-work-planner-canvas-scroll]");
  }

  function getCamera(root) {
    return root.querySelector("[data-work-planner-canvas-camera]");
  }

  function getSurface(root) {
    return root.querySelector("[data-work-planner-canvas-surface]");
  }

  function getMonthCount(root) {
    const parsed = Number.parseInt(
      root.style.getPropertyValue("--work-planner-month-count"),
      10
    );
    return Number.isFinite(parsed) && parsed > 0 ? parsed : 1;
  }

  function getBaseMonthWidth(root) {
    const parsed = Number.parseFloat(
      getComputedStyle(root)
        .getPropertyValue("--work-planner-month-width")
        .replace("px", "")
        .trim()
    );
    return Number.isFinite(parsed) ? parsed : BASE_MONTH_WIDTH_DEFAULT;
  }

  function getCanvasScale(root) {
    const parsed = Number.parseFloat(
      getComputedStyle(root)
        .getPropertyValue("--work-planner-scale")
        .trim()
    );
    return Number.isFinite(parsed) ? parsed : SCALE_DEFAULT;
  }

  function getSurfaceSize(root) {
    const surface = getSurface(root);
    if (!surface) {
      return {
        width: 1,
        height: 1,
      };
    }
    return {
      width: Math.max(surface.scrollWidth, surface.offsetWidth, 1),
      height: Math.max(surface.scrollHeight, surface.offsetHeight, 1),
    };
  }

  function getScaleBounds(root) {
    const scrollContainer = getScrollContainer(root);
    const { width, height } = getSurfaceSize(root);

    if (!scrollContainer) {
      return {
        minScale: SCALE_DEFAULT,
        maxScale: SCALE_DEFAULT,
        surfaceWidth: width,
        surfaceHeight: height,
      };
    }

    const viewportWidth = Math.max(scrollContainer.clientWidth, 1);
    const viewportHeight = Math.max(scrollContainer.clientHeight, 1);
    const fitWidthScale = viewportWidth / width;
    const fitHeightScale = viewportHeight / height;
    const minScale = Math.min(SCALE_DEFAULT, fitWidthScale, fitHeightScale);
    const maxScale = Math.max(
      minScale,
      viewportWidth / Math.max(1, getBaseMonthWidth(root))
    );

    return {
      minScale,
      maxScale,
      surfaceWidth: width,
      surfaceHeight: height,
    };
  }

  function clampScale(root, scale) {
    const { minScale, maxScale } = getScaleBounds(root);
    return clamp(scale, minScale, maxScale);
  }

  function updateCanvasCamera(root) {
    const scrollContainer = getScrollContainer(root);
    const camera = getCamera(root);
    if (!scrollContainer || !camera) {
      return;
    }

    const { surfaceWidth, surfaceHeight } = getScaleBounds(root);
    const scale = getCanvasScale(root);
    camera.style.width = `${Math.max(
      scrollContainer.clientWidth,
      surfaceWidth * scale
    )}px`;
    camera.style.height = `${Math.max(
      scrollContainer.clientHeight,
      surfaceHeight * scale
    )}px`;
  }

  function applyCanvasScale(root, scale) {
    const clampedScale = clampScale(root, scale);
    root.style.setProperty("--work-planner-scale", `${clampedScale}`);
    localStorage.setItem(ZOOM_STORAGE_KEY, `${clampedScale}`);
    updateCanvasCamera(root);
    return clampedScale;
  }

  function zoomToScale(
    root,
    scale,
    anchorClientX = null,
    anchorClientY = null
  ) {
    const scrollContainer = getScrollContainer(root);
    if (!scrollContainer) {
      applyCanvasScale(root, scale);
      return;
    }

    const oldScale = getCanvasScale(root);
    const newScale = clampScale(root, scale);
    if (Math.abs(newScale - oldScale) < 0.0001) {
      applyCanvasScale(root, newScale);
      return;
    }

    const rect = scrollContainer.getBoundingClientRect();
    const anchorOffsetX =
      anchorClientX === null
        ? rect.width / 2
        : clamp(anchorClientX - rect.left, 0, rect.width);
    const anchorOffsetY =
      anchorClientY === null
        ? rect.height / 2
        : clamp(anchorClientY - rect.top, 0, rect.height);

    const logicalX = (scrollContainer.scrollLeft + anchorOffsetX) / oldScale;
    const logicalY = (scrollContainer.scrollTop + anchorOffsetY) / oldScale;

    applyCanvasScale(root, newScale);

    const maxScrollLeft = Math.max(
      0,
      scrollContainer.scrollWidth - scrollContainer.clientWidth
    );
    const maxScrollTop = Math.max(
      0,
      scrollContainer.scrollHeight - scrollContainer.clientHeight
    );

    scrollContainer.scrollLeft = clamp(
      logicalX * newScale - anchorOffsetX,
      0,
      maxScrollLeft
    );
    scrollContainer.scrollTop = clamp(
      logicalY * newScale - anchorOffsetY,
      0,
      maxScrollTop
    );
  }

  function getZoomedInScale(root) {
    return getCanvasScale(root) * ZOOM_SCALE_FACTOR;
  }

  function getZoomedOutScale(root) {
    return getCanvasScale(root) / ZOOM_SCALE_FACTOR;
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

  function postMove(endpoint, nodeMid, monthDelta) {
    const formData = new FormData();
    formData.append("node_mid", nodeMid);
    formData.append("month_delta", `${monthDelta}`);

    fetch(endpoint, {
      method: "POST",
      headers: {
        Accept: "text/vnd.turbo-stream.html",
      },
      body: formData,
    })
      .then((response) => response.text())
      .then((html) => Turbo.renderStreamMessage(html));
  }

  function bindDragAndDrop(root) {
    const scrollContainer = getScrollContainer(root);
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

        const monthCount = getMonthCount(root);
        const baseMonthWidth = getBaseMonthWidth(root);
        const scale = getCanvasScale(root);
        const dropzoneRect = dropzone.getBoundingClientRect();
        const logicalX =
          (scrollContainer.scrollLeft + event.clientX - dropzoneRect.left) / scale;
        const targetMonthIndex = clamp(
          Math.floor(logicalX / baseMonthWidth),
          0,
          monthCount - 1
        );
        const monthDelta = targetMonthIndex - dragPayload.startMonthIndex;

        if (monthDelta === 0) {
          return;
        }

        postMove(dragPayload.endpoint, dragPayload.nodeMid, monthDelta);
      });
    });
  }

  function handleCanvasWheel(event) {
    if (!(event.ctrlKey || event.metaKey)) {
      return;
    }

    const targetElement = normalizeTarget(event.target);
    if (!targetElement) {
      return;
    }

    const scrollContainer = targetElement.closest(
      "[data-work-planner-canvas-scroll]"
    );
    if (!scrollContainer || event.deltaY === 0) {
      return;
    }

    const root = getRootFromElement(scrollContainer);
    if (!root) {
      return;
    }

    event.preventDefault();
    zoomToScale(
      root,
      event.deltaY < 0 ? getZoomedInScale(root) : getZoomedOutScale(root),
      event.clientX,
      event.clientY
    );
  }

  function initialize() {
    const root = getRoot();
    if (!root) {
      return;
    }
    if (root.dataset.workPlannerInitialized === "true") {
      applyCanvasScale(root, getCanvasScale(root));
      return;
    }
    root.dataset.workPlannerInitialized = "true";

    const storedScale = Number.parseFloat(
      localStorage.getItem(ZOOM_STORAGE_KEY) || `${SCALE_DEFAULT}`
    );
    applyCanvasScale(root, storedScale);

    const documentSelector = root.querySelector(
      "[data-work-planner-default-document]"
    );
    if (documentSelector) {
      documentSelector.addEventListener("change", () => updateAddLinks(root));
      updateAddLinks(root);
    }

    const zoomInButton = root.querySelector("[data-work-planner-zoom-in]");
    const zoomOutButton = root.querySelector("[data-work-planner-zoom-out]");
    const zoomResetButton = root.querySelector("[data-work-planner-zoom-reset]");

    zoomInButton &&
      zoomInButton.addEventListener("click", () => {
        zoomToScale(root, getZoomedInScale(root));
      });

    zoomOutButton &&
      zoomOutButton.addEventListener("click", () => {
        zoomToScale(root, getZoomedOutScale(root));
      });

    zoomResetButton &&
      zoomResetButton.addEventListener("click", () => {
        zoomToScale(root, SCALE_DEFAULT);
      });

    bindDragAndDrop(root);
  }

  function scheduleInitialize() {
    requestAnimationFrame(() => {
      initialize();
    });
  }

  function installGlobalListeners() {
    if (window[GLOBAL_BIND_FLAG] === true) {
      return;
    }
    window[GLOBAL_BIND_FLAG] = true;

    document.addEventListener("wheel", handleCanvasWheel, { passive: false });
    window.addEventListener("resize", scheduleInitialize);
  }

  installGlobalListeners();

  document.addEventListener("DOMContentLoaded", scheduleInitialize);
  document.addEventListener("turbo:before-stream-render", scheduleInitialize);
  document.addEventListener("turbo:render", scheduleInitialize);
  document.addEventListener("turbo:frame-render", scheduleInitialize);
  document.addEventListener("turbo:load", scheduleInitialize);
})();
