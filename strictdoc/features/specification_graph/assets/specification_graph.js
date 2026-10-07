// Interactivity of the specification graph screen. The script works on the
// inline SVG of the generator: it reads the data-* attributes of the nodes
// and the relations.

(() => {
  const PREFIX = "specification-graph";

  const createGraphController = (graph, infoPanel) => {
    const nodes = [...graph.querySelectorAll(`.${PREFIX}-node`)];
    const edges = [...graph.querySelectorAll(`.${PREFIX}-edge`)];
    const nodesById = new Map(nodes.map((node) => [node.dataset.nodeId, node]));
    // The generator keeps <title> for the SVG without this script: it is the
    // only way to see a cut title there. On the screen, the Shift panel shows
    // the full title, and the native tooltip of <title> would cover it, so
    // the title moves to an attribute.
    nodes.forEach((node) => {
      const title = node.querySelector(":scope > title");
      if (title !== null) {
        node.dataset.nodeTitle = title.textContent;
        title.remove();
      }
    });
    const edgesByNodeId = new Map();
    edges.forEach((edge) => {
      [edge.dataset.sourceId, edge.dataset.targetId].forEach((nodeId) => {
        if (!edgesByNodeId.has(nodeId)) {
          edgesByNodeId.set(nodeId, []);
        }
        edgesByNodeId.get(nodeId).push(edge);
      });
    });
    const infoTable = infoPanel?.querySelector(`.${PREFIX}-info-table`);
    const contentBounds = {
      x: graph.viewBox.baseVal.x,
      y: graph.viewBox.baseVal.y,
      width: graph.viewBox.baseVal.width,
      height: graph.viewBox.baseVal.height,
    };
    // The SVG fills the viewport; the viewBox sets the scale and the offset.
    graph.removeAttribute("width");
    graph.removeAttribute("height");
    let viewport = {...contentBounds};
    let oneToOneViewport = {...contentBounds};
    let panStart = null;
    let spacePressed = false;
    let onZoomChange = () => {};
    // Hover highlight, shown while the pointer is on a node or a relation.
    let activeNodeId = null;
    let activeEdge = null;
    // Selection, kept until a click elsewhere.
    let selectedNodeId = null;
    let selectedEdge = null;
    let pressPoint = null;
    // The last pointer move over a node: Shift pressed without a move shows
    // the panel at once.
    let lastNodeMove = null;

    const viewportSize = () => {
      const bounds = graph.getBoundingClientRect();
      return {width: bounds.width, height: bounds.height};
    };
    const scale = () => {
      const size = viewportSize();
      return Math.min(size.width / viewport.width, size.height / viewport.height);
    };
    const applyViewport = () => {
      graph.setAttribute(
        "viewBox",
        `${viewport.x} ${viewport.y} ${viewport.width} ${viewport.height}`,
      );
      onZoomChange(scale());
    };
    const contentCenter = () => ({
      x: contentBounds.x + contentBounds.width / 2,
      y: contentBounds.y + contentBounds.height / 2,
    });
    const viewAround = (center, factor) => {
      const size = viewportSize();
      return {
        x: center.x - size.width / factor / 2,
        y: center.y - size.height / factor / 2,
        width: size.width / factor,
        height: size.height / factor,
      };
    };
    const resetView = () => {
      oneToOneViewport = viewAround(contentCenter(), 1);
      viewport = {...oneToOneViewport};
      applyViewport();
    };
    const fitView = () => {
      const size = viewportSize();
      const factor = Math.min(
        size.width / contentBounds.width,
        size.height / contentBounds.height,
      );
      viewport = viewAround(contentCenter(), factor);
      applyViewport();
    };
    const zoomAt = (factor, centerX, centerY) => {
      const nextWidth = Math.min(
        oneToOneViewport.width * 20,
        Math.max(oneToOneViewport.width * 0.05, viewport.width * factor),
      );
      const appliedFactor = nextWidth / viewport.width;
      viewport = {
        x: centerX - (centerX - viewport.x) * appliedFactor,
        y: centerY - (centerY - viewport.y) * appliedFactor,
        width: nextWidth,
        height: viewport.height * appliedFactor,
      };
      applyViewport();
    };
    const zoomStep = (zoomIn) => {
      zoomAt(
        zoomIn ? 0.8 : 1.25,
        viewport.x + viewport.width / 2,
        viewport.y + viewport.height / 2,
      );
    };

    // Highlight: the relations of a node, or one relation, and the nodes
    // at their ends. The other relations fade. The hover shows over the
    // selection; when the pointer leaves, the selection shows again.
    const refreshHighlights = () => {
      graph
        .querySelectorAll(".is-highlighted, .is-selected")
        .forEach((element) => {
          element.classList.remove("is-highlighted", "is-selected");
        });
      const isHover = activeNodeId !== null || activeEdge !== null;
      const nodeId = isHover ? activeNodeId : selectedNodeId;
      const edge = isHover ? activeEdge : selectedEdge;
      const highlightedEdges = edge !== null
        ? [edge]
        : edgesByNodeId.get(nodeId) ?? [];
      if (nodeId !== null) {
        nodesById.get(nodeId)?.classList.add("is-highlighted");
      }
      highlightedEdges.forEach((edge_) => {
        edge_.classList.add("is-highlighted");
        nodesById.get(edge_.dataset.sourceId)?.classList.add("is-highlighted");
        nodesById.get(edge_.dataset.targetId)?.classList.add("is-highlighted");
      });
      if (selectedNodeId !== null) {
        nodesById.get(selectedNodeId)?.classList.add("is-selected");
      }
      selectedEdge?.classList.add("is-selected");
      graph.classList.toggle("has-highlight", nodeId !== null || edge !== null);
    };

    const hideInfoPanel = () => {
      if (infoPanel) {
        infoPanel.hidden = true;
      }
    };
    const showInfoPanel = (node, event) => {
      if (!infoPanel || !infoTable) {
        return;
      }
      const details = JSON.parse(node.dataset.nodeDetails ?? "[]");
      const rows = [["Title", node.dataset.nodeTitle], ...details]
        .filter(([, value]) => value !== null && value !== undefined && value !== "");
      infoTable.replaceChildren();
      rows.forEach(([name, value]) => {
        const term = document.createElement("dt");
        term.textContent = name;
        const description = document.createElement("dd");
        description.textContent = value;
        infoTable.append(term, description);
      });
      infoPanel.hidden = false;
      const panelBounds = infoPanel.getBoundingClientRect();
      infoPanel.style.left = `${Math.max(
        8,
        Math.min(event.clientX + 12, window.innerWidth - panelBounds.width - 8),
      )}px`;
      infoPanel.style.top = `${Math.max(
        8,
        Math.min(event.clientY + 12, window.innerHeight - panelBounds.height - 8),
      )}px`;
    };

    // A frame takes Shift+hover and Shift+click on its title only: the rest
    // of the frame is the space of its children.
    const isTitleEvent = (node, event) => (
      !node.classList.contains(`${PREFIX}-node--composite`) ||
      event.target.closest(`.${PREFIX}-node__title-box`) !== null
    );

    nodes.forEach((node) => {
      const nodeId = node.dataset.nodeId;
      node.addEventListener("pointerenter", () => {
        activeNodeId = nodeId;
        refreshHighlights();
      });
      node.addEventListener("pointerleave", () => {
        if (activeNodeId === nodeId) {
          activeNodeId = null;
          refreshHighlights();
        }
        if (lastNodeMove?.node === node) {
          lastNodeMove = null;
        }
        hideInfoPanel();
      });
      node.addEventListener("pointermove", (event) => {
        lastNodeMove = {node, event};
        if (event.shiftKey && !spacePressed && isTitleEvent(node, event)) {
          showInfoPanel(node, event);
        } else {
          hideInfoPanel();
        }
      });
      node.addEventListener("click", (event) => {
        if (!event.shiftKey || spacePressed || !isTitleEvent(node, event)) {
          return;
        }
        event.preventDefault();
        if (node.dataset.nodeLink !== undefined) {
          window.open(node.dataset.nodeLink, "_blank");
        }
      });
    });
    edges.forEach((edge) => {
      edge.addEventListener("pointerenter", () => {
        activeEdge = edge;
        refreshHighlights();
      });
      edge.addEventListener("pointerleave", () => {
        if (activeEdge === edge) {
          activeEdge = null;
          refreshHighlights();
        }
      });
    });

    // A click on a node or a relation selects it; a click on the free space,
    // or on a frame outside its title, clears the selection. A press that
    // moves the pointer before the release is a drag, not a click.
    graph.addEventListener("pointerdown", (event) => {
      pressPoint = {x: event.clientX, y: event.clientY};
    });
    graph.addEventListener("click", (event) => {
      if (event.shiftKey || spacePressed) {
        return;
      }
      if (
        pressPoint !== null &&
        Math.hypot(event.clientX - pressPoint.x, event.clientY - pressPoint.y) > 4
      ) {
        return;
      }
      const edge = event.target.closest(`.${PREFIX}-edge`);
      const node = event.target.closest(`.${PREFIX}-node`);
      selectedEdge = edge;
      selectedNodeId = edge === null && node !== null && isTitleEvent(node, event)
        ? node.dataset.nodeId
        : null;
      refreshHighlights();
    });

    graph.addEventListener("wheel", (event) => {
      const delta = event.deltaY !== 0 ? event.deltaY : event.deltaX;
      if (delta === 0) {
        return;
      }
      event.preventDefault();
      const bounds = graph.getBoundingClientRect();
      // The SVG keeps the aspect ratio: map the pointer through the scale.
      const factor = scale();
      const offsetX = (bounds.width - viewport.width * factor) / 2;
      const offsetY = (bounds.height - viewport.height * factor) / 2;
      const centerX = viewport.x + (event.clientX - bounds.left - offsetX) / factor;
      const centerY = viewport.y + (event.clientY - bounds.top - offsetY) / factor;
      zoomAt(delta < 0 ? 0.9 : 1.1, centerX, centerY);
    }, {passive: false});

    graph.addEventListener("pointerdown", (event) => {
      if (!spacePressed || event.button !== 0) {
        return;
      }
      event.preventDefault();
      graph.setPointerCapture(event.pointerId);
      panStart = {
        pointerX: event.clientX,
        pointerY: event.clientY,
        viewportX: viewport.x,
        viewportY: viewport.y,
      };
      graph.classList.add("is-panning");
    });
    graph.addEventListener("pointermove", (event) => {
      if (panStart === null) {
        return;
      }
      const factor = scale();
      viewport.x = panStart.viewportX - (event.clientX - panStart.pointerX) / factor;
      viewport.y = panStart.viewportY - (event.clientY - panStart.pointerY) / factor;
      applyViewport();
    });
    const stopPanning = (event) => {
      if (panStart === null) {
        return;
      }
      panStart = null;
      graph.classList.remove("is-panning");
      if (graph.hasPointerCapture(event.pointerId)) {
        graph.releasePointerCapture(event.pointerId);
      }
    };
    graph.addEventListener("pointerup", stopPanning);
    graph.addEventListener("pointercancel", stopPanning);

    const setShiftPressed = (pressed) => {
      if (
        pressed &&
        lastNodeMove !== null &&
        !spacePressed &&
        isTitleEvent(lastNodeMove.node, lastNodeMove.event)
      ) {
        showInfoPanel(lastNodeMove.node, lastNodeMove.event);
      } else {
        hideInfoPanel();
      }
    };

    const setSpacePressed = (pressed) => {
      spacePressed = pressed;
      graph.classList.toggle("is-pan-ready", pressed);
      if (!pressed) {
        graph.classList.remove("is-panning");
        panStart = null;
      }
    };

    resetView();
    if (
      contentBounds.width > oneToOneViewport.width ||
      contentBounds.height > oneToOneViewport.height
    ) {
      fitView();
    }

    return {
      graph,
      resetView,
      fitView,
      zoomStep,
      setSpacePressed,
      setShiftPressed,
      hideInfoPanel,
      setRoutingDebug: (enabled) => {
        graph.classList.toggle("show-routing-debug", enabled);
      },
      setZoomListener: (listener) => {
        onZoomChange = listener;
        listener(scale());
      },
    };
  };

  const initializeScreen = (screen) => {
    const select = screen.querySelector("[data-specification-graph-view-select]");
    const toolbox = screen.querySelector(`.${PREFIX}-toolbox`);
    const zoomOutput = toolbox?.querySelector(`.${PREFIX}-toolbox__zoom`);
    const debugToggle = toolbox?.querySelector("[data-graph-routing-debug]");
    const infoPanel = screen.querySelector(`.${PREFIX}-info-panel`);
    const views = [...screen.querySelectorAll("[data-specification-graph-view]")];
    const controllers = new Map();
    let active = null;

    const activateView = () => {
      active?.hideInfoPanel();
      active = null;
      views.forEach((view) => {
        view.hidden = view.dataset.specificationGraphView !== select.value;
        if (view.hidden) {
          return;
        }
        const graph = view.querySelector(`svg.${PREFIX}`);
        if (graph === null) {
          return;
        }
        // A hidden view has no size: build its controller when it shows.
        if (!controllers.has(view)) {
          controllers.set(view, createGraphController(graph, infoPanel));
        }
        active = controllers.get(view);
        active.setRoutingDebug(debugToggle?.checked ?? false);
        active.setZoomListener((value) => {
          if (zoomOutput) {
            zoomOutput.value = `${Math.round(value * 100)}%`;
          }
        });
      });
    };

    toolbox?.querySelectorAll("[data-graph-action]").forEach((button) => {
      button.addEventListener("click", () => {
        const action = button.dataset.graphAction;
        if (action === "zoom-in" || action === "zoom-out") {
          active?.zoomStep(action === "zoom-in");
        } else if (action === "reset") {
          active?.resetView();
        } else if (action === "fit") {
          active?.fitView();
        }
      });
    });
    debugToggle?.addEventListener("change", () => {
      active?.setRoutingDebug(debugToggle.checked);
    });
    select?.addEventListener("change", activateView);

    const isEditable = () => {
      const element = document.activeElement;
      return element !== null && (
        element.tagName === "INPUT" ||
        element.tagName === "SELECT" ||
        element.tagName === "TEXTAREA" ||
        element.isContentEditable
      );
    };
    document.addEventListener("keydown", (event) => {
      if (active === null || isEditable() || document.querySelector("[data-js-modal]")) {
        return;
      }
      if (event.key === "Shift") {
        active.setShiftPressed(true);
      } else if (event.key === " ") {
        event.preventDefault();
        active.setSpacePressed(true);
      } else if (event.key === "0") {
        active.resetView();
      } else if (event.key === "f" || event.key === "F") {
        active.fitView();
      }
    });
    document.addEventListener("keyup", (event) => {
      if (event.key === "Shift") {
        active?.setShiftPressed(false);
      } else if (event.key === " ") {
        active?.setSpacePressed(false);
      }
    });
    window.addEventListener("blur", () => {
      active?.setSpacePressed(false);
      active?.hideInfoPanel();
    });

    if (select) {
      activateView();
    }
  };

  const start = () => {
    document
      .querySelectorAll(`.${PREFIX}-screen`)
      .forEach(initializeScreen);
  };
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();
