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
    minNodeHeight: 32,
    minLabelWidth: 56,
    targetNodeArea: 1200,
  });
  const nodeWeights = new WeakMap();
  const nodeParents = new WeakMap();
  const syntheticGroupNavigation = new WeakMap();
  const renderableChildrenCache = new WeakMap();

  function indexNodeParents(node) {
    for (const child of node.children) {
      nodeParents.set(child, node);
      indexNodeParents(child);
    }
  }

  function getNodeAncestors(node) {
    const ancestors = [];
    let parent = nodeParents.get(node);
    while (parent !== undefined) {
      ancestors.unshift(parent);
      parent = nodeParents.get(parent);
    }
    return ancestors;
  }

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

  function enforceMinimumHeight(positionedItems, minimumHeight) {
    // Squarify may produce a vertical stack containing a very short tile next
    // to a tall sibling. Borrow only the required height from taller siblings
    // in that same stack, preserving its total rectangle and avoiding overlap.
    const stacks = new Map();
    for (const item of positionedItems) {
      const stackKey = `${item.x.toFixed(6)}:${item.width.toFixed(6)}`;
      const stack = stacks.get(stackKey) ?? [];
      stack.push(item);
      stacks.set(stackKey, stack);
    }

    for (const stack of stacks.values()) {
      stack.sort((left, right) => left.y - right.y);
      const runs = [];
      let run = [];
      for (const item of stack) {
        const previousItem = run[run.length - 1];
        if (
          previousItem !== undefined &&
          Math.abs(previousItem.y + previousItem.height - item.y) > 0.01
        ) {
          runs.push(run);
          run = [];
        }
        run.push(item);
      }
      if (run.length > 0) {
        runs.push(run);
      }

      for (const contiguousItems of runs) {
        const deficit = contiguousItems.reduce(
          (total, item) =>
            total + Math.max(0, minimumHeight - item.height),
          0,
        );
        if (deficit === 0) {
          continue;
        }
        const availableHeight = contiguousItems.reduce(
          (total, item) =>
            total + Math.max(0, item.height - minimumHeight),
          0,
        );
        if (availableHeight < deficit) {
          return false;
        }

        // Change the original weight-based geometry as little as possible:
        // short tiles receive only their deficit, while donors contribute in
        // proportion to the height they have above the minimum.
        let offsetY = contiguousItems[0].y;
        for (const item of contiguousItems) {
          const donorHeight = Math.max(0, item.height - minimumHeight);
          item.height =
            item.height < minimumHeight
              ? minimumHeight
              : item.height - deficit * (donorHeight / availableHeight);
          item.y = offsetY;
          offsetY += item.height;
        }
      }
    }
    return true;
  }

  function layoutConstrainedRows(
    children,
    pixelRectangle,
    minimumHeight,
    minimumWidth,
  ) {
    // Search row partitions of weight-sorted nodes. Fixed minimum dimensions
    // are assigned first; remaining width and height retain weight ratios.
    const maximumColumns = Math.floor(pixelRectangle.width / minimumWidth);
    const maximumRows = Math.floor(pixelRectangle.height / minimumHeight);
    if (maximumColumns === 0 || maximumRows === 0) {
      return null;
    }

    const sortedChildren = [...children].sort(
      (left, right) => getNodeWeight(right) - getNodeWeight(left),
    );
    const totalWeight = sortedChildren.reduce(
      (total, child) => total + getNodeWeight(child),
      0,
    );
    const minimumRows = Math.ceil(sortedChildren.length / maximumColumns);
    const maximumCandidateRows = Math.min(
      sortedChildren.length,
      maximumRows,
    );
    let bestCandidate = null;

    for (
      let numberOfRows = minimumRows;
      numberOfRows <= maximumCandidateRows;
      numberOfRows += 1
    ) {
      const weightedHeight =
        pixelRectangle.height - numberOfRows * minimumHeight;
      const memoizedPartitions = new Map();

      function findBestPartition(startIndex, remainingRows) {
        const memoKey = `${startIndex}:${remainingRows}`;
        if (memoizedPartitions.has(memoKey)) {
          return memoizedPartitions.get(memoKey);
        }
        if (remainingRows === 0) {
          return startIndex === sortedChildren.length
            ? { worstAspectRatio: 0, totalAspectRatio: 0, rows: [] }
            : null;
        }

        const remainingNodes = sortedChildren.length - startIndex;
        const maximumRowLength = Math.min(
          maximumColumns,
          remainingNodes - (remainingRows - 1),
        );
        let bestPartition = null;
        for (let rowLength = 1; rowLength <= maximumRowLength; rowLength += 1) {
          const rowNodes = sortedChildren.slice(
            startIndex,
            startIndex + rowLength,
          );
          const rowWeight = rowNodes.reduce(
            (total, node) => total + getNodeWeight(node),
            0,
          );
          const rowHeight =
            minimumHeight + weightedHeight * (rowWeight / totalWeight);
          const weightedWidth =
            pixelRectangle.width - rowLength * minimumWidth;
          let rowWorstAspectRatio = 0;
          let rowTotalAspectRatio = 0;
          for (const node of rowNodes) {
            const nodeWidth =
              minimumWidth +
              weightedWidth * (getNodeWeight(node) / rowWeight);
            const aspectRatio = Math.max(
              nodeWidth / rowHeight,
              rowHeight / nodeWidth,
            );
            rowWorstAspectRatio = Math.max(
              rowWorstAspectRatio,
              aspectRatio,
            );
            rowTotalAspectRatio += aspectRatio;
          }

          const suffix = findBestPartition(
            startIndex + rowLength,
            remainingRows - 1,
          );
          if (suffix === null) {
            continue;
          }
          const candidate = {
            worstAspectRatio: Math.max(
              rowWorstAspectRatio,
              suffix.worstAspectRatio,
            ),
            totalAspectRatio: rowTotalAspectRatio + suffix.totalAspectRatio,
            rows: [rowNodes, ...suffix.rows],
          };
          if (
            bestPartition === null ||
            candidate.worstAspectRatio < bestPartition.worstAspectRatio ||
            (candidate.worstAspectRatio === bestPartition.worstAspectRatio &&
              candidate.totalAspectRatio < bestPartition.totalAspectRatio)
          ) {
            bestPartition = candidate;
          }
        }
        memoizedPartitions.set(memoKey, bestPartition);
        return bestPartition;
      }

      const candidate = findBestPartition(0, numberOfRows);
      if (
        candidate !== null &&
        (bestCandidate === null ||
          candidate.worstAspectRatio < bestCandidate.worstAspectRatio ||
          (candidate.worstAspectRatio === bestCandidate.worstAspectRatio &&
            candidate.totalAspectRatio < bestCandidate.totalAspectRatio))
      ) {
        bestCandidate = candidate;
      }
    }
    if (bestCandidate === null) {
      return null;
    }

    const weightedHeight =
      pixelRectangle.height - bestCandidate.rows.length * minimumHeight;
    const positionedItems = [];
    let offsetY = 0;
    bestCandidate.rows.forEach((rowNodes, rowIndex) => {
      const rowWeight = rowNodes.reduce(
        (total, node) => total + getNodeWeight(node),
        0,
      );
      const rowHeight =
        rowIndex === bestCandidate.rows.length - 1
          ? pixelRectangle.height - offsetY
          : minimumHeight +
            weightedHeight * (rowWeight / totalWeight);
      const weightedWidth =
        pixelRectangle.width - rowNodes.length * minimumWidth;
      let offsetX = 0;
      rowNodes.forEach((node, columnIndex) => {
        const nodeWidth =
          columnIndex === rowNodes.length - 1
            ? pixelRectangle.width - offsetX
            : minimumWidth +
              weightedWidth * (getNodeWeight(node) / rowWeight);
        positionedItems.push({
          node,
          x: offsetX,
          y: offsetY,
          width: nodeWidth,
          height: rowHeight,
        });
        offsetX += nodeWidth;
      });
      offsetY += rowHeight;
    });
    return positionedItems;
  }

  function layoutChildren(
    children,
    pixelRectangle,
    minimumHeight,
    minimumWidth,
  ) {
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
    // Some valid squarify layouts split short nodes into strips with different
    // widths, so no single strip can donate height locally. In that case use
    // full-width rows when the complete sibling list physically fits.
    const constrainedItems = enforceMinimumHeight(
      positionedItems,
      minimumHeight,
    )
      ? positionedItems
      : layoutConstrainedRows(
          children,
          pixelRectangle,
          minimumHeight,
          minimumWidth,
        );
    if (constrainedItems === null) {
      return null;
    }
    // CSS percentages keep the computed pixel geometry responsive between
    // ResizeObserver updates.
    return constrainedItems.map((item) => ({
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

    const cachedChildren = renderableChildrenCache.get(node);
    if (
      cachedChildren !== undefined &&
      cachedChildren.maxDirectChildren === options.maxDirectChildren &&
      cachedChildren.targetGroupSize === options.targetGroupSize
    ) {
      return cachedChildren.children;
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
    // Groups are renderer-created navigation nodes. Keep their relation to the
    // source parent outside the serialized tree and give every group access to
    // only its synthetic siblings for horizontal navigation.
    groups.forEach((group, index) => {
      nodeParents.set(group, node);
      syntheticGroupNavigation.set(group, { groups, index });
    });
    renderableChildrenCache.set(node, {
      maxDirectChildren: options.maxDirectChildren,
      targetGroupSize: options.targetGroupSize,
      children: groups,
    });
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
    if (depth === 0) {
      // The focused node remains the visible geometry and header around its
      // children, but it is already open and therefore is not interactive.
      nodeElement.classList.add("tree-map-html__node--focused-root");
    }
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
    // An absent color means that presentation belongs to CSS. Inline colors
    // are reserved for values that carry data, such as coverage ratios.
    if (typeof node.color === "string") {
      surfaceElement.style.backgroundColor = node.color;
    }
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

    if (depth === 0) {
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
          options.minNodeHeight,
          options.minLabelWidth,
        );
        if (childRectangles === null) {
          nodeElement.dataset.truncated = "true";
          continue;
        }
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

  function applyPageGeometryProperties(rootElement, options) {
    // Gaps, padding, and header height form one geometry system for the page.
    // Individual node data, such as color, stays on the node surface instead.
    rootElement.style.setProperty(
      "--tree-map-html-node-gap-half",
      `${options.nodeGap / 2}px`,
    );
    rootElement.style.setProperty(
      "--tree-map-html-node-header-height",
      `${options.nodeHeaderHeight}px`,
    );
    rootElement.style.setProperty(
      "--tree-map-html-node-padding",
      `${options.nodePadding}px`,
    );
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

    const groupNavigationElement = document.createElement("div");
    groupNavigationElement.className = "tree-map-html__group-navigation";

    const previousGroupButton = document.createElement("button");
    previousGroupButton.className = "tree-map-html__previous-group";
    previousGroupButton.type = "button";
    previousGroupButton.textContent = "Previous group";
    groupNavigationElement.append(previousGroupButton);

    const nextGroupButton = document.createElement("button");
    nextGroupButton.className = "tree-map-html__next-group";
    nextGroupButton.type = "button";
    nextGroupButton.textContent = "Next group";
    groupNavigationElement.append(nextGroupButton);
    toolbarElement.append(groupNavigationElement);
    sectionElement.append(toolbarElement);

    const ancestorsElement = document.createElement("nav");
    ancestorsElement.className = "tree-map-html__ancestors";
    ancestorsElement.setAttribute("aria-label", "Tree map ancestors");
    sectionElement.append(ancestorsElement);

    const canvasElement = document.createElement("div");
    canvasElement.className = "tree-map-html__canvas";
    sectionElement.append(canvasElement);
    rootElement.append(sectionElement);

    indexNodeParents(treeMap.root);
    const visitHistory = [treeMap.root];

    function navigateTo(node) {
      const focusedNode = visitHistory[visitHistory.length - 1];
      if (node !== focusedNode) {
        visitHistory.push(node);
        renderFocusedNode();
      }
    }

    function renderAncestors(focusedNode) {
      ancestorsElement.replaceChildren();
      for (const ancestor of getNodeAncestors(focusedNode)) {
        // create button
        const ancestorButton = document.createElement("button");
        ancestorButton.className = "tree-map-html__ancestor";
        ancestorButton.type = "button";
        // create label
        const labelElement = document.createElement("span");
        labelElement.className = "tree-map-html__label";
        labelElement.textContent = ancestor.label;
        ancestorButton.append(labelElement);
        // place button
        ancestorButton.addEventListener("click", () => navigateTo(ancestor));
        ancestorsElement.append(ancestorButton);
      }
    }

    function renderGroupNavigation(focusedNode) {
      const navigation = syntheticGroupNavigation.get(focusedNode);
      groupNavigationElement.hidden = navigation === undefined;
      if (navigation === undefined) {
        return;
      }
      previousGroupButton.disabled = navigation.index === 0;
      nextGroupButton.disabled = navigation.index === navigation.groups.length - 1;
      previousGroupButton.onclick = () =>
        navigateTo(navigation.groups[navigation.index - 1]);
      nextGroupButton.onclick = () =>
        navigateTo(navigation.groups[navigation.index + 1]);
    }

    function renderFocusedNode() {
      const focusedNode = visitHistory[visitHistory.length - 1];
      const canvasRectangle = canvasElement.getBoundingClientRect();
      canvasElement.replaceChildren();
      backButton.disabled = visitHistory.length === 1;
      renderAncestors(focusedNode);
      renderGroupNavigation(focusedNode);

      canvasElement.append(
        renderNodeTree(
          focusedNode,
          canvasRectangle,
          navigateTo,
          options,
        ),
      );
    }

    backButton.addEventListener("click", () => {
      if (visitHistory.length > 1) {
        visitHistory.pop();
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
    applyPageGeometryProperties(rootElement, options);
    const treeMapData = JSON.parse(dataElement.textContent);
    for (const treeMap of treeMapData.tree_maps) {
      createTreeMap(treeMap, rootElement, options);
    }
  }

  renderTreeMaps();
})();
