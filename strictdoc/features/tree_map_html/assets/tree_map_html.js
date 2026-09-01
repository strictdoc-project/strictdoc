// @relation(SDOC-SRS-157, scope=file)

(function () {
  "use strict";

  // Keep renderer policy in one object so callers can provide project-specific
  // values later without changing the layout functions.
  const DEFAULT_RENDER_OPTIONS = Object.freeze({
    nodeHeaderHeight: 20,
    nodeGap: 4,
    nodePadding: 4,
    maxRenderedDepth: 4,
    maxRenderedNodes: 500,
    maxDirectChildren: 128,
    targetGroupSize: 100,
    minChildrenArea: 2500,
    minNodeArea: 16,
    minLabelWidth: 56,
    targetNodeArea: 1200,
  });
  const nodeWeights = new WeakMap();

  function getNodeWeight(node) {
    const cachedWeight = nodeWeights.get(node);
    if (cachedWeight !== undefined) {
      return cachedWeight;
    }

    if (node.weight > 0) {
      nodeWeights.set(node, node.weight);
      return node.weight;
    }
    const nodeWeight = node.children.reduce(
      (totalWeight, child) => totalWeight + getNodeWeight(child),
      0,
    );
    nodeWeights.set(node, nodeWeight);
    return nodeWeight;
  }

  function getWorstAspectRatio(row, shortSide) {
    // Squarify adds an item only while it improves the worst-shaped tile in
    // the current row. Lower values mean more balanced rectangles.
    if (row.length === 0) {
      return Number.POSITIVE_INFINITY;
    }

    const rowArea = row.reduce((total, item) => total + item.area, 0);
    const largestArea = Math.max(...row.map((item) => item.area));
    const smallestArea = Math.min(...row.map((item) => item.area));
    const sideSquared = shortSide * shortSide;
    const areaSquared = rowArea * rowArea;
    return Math.max(
      (sideSquared * largestArea) / areaSquared,
      areaSquared / (sideSquared * smallestArea),
    );
  }

  function positionRow(row, rectangle, positionedItems) {
    // Consume a strip from the longest side of the remaining rectangle. Each
    // item keeps its exact proportional area inside that strip.
    const rowArea = row.reduce((total, item) => total + item.area, 0);

    if (rectangle.width >= rectangle.height) {
      const rowWidth = rowArea / rectangle.height;
      let offsetY = rectangle.y;
      for (const item of row) {
        const itemHeight = item.area / rowWidth;
        positionedItems.push({
          node: item.node,
          x: rectangle.x,
          y: offsetY,
          width: rowWidth,
          height: itemHeight,
        });
        offsetY += itemHeight;
      }
      rectangle.x += rowWidth;
      rectangle.width -= rowWidth;
      return;
    }

    const rowHeight = rowArea / rectangle.width;
    let offsetX = rectangle.x;
    for (const item of row) {
      const itemWidth = item.area / rowHeight;
      positionedItems.push({
        node: item.node,
        x: offsetX,
        y: rectangle.y,
        width: itemWidth,
        height: rowHeight,
      });
      offsetX += itemWidth;
    }
    rectangle.y += rowHeight;
    rectangle.height -= rowHeight;
  }

  function layoutChildren(children, pixelRectangle) {
    // Squarify must see the real aspect ratio. Calculating in a square and
    // stretching the result later produces long strips in narrow containers.
    const totalWeight = children.reduce(
      (total, child) => total + getNodeWeight(child),
      0,
    );
    if (
      totalWeight <= 0 ||
      pixelRectangle.width <= 0 ||
      pixelRectangle.height <= 0
    ) {
      return [];
    }

    const availableArea = pixelRectangle.width * pixelRectangle.height;
    const remainingItems = children
      .map((node) => ({
        node,
        area: (getNodeWeight(node) / totalWeight) * availableArea,
      }))
      .sort((left, right) => right.area - left.area);
    const rectangle = {
      x: 0,
      y: 0,
      width: pixelRectangle.width,
      height: pixelRectangle.height,
    };
    const positionedItems = [];
    let row = [];

    while (remainingItems.length > 0) {
      const nextItem = remainingItems[0];
      const shortSide = Math.min(rectangle.width, rectangle.height);
      const candidateRow = [...row, nextItem];
      if (
        row.length === 0 ||
        getWorstAspectRatio(candidateRow, shortSide) <=
          getWorstAspectRatio(row, shortSide)
      ) {
        row = candidateRow;
        remainingItems.shift();
      } else {
        positionRow(row, rectangle, positionedItems);
        row = [];
      }
    }
    if (row.length > 0) {
      positionRow(row, rectangle, positionedItems);
    }
    // CSS percentages keep the computed pixel geometry responsive between
    // ResizeObserver updates.
    return positionedItems.map((item) => ({
      node: item.node,
      x: (item.x / pixelRectangle.width) * 100,
      y: (item.y / pixelRectangle.height) * 100,
      width: (item.width / pixelRectangle.width) * 100,
      height: (item.height / pixelRectangle.height) * 100,
    }));
  }

  function applyRectangle(nodeElement, rectangle) {
    nodeElement.style.left = `${rectangle.x}%`;
    nodeElement.style.top = `${rectangle.y}%`;
    nodeElement.style.width = `${rectangle.width}%`;
    nodeElement.style.height = `${rectangle.height}%`;
  }

  function getPixelRectangle(parentRectangle, rectangle) {
    // Visibility and level-of-detail decisions use pixels, not percentages.
    return {
      width: (parentRectangle.width * rectangle.width) / 100,
      height: (parentRectangle.height * rectangle.height) / 100,
    };
  }

  function getChildrenPixelRectangle(pixelRectangle, options) {
    // The transparent positioning box contains an inset visual surface. Child
    // layout starts after both the surface gap and the content padding.
    const contentInset = options.nodeGap / 2 + options.nodePadding;
    return {
      width: Math.max(0, pixelRectangle.width - contentInset * 2),
      height: Math.max(
        0,
        pixelRectangle.height -
          options.nodeHeaderHeight -
          contentInset * 2,
      ),
    };
  }

  function calculateSyntheticGroupSize(numberOfChildren, targetGroupSize) {
    // Calculate the minimum number of groups, then distribute children
    // evenly. This avoids one very small remainder group at the end.
    const numberOfGroups = Math.ceil(numberOfChildren / targetGroupSize);
    return Math.ceil(numberOfChildren / numberOfGroups);
  }

  function getRenderableChildren(node, options) {
    if (node.children.length <= options.maxDirectChildren) {
      return node.children;
    }

    // Synthetic group membership depends only on the hard limit. Resizing the
    // canvas cannot move a source node from one group to another.
    const groupSize = calculateSyntheticGroupSize(
      node.children.length,
      options.targetGroupSize,
    );
    const groups = [];
    for (let index = 0; index < node.children.length; index += groupSize) {
      const children = node.children.slice(index, index + groupSize);
      const firstChildNumber = index + 1;
      const lastChildNumber = index + children.length;
      groups.push({
        label: `Items ${firstChildNumber}-${lastChildNumber}`,
        weight: 0,
        color: node.color,
        children,
        isSyntheticGroup: true,
      });
    }
    return groups;
  }

  function hasEnoughAreaForChildren(
    childrenPixelRectangle,
    numberOfChildren,
    options,
  ) {
    const availableArea =
      childrenPixelRectangle.width * childrenPixelRectangle.height;
    const requiredArea = numberOfChildren * options.targetNodeArea;
    return availableArea >= requiredArea;
  }

  function createNodeElement(
    node,
    depth,
    rectangle,
    pixelRectangle,
    zoomIntoNode,
    options,
  ) {
    const renderableChildren = getRenderableChildren(node, options);
    const nodeElement = document.createElement("div");
    nodeElement.className = "tree-map-html__node";
    nodeElement.dataset.depth = depth;
    // The immediate children of the focused root are the current level. Deeper
    // nodes provide context and use a quieter visual treatment.
    if (depth === 1) {
      nodeElement.classList.add("tree-map-html__node--current-level");
    }
    nodeElement.dataset.childCount = renderableChildren.length;
    nodeElement.dataset.sourceChildCount = node.children.length;
    if (node.isSyntheticGroup === true) {
      nodeElement.dataset.syntheticGroup = "true";
    }
    const nodeWeight = getNodeWeight(node);
    nodeElement.dataset.weight = nodeWeight;
    nodeElement.title = `${node.label} (${nodeWeight})`;
    applyRectangle(nodeElement, rectangle);

    // Keep layout geometry on the transparent outer node. The surface owns
    // color and content, leaving room for links and actions without changing
    // the absolute positioning contract.
    const surfaceElement = document.createElement("div");
    surfaceElement.className = "tree-map-html__node-surface";
    surfaceElement.style.backgroundColor = node.color;
    nodeElement.append(surfaceElement);

    const headerElement = document.createElement("div");
    headerElement.className = "tree-map-html__node-header";
    surfaceElement.append(headerElement);
    if (
      pixelRectangle.width >= options.minLabelWidth &&
      pixelRectangle.height >= options.nodeHeaderHeight
    ) {
      const labelElement = document.createElement("span");
      labelElement.className = "tree-map-html__label";
      labelElement.textContent = node.label;
      headerElement.append(labelElement);
    }

    if (node.children.length === 0) {
      nodeElement.classList.add("tree-map-html__node--leaf");
      return {
        node,
        nodeElement,
        depth,
        pixelRectangle,
        renderableChildren,
      };
    }

    nodeElement.classList.add("tree-map-html__node--branch");
    nodeElement.setAttribute("role", "button");
    nodeElement.tabIndex = 0;
    nodeElement.addEventListener("click", (event) => {
      event.stopPropagation();
      zoomIntoNode(node);
    });
    nodeElement.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        event.stopPropagation();
        zoomIntoNode(node);
      }
    });

    return {
      node,
      nodeElement,
      depth,
      pixelRectangle,
      renderableChildren,
    };
  }

  function renderNodeTree(
    focusedNode,
    canvasRectangle,
    zoomIntoNode,
    options,
  ) {
    const rootRecord = createNodeElement(
      focusedNode,
      0,
      { x: 0, y: 0, width: 100, height: 100 },
      {
        width: canvasRectangle.width,
        height: canvasRectangle.height,
      },
      zoomIntoNode,
      options,
    );
    let renderedNodeCount = 1;
    let currentLevel = [rootRecord];

    while (currentLevel.length > 0) {
      const nextLevel = [];
      // Process one hierarchy level at a time. Larger visible branches get
      // the remaining budget first without letting a deep branch starve peers.
      const expansionCandidates = currentLevel
        .filter((record) => record.renderableChildren.length > 0)
        .sort(
          (left, right) =>
            right.pixelRectangle.width * right.pixelRectangle.height -
            left.pixelRectangle.width * left.pixelRectangle.height,
        );

      for (const record of expansionCandidates) {
        const {
          node,
          nodeElement,
          depth,
          pixelRectangle,
          renderableChildren,
        } = record;
        // A group is a navigation tile in its parent's overview. Expanding it
        // there would make equal groups compete for the shared DOM budget.
        if (node.isSyntheticGroup === true && node !== focusedNode) {
          nodeElement.dataset.truncated = "true";
          continue;
        }
        const childrenPixelRectangle = getChildrenPixelRectangle(
          pixelRectangle,
          options,
        );
        if (
          depth >= options.maxRenderedDepth ||
          childrenPixelRectangle.width * childrenPixelRectangle.height <
            options.minChildrenArea ||
          !hasEnoughAreaForChildren(
            childrenPixelRectangle,
            renderableChildren.length,
            options,
          )
        ) {
          nodeElement.dataset.truncated = "true";
          continue;
        }

        const childRectangles = layoutChildren(
          renderableChildren,
          childrenPixelRectangle,
        );
        const childRecords = childRectangles.map((childRectangle) => {
          const childPixelRectangle = getPixelRectangle(
            childrenPixelRectangle,
            childRectangle,
          );
          return {
            childRectangle,
            childPixelRectangle,
          };
        });
        const childrenFit = childRecords.every(
          ({ childPixelRectangle }) =>
            childPixelRectangle.width * childPixelRectangle.height >=
            options.minNodeArea,
        );
        // Never render a partial sibling list. A collapsed parent still
        // represents the complete weight and remains available for zoom.
        if (
          !childrenFit ||
          renderedNodeCount + childRecords.length > options.maxRenderedNodes
        ) {
          nodeElement.dataset.truncated = "true";
          continue;
        }

        const childrenElement = document.createElement("div");
        childrenElement.className = "tree-map-html__children";
        for (const { childRectangle, childPixelRectangle } of childRecords) {
          const childRecord = createNodeElement(
            childRectangle.node,
            depth + 1,
            childRectangle,
            childPixelRectangle,
            zoomIntoNode,
            options,
          );
          childrenElement.append(childRecord.nodeElement);
          nextLevel.push(childRecord);
          renderedNodeCount += 1;
        }
        nodeElement.append(childrenElement);
      }
      currentLevel = nextLevel;
    }

    return rootRecord.nodeElement;
  }

  function createTreeMap(treeMap, rootElement, options) {
    const sectionElement = document.createElement("section");
    sectionElement.className = "tree-map-html__section";

    const titleElement = document.createElement("h2");
    titleElement.className = "tree-map-html__title";
    titleElement.textContent = treeMap.title;
    sectionElement.append(titleElement);

    const toolbarElement = document.createElement("div");
    toolbarElement.className = "tree-map-html__toolbar";

    const backButton = document.createElement("button");
    backButton.className = "tree-map-html__back";
    backButton.type = "button";
    backButton.textContent = "Back";
    toolbarElement.append(backButton);

    const locationElement = document.createElement("span");
    locationElement.className = "tree-map-html__location";
    locationElement.dataset.testid = "tree-map-html-location";
    toolbarElement.append(locationElement);
    sectionElement.append(toolbarElement);

    const canvasElement = document.createElement("div");
    canvasElement.className = "tree-map-html__canvas";
    canvasElement.style.setProperty(
      "--tree-map-html-node-header-height",
      `${options.nodeHeaderHeight}px`,
    );
    // Adjacent transparent positioning boxes touch. Their inset surfaces leave
    // half a gap on each side without introducing CSS margins.
    canvasElement.style.setProperty(
      "--tree-map-html-node-gap-half",
      `${options.nodeGap / 2}px`,
    );
    canvasElement.style.setProperty(
      "--tree-map-html-node-padding",
      `${options.nodePadding}px`,
    );
    sectionElement.append(canvasElement);
    rootElement.append(sectionElement);

    const nodePath = [treeMap.root];

    function renderFocusedNode() {
      const focusedNode = nodePath[nodePath.length - 1];
      const canvasRectangle = canvasElement.getBoundingClientRect();
      canvasElement.replaceChildren();
      locationElement.textContent = nodePath
        .map((node) => node.label)
        .join(" / ");
      backButton.disabled = nodePath.length === 1;

      const zoomIntoNode = (node) => {
        if (node === focusedNode) {
          return;
        }
        nodePath.push(node);
        renderFocusedNode();
      };
      canvasElement.append(
        renderNodeTree(
          focusedNode,
          canvasRectangle,
          zoomIntoNode,
          options,
        ),
      );
    }

    backButton.addEventListener("click", () => {
      if (nodePath.length > 1) {
        nodePath.pop();
        renderFocusedNode();
      }
    });

    let canvasWidth = 0;
    let canvasHeight = 0;
    const resizeObserver = new ResizeObserver((entries) => {
      const { width, height } = entries[0].contentRect;
      if (width !== canvasWidth || height !== canvasHeight) {
        canvasWidth = width;
        canvasHeight = height;
        renderFocusedNode();
      }
    });
    resizeObserver.observe(canvasElement);
    renderFocusedNode();
  }

  function renderTreeMaps(renderOptions = {}) {
    const rootElement = document.getElementById("tree-map-html-root");
    const dataElement = document.getElementById("tree-map-html-data");
    if (rootElement === null || dataElement === null) {
      return;
    }

    const options = {
      ...DEFAULT_RENDER_OPTIONS,
      ...renderOptions,
    };
    const treeMapData = JSON.parse(dataElement.textContent);
    for (const treeMap of treeMapData.tree_maps) {
      createTreeMap(treeMap, rootElement, options);
    }
  }

  renderTreeMaps();
})();
