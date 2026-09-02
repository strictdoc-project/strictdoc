// @relation(SDOC-SRS-157, scope=file)

(function () {
  "use strict";

  // Keep renderer policy in one object so callers can provide project-specific
  // values later without changing the layout functions.
  const DEFAULT_RENDER_OPTIONS = Object.freeze({
    nodeHeaderHeight: 20,
    nodeGap: 4,
    nodePadding: 4,
    // The focused node always shows its direct children. Disable this option
    // to render those child folders as closed tiles without nested previews.
    showCollapsedFolderContent: false,
    maxRenderedDepth: 4,
    maxRenderedNodes: 500,
    maxDirectChildren: 128,
    targetGroupSize: 100,
    minChildrenArea: 2500,
    minNodeArea: 16,
    minNodeHeight: 32,
    minLabelWidth: 56,
    targetNodeArea: 1200,
    // 1 restores classic square-oriented squarify behavior. Values above 1
    // prefer wider rectangles for text without forcing a fixed orientation.
    targetNodeAspectRatio: 1.6,
  });
  const CSS_CLASSES = Object.freeze({
    ancestor: "tree-map-html__ancestor",
    ancestors: "tree-map-html__ancestors",
    back: "tree-map-html__back",
    canvas: "tree-map-html__canvas",
    children: "tree-map-html__children",
    groupNavigation: "tree-map-html__group-navigation",
    groupPosition: "tree-map-html__group-position",
    label: "tree-map-html__label",
    labelAncestor: "tree-map-html__label--ancestor",
    labelBranch: "tree-map-html__label--branch",
    labelLeaf: "tree-map-html__label--leaf",
    labelRoot: "tree-map-html__label--root",
    historyBreadcrumb: "tree-map-html__history-breadcrumb",
    nextGroup: "tree-map-html__next-group",
    node: "tree-map-html__node",
    nodeBranch: "tree-map-html__node--branch",
    nodeCurrentLevel: "tree-map-html__node--current-level",
    nodeFocusedRoot: "tree-map-html__node--focused-root",
    nodeHeader: "tree-map-html__node-header",
    nodeLeaf: "tree-map-html__node--leaf",
    nodeSurface: "tree-map-html__node-surface",
    previousGroup: "tree-map-html__previous-group",
    previewControl: "tree-map-html__preview-control",
    previewInput: "tree-map-html__preview-input",
    previewSlider: "tree-map-html__preview-slider",
    section: "tree-map-html__section",
    title: "tree-map-html__title",
    toolbar: "tree-map-html__toolbar",
  });
  const DOM_IDS = Object.freeze({
    backIconTemplate: "tree-map-html-back-icon",
    data: "tree-map-html-data",
    modal: "modal",
    root: "tree-map-html-root",
    tipsButton: "tree-map-html-tips-button",
    tipsModalTemplate: "tree-map-html-tips-modal-template",
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

  function createLabel(text, modifierClass) {
    // Labels in nodes and ancestor navigation share their markup. A semantic
    // modifier lets CSS add the right icon without depending on DOM depth.
    const labelElement = document.createElement("span");
    labelElement.classList.add(CSS_CLASSES.label, modifierClass);
    labelElement.textContent = text;
    return labelElement;
  }

  function createTemplateIcon(templateId) {
    const templateElement = document.getElementById(templateId);
    if (!(templateElement instanceof HTMLTemplateElement)) {
      throw new Error(`Missing icon template: ${templateId}`);
    }
    const iconElement = templateElement.content.querySelector("svg");
    if (iconElement === null) {
      throw new Error(`Icon template has no SVG: ${templateId}`);
    }
    return iconElement.cloneNode(true);
  }

  function applyNodeColor(element, node) {
    // A missing color keeps the page-level CSS default. A data-defined color
    // follows the node into every representation, including ancestor buttons.
    if (typeof node.color === "string") {
      element.style.backgroundColor = node.color;
    }
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

  function getAspectRatioPenalty(width, height, targetAspectRatio) {
    const aspectRatio = width / height;
    return Math.max(
      aspectRatio / targetAspectRatio,
      targetAspectRatio / aspectRatio,
    );
  }

  function usesVerticalStrip(rectangle, targetAspectRatio) {
    // A target above 1 delays column-oriented strips until the remaining
    // rectangle is clearly wide, favoring rows suitable for text labels.
    return rectangle.width >= rectangle.height * targetAspectRatio;
  }

  function getWorstAspectRatio(row, rectangle, targetAspectRatio) {
    // Squarify adds an item only while it improves the worst-shaped tile in
    // the current row. The preferred tile is wider than a square because node
    // labels are horizontal text.
    if (row.length === 0) {
      return Number.POSITIVE_INFINITY;
    }

    const rowArea = row.reduce((total, item) => total + item.area, 0);
    if (usesVerticalStrip(rectangle, targetAspectRatio)) {
      const rowWidth = rowArea / rectangle.height;
      return Math.max(
        ...row.map((item) =>
          getAspectRatioPenalty(
            rowWidth,
            item.area / rowWidth,
            targetAspectRatio,
          ),
        ),
      );
    }
    const rowHeight = rowArea / rectangle.width;
    return Math.max(
      ...row.map((item) =>
        getAspectRatioPenalty(
          item.area / rowHeight,
          rowHeight,
          targetAspectRatio,
        ),
      ),
    );
  }

  function positionRow(
    row,
    rectangle,
    positionedItems,
    targetAspectRatio,
  ) {
    // Consume a strip in the orientation selected for text-shaped tiles. Each
    // item keeps its exact proportional area inside that strip.
    const rowArea = row.reduce((total, item) => total + item.area, 0);

    if (usesVerticalStrip(rectangle, targetAspectRatio)) {
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
    targetAspectRatio,
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
            const aspectRatio = getAspectRatioPenalty(
              nodeWidth,
              rowHeight,
              targetAspectRatio,
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
    targetAspectRatio,
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
      const candidateRow = [...row, nextItem];
      if (
        row.length === 0 ||
        getWorstAspectRatio(candidateRow, rectangle, targetAspectRatio) <=
          getWorstAspectRatio(row, rectangle, targetAspectRatio)
      ) {
        row = candidateRow;
        remainingItems.shift();
      } else {
        positionRow(row, rectangle, positionedItems, targetAspectRatio);
        row = [];
      }
    }
    if (row.length > 0) {
      positionRow(row, rectangle, positionedItems, targetAspectRatio);
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
          targetAspectRatio,
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
      const group = {
        weight: 0,
        color: node.color,
        children,
        isSyntheticGroup: true,
        firstItem: firstChildNumber,
        lastItem: lastChildNumber,
        totalItems: node.children.length,
      };
      group.label = `Items ${group.firstItem}-${group.lastItem}`;
      groups.push(group);
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
    nodeElement.className = CSS_CLASSES.node;
    nodeElement.dataset.depth = depth;
    if (depth === 0) {
      // The focused node remains the visible geometry and header around its
      // children, but it is already open and therefore is not interactive.
      nodeElement.classList.add(CSS_CLASSES.nodeFocusedRoot);
    }
    // The immediate children of the focused root are the current level. Deeper
    // nodes provide context and use a quieter visual treatment.
    if (depth === 1) {
      nodeElement.classList.add(CSS_CLASSES.nodeCurrentLevel);
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
    surfaceElement.className = CSS_CLASSES.nodeSurface;
    applyNodeColor(surfaceElement, node);
    nodeElement.append(surfaceElement);

    const headerElement = document.createElement("div");
    headerElement.className = CSS_CLASSES.nodeHeader;
    surfaceElement.append(headerElement);
    if (
      pixelRectangle.width >= options.minLabelWidth &&
      pixelRectangle.height >= options.nodeHeaderHeight
    ) {
      const labelModifier =
        depth === 0
          ? CSS_CLASSES.labelRoot
          : node.children.length === 0
            ? CSS_CLASSES.labelLeaf
            : CSS_CLASSES.labelBranch;
      headerElement.append(createLabel(node.label, labelModifier));
    }

    if (node.children.length === 0) {
      nodeElement.classList.add(CSS_CLASSES.nodeLeaf);
      return {
        node,
        nodeElement,
        headerElement,
        depth,
        pixelRectangle,
        renderableChildren,
      };
    }

    if (depth === 0) {
      return {
        node,
        nodeElement,
        headerElement,
        depth,
        pixelRectangle,
        renderableChildren,
      };
    }

    nodeElement.classList.add(CSS_CLASSES.nodeBranch);
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
      headerElement,
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
        // Depth zero is the open folder represented by the canvas. Every
        // deeper branch is a closed folder until the user navigates into it.
        if (!options.showCollapsedFolderContent && depth > 0) {
          nodeElement.dataset.collapsed = "true";
          continue;
        }
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
          options.targetNodeAspectRatio,
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
        childrenElement.className = CSS_CLASSES.children;
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

    return rootRecord;
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
    // Every canvas owns its display options. Changing one map must not change
    // sibling maps created from the shared renderer defaults.
    const mapOptions = { ...options };
    const sectionElement = document.createElement("section");
    sectionElement.className = CSS_CLASSES.section;

    const titleElement = document.createElement("h2");
    titleElement.className = CSS_CLASSES.title;
    titleElement.textContent = treeMap.title;
    sectionElement.append(titleElement);

    const toolbarElement = document.createElement("div");
    toolbarElement.className = CSS_CLASSES.toolbar;

    const previewControlElement = document.createElement("label");
    previewControlElement.className = CSS_CLASSES.previewControl;
    const previewInputElement = document.createElement("input");
    previewInputElement.className = CSS_CLASSES.previewInput;
    previewInputElement.type = "checkbox";
    previewInputElement.checked = mapOptions.showCollapsedFolderContent;
    previewInputElement.dataset.testid =
      "tree-map-html-preview-folder-contents";
    const previewSliderElement = document.createElement("span");
    previewSliderElement.className = CSS_CLASSES.previewSlider;
    previewControlElement.append(
      previewInputElement,
      previewSliderElement,
      "Preview folder contents",
    );
    toolbarElement.append(previewControlElement);

    const historyBreadcrumbElement = document.createElement("span");
    historyBreadcrumbElement.className = CSS_CLASSES.historyBreadcrumb;
    historyBreadcrumbElement.dataset.testid =
      "tree-map-html-history-breadcrumb";
    toolbarElement.append(historyBreadcrumbElement);

    const backIconElement = createTemplateIcon(DOM_IDS.backIconTemplate);
    backIconElement.classList.add(CSS_CLASSES.back);
    backIconElement.setAttribute("role", "button");
    backIconElement.setAttribute("aria-label", "Back");
    backIconElement.tabIndex = 0;
    toolbarElement.append(backIconElement);

    const groupNavigationElement = document.createElement("div");
    groupNavigationElement.className = CSS_CLASSES.groupNavigation;

    const previousGroupButton = document.createElement("button");
    previousGroupButton.className = CSS_CLASSES.previousGroup;
    previousGroupButton.type = "button";
    previousGroupButton.setAttribute("aria-label", "Previous items");
    previousGroupButton.textContent = "◂";

    const nextGroupButton = document.createElement("button");
    nextGroupButton.className = CSS_CLASSES.nextGroup;
    nextGroupButton.type = "button";
    nextGroupButton.setAttribute("aria-label", "Next items");
    nextGroupButton.textContent = "▸";

    const groupPositionElement = document.createElement("span");
    groupPositionElement.className = CSS_CLASSES.groupPosition;
    groupNavigationElement.append(
      groupPositionElement,
      previousGroupButton,
      nextGroupButton,
    );
    sectionElement.append(toolbarElement);

    const ancestorsElement = document.createElement("nav");
    ancestorsElement.className = CSS_CLASSES.ancestors;
    ancestorsElement.setAttribute("aria-label", "Tree map ancestors");
    sectionElement.append(ancestorsElement);

    const canvasElement = document.createElement("div");
    canvasElement.className = CSS_CLASSES.canvas;
    sectionElement.append(canvasElement);
    rootElement.append(sectionElement);

    indexNodeParents(treeMap.root);
    const visitHistory = [treeMap.root];

    function getFocusedNode() {
      return visitHistory[visitHistory.length - 1];
    }

    function navigateTo(node) {
      const focusedNode = getFocusedNode();
      if (node !== focusedNode) {
        visitHistory.push(node);
        renderFocusedNode();
      }
    }

    function navigateToSyntheticSibling(offset) {
      const navigation = syntheticGroupNavigation.get(getFocusedNode());
      if (navigation === undefined) {
        return false;
      }
      const sibling = navigation.groups[navigation.index + offset];
      if (sibling === undefined) {
        return false;
      }
      navigateTo(sibling);
      return true;
    }

    function navigateToParent() {
      const parent = nodeParents.get(getFocusedNode());
      if (parent === undefined) {
        return false;
      }
      navigateTo(parent);
      return true;
    }

    function navigateBack() {
      if (visitHistory.length === 1) {
        return false;
      }
      visitHistory.pop();
      renderFocusedNode();
      return true;
    }

    function isTextEditingTarget(target) {
      return (
        target instanceof HTMLElement &&
        (target.matches("input, textarea") || target.isContentEditable)
      );
    }

    function renderAncestors(focusedNode) {
      ancestorsElement.replaceChildren();
      for (const ancestor of getNodeAncestors(focusedNode)) {
        // create button
        const ancestorButton = document.createElement("button");
        ancestorButton.className = CSS_CLASSES.ancestor;
        ancestorButton.type = "button";
        applyNodeColor(ancestorButton, ancestor);
        ancestorButton.append(
          createLabel(ancestor.label, CSS_CLASSES.labelAncestor),
        );
        // place button
        ancestorButton.addEventListener("click", () => navigateTo(ancestor));
        ancestorsElement.append(ancestorButton);
      }
    }

    function renderGroupNavigation(focusedNode, focusedHeaderElement) {
      groupNavigationElement.remove();
      const navigation = syntheticGroupNavigation.get(focusedNode);
      if (navigation === undefined) {
        return;
      }
      groupPositionElement.textContent =
        `${focusedNode.firstItem}–${focusedNode.lastItem} ` +
        `of ${focusedNode.totalItems}`;
      previousGroupButton.disabled = navigation.index === 0;
      nextGroupButton.disabled = navigation.index === navigation.groups.length - 1;
      previousGroupButton.onclick = () => navigateToSyntheticSibling(-1);
      nextGroupButton.onclick = () => navigateToSyntheticSibling(1);
      focusedHeaderElement.append(groupNavigationElement);
    }

    function renderFocusedNode() {
      const focusedNode = getFocusedNode();
      const canvasRectangle = canvasElement.getBoundingClientRect();
      canvasElement.replaceChildren();
      historyBreadcrumbElement.textContent = visitHistory
        .slice(0, -1)
        .map((node) => node.label)
        .join(" • ");
      backIconElement.toggleAttribute(
        "hidden",
        historyBreadcrumbElement.textContent.length === 0,
      );
      renderAncestors(focusedNode);
      const rootRecord = renderNodeTree(
        focusedNode,
        canvasRectangle,
        navigateTo,
        mapOptions,
      );
      canvasElement.append(rootRecord.nodeElement);
      renderGroupNavigation(focusedNode, rootRecord.headerElement);
    }

    document.addEventListener("keydown", (event) => {
      // Keyboard navigation belongs to the complete map section under the
      // pointer, including its toolbar, ancestors, and canvas. Other maps and
      // the rest of the page keep native keys.
      if (!sectionElement.matches(":hover")) {
        return;
      }
      let didNavigate = false;
      if (event.key === "ArrowLeft") {
        didNavigate = navigateToSyntheticSibling(-1);
      } else if (event.key === "ArrowRight") {
        didNavigate = navigateToSyntheticSibling(1);
      } else if (event.key === "ArrowUp") {
        didNavigate = navigateToParent();
      } else if (
        event.key === "Backspace" &&
        !isTextEditingTarget(event.target)
      ) {
        didNavigate = navigateBack();
      }
      if (didNavigate) {
        event.preventDefault();
      }
    });

    backIconElement.addEventListener("click", navigateBack);
    backIconElement.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        navigateBack();
      }
    });

    previewInputElement.addEventListener("change", () => {
      mapOptions.showCollapsedFolderContent = previewInputElement.checked;
      renderFocusedNode();
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
    const rootElement = document.getElementById(DOM_IDS.root);
    const dataElement = document.getElementById(DOM_IDS.data);
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

  function initializeTipsModal() {
    // The page header owns one help button and one inert template. Copying the
    // template into StrictDoc's modal outlet follows the table-screen pattern.
    const buttonElement = document.getElementById(DOM_IDS.tipsButton);
    const modalElement = document.getElementById(DOM_IDS.modal);
    const templateElement = document.getElementById(DOM_IDS.tipsModalTemplate);
    if (
      buttonElement === null ||
      modalElement === null ||
      !(templateElement instanceof HTMLTemplateElement)
    ) {
      return;
    }
    buttonElement.addEventListener("click", () => {
      modalElement.replaceChildren(templateElement.content.cloneNode(true));
    });
  }

  initializeTipsModal();
  renderTreeMaps();
})();
