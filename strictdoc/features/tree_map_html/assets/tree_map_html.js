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
    siblingCurrent: "tree-map-html__sibling-current",
    siblingLabel: "tree-map-html__sibling-label",
    siblingLabelNext: "tree-map-html__sibling-label--next",
    siblingLabelPrevious: "tree-map-html__sibling-label--previous",
    siblingNavigation: "tree-map-html__sibling-navigation",
    siblingNavigationProjectRoot:
      "tree-map-html__sibling-navigation--project-root",
    siblingSymbol: "tree-map-html__sibling-symbol",
    infoPanel: "tree-map-html__info-panel",
    infoTable: "tree-map-html__info-table",
    label: "tree-map-html__label",
    labelAncestor: "tree-map-html__label--ancestor",
    labelBranch: "tree-map-html__label--branch",
    labelLeaf: "tree-map-html__label--leaf",
    labelRoot: "tree-map-html__label--root",
    historyBreadcrumb: "tree-map-html__history-breadcrumb",
    historyBreadcrumbEllipsis:
      "tree-map-html__history-breadcrumb-ellipsis",
    historyBreadcrumbItem: "tree-map-html__history-breadcrumb-item",
    historyBreadcrumbLatest:
      "tree-map-html__history-breadcrumb-item--latest",
    historyBreadcrumbSeparator:
      "tree-map-html__history-breadcrumb-separator",
    nextSibling: "tree-map-html__next-sibling",
    node: "tree-map-html__node",
    nodeBranch: "tree-map-html__node--branch",
    nodeCurrentLevel: "tree-map-html__node--current-level",
    nodeFocusedRoot: "tree-map-html__node--focused-root",
    nodeHeader: "tree-map-html__node-header",
    nodeLeaf: "tree-map-html__node--leaf",
    nodeSurface: "tree-map-html__node-surface",
    nodeAction: "tree-map-html__node-action",
    nodeActions: "tree-map-html__node-actions",
    nodeGoToDocument: "tree-map-html__node-action--go-to-document",
    nodePreview: "tree-map-html__node-action--preview",
    previousSibling: "tree-map-html__previous-sibling",
    previewControl: "tree-map-html__preview-control",
    previewInput: "tree-map-html__preview-input",
    previewSlider: "tree-map-html__preview-slider",
    section: "tree-map-html__section",
    title: "tree-map-html__title",
    toolbar: "tree-map-html__toolbar",
    footer: "tree-map-html__footer",
  });
  const DOM_IDS = Object.freeze({
    backIconTemplate: "tree-map-html-back-icon",
    data: "tree-map-html-data",
    modal: "modal",
    root: "tree-map-html-root",
    goToDocumentIconTemplate: "tree-map-html-go-to-document-icon",
    previewIconTemplate: "tree-map-html-preview-icon",
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

  function createNodeAction(node, kind) {
    const isDocumentAction = kind === "document";
    const url = isDocumentAction ? node.document_url : node.preview_url;
    if (typeof url !== "string") {
      return null;
    }
    const actionElement = document.createElement("a");
    actionElement.classList.add(
      CSS_CLASSES.nodeAction,
      isDocumentAction
        ? CSS_CLASSES.nodeGoToDocument
        : CSS_CLASSES.nodePreview,
    );
    actionElement.href = url;
    actionElement.title = isDocumentAction
      ? "Find it in the document view"
      : "Show in full in modal";
    actionElement.setAttribute("aria-label", actionElement.title);
    if (!isDocumentAction) {
      actionElement.dataset.turbo = "true";
      actionElement.dataset.turboAction = "replace";
    }
    actionElement.append(
      createTemplateIcon(
        isDocumentAction
          ? DOM_IDS.goToDocumentIconTemplate
          : DOM_IDS.previewIconTemplate,
      ),
    );
    return actionElement;
  }

  function createNodeActions(node) {
    const actionsElement = document.createElement("span");
    actionsElement.className = CSS_CLASSES.nodeActions;
    for (const kind of ["document", "preview"]) {
      const actionElement = createNodeAction(node, kind);
      if (actionElement !== null) {
        if (kind === "preview") {
          // DEEP-TRACE scopes the full-node action through a Turbo frame. The
          // frame has no visual box but lets Turbo process the stream response.
          const turboFrameElement = document.createElement("turbo-frame");
          turboFrameElement.append(actionElement);
          actionsElement.append(turboFrameElement);
        } else {
          actionsElement.append(actionElement);
        }
      }
    }
    return actionsElement.childElementCount > 0 ? actionsElement : null;
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
    if (typeof node.mid === "string") {
      nodeElement.dataset.nodeMid = node.mid;
    }
    if (typeof node.title === "string") {
      nodeElement.dataset.nodeTitle = node.title;
    }
    if (typeof node.uid === "string") {
      nodeElement.dataset.nodeUid = node.uid;
    }
    if (node.isSyntheticGroup === true) {
      nodeElement.dataset.syntheticGroup = "true";
    }
    const nodeWeight = getNodeWeight(node);
    nodeElement.dataset.weight = nodeWeight;
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
      depth !== 0 &&
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

    const actionsElement = createNodeActions(node);
    if (actionsElement !== null && depth !== 0) {
      if (node.children.length === 0) {
        surfaceElement.append(actionsElement);
      } else {
        headerElement.append(actionsElement);
      }
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
        actionsElement,
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
        actionsElement,
      };
    }

    nodeElement.classList.add(CSS_CLASSES.nodeBranch);
    nodeElement.setAttribute("role", "button");
    nodeElement.tabIndex = 0;
    nodeElement.addEventListener("click", (event) => {
      // Action links must keep bubbling to Turbo and the browser. Exclude them
      // here instead of stopping their event at the link.
      if (
        event.target instanceof Element &&
        event.target.closest(`.${CSS_CLASSES.nodeAction}`) !== null
      ) {
        return;
      }
      event.stopPropagation();
      zoomIntoNode(node);
    });
    nodeElement.addEventListener("keydown", (event) => {
      if (
        event.target instanceof Element &&
        event.target.closest(`.${CSS_CLASSES.nodeAction}`) !== null
      ) {
        return;
      }
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
      actionsElement,
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

    // ** sibling Navigation **

    const siblingNavigationElement = document.createElement("div");
    siblingNavigationElement.className = CSS_CLASSES.siblingNavigation;

    // sibling Navigation: current Label
    const currentSiblingElement = document.createElement("div");
    currentSiblingElement.className = CSS_CLASSES.siblingCurrent;
    const currentSiblingLabel = createLabel("", CSS_CLASSES.labelRoot);
    currentSiblingElement.append(currentSiblingLabel);

    // sibling Navigation: previous Button
    const previousSiblingLabel = document.createElement("span");
    previousSiblingLabel.classList.add(
      CSS_CLASSES.siblingLabel,
      CSS_CLASSES.siblingLabelPrevious,
    );
    const previousSiblingButton = document.createElement("button");
    previousSiblingButton.className = CSS_CLASSES.previousSibling;
    previousSiblingButton.type = "button";
    const previousSiblingSymbol = document.createElement("span");
    previousSiblingSymbol.className = CSS_CLASSES.siblingSymbol;
    previousSiblingSymbol.textContent = "❮";
    previousSiblingButton.append(
      previousSiblingSymbol,
      previousSiblingLabel,
    );

  // sibling Navigation: next Button
    const nextSiblingLabel = document.createElement("span");
    nextSiblingLabel.classList.add(
      CSS_CLASSES.siblingLabel,
      CSS_CLASSES.siblingLabelNext,
    );
    const nextSiblingButton = document.createElement("button");
    nextSiblingButton.className = CSS_CLASSES.nextSibling;
    nextSiblingButton.type = "button";
    const nextSiblingSymbol = document.createElement("span");
    nextSiblingSymbol.className = CSS_CLASSES.siblingSymbol;
    nextSiblingSymbol.textContent = "❯";
    nextSiblingButton.append(
      nextSiblingLabel,
      nextSiblingSymbol,
    );

    siblingNavigationElement.append(
      previousSiblingButton,
      currentSiblingElement,
      nextSiblingButton,
    );
    sectionElement.append(toolbarElement);

    // ***

    const ancestorsElement = document.createElement("nav");
    ancestorsElement.className = CSS_CLASSES.ancestors;
    ancestorsElement.setAttribute("aria-label", "Tree map ancestors");
    sectionElement.append(ancestorsElement);

    const canvasElement = document.createElement("div");
    canvasElement.className = CSS_CLASSES.canvas;
    sectionElement.append(canvasElement);

    const infoPanelElement = document.createElement("div");
    infoPanelElement.className = CSS_CLASSES.infoPanel;
    infoPanelElement.hidden = true;
    const infoTableElement = document.createElement("dl");
    infoTableElement.className = CSS_CLASSES.infoTable;
    infoPanelElement.append(infoTableElement);
    sectionElement.append(infoPanelElement);

    const footerElement = document.createElement("footer");
    footerElement.className = CSS_CLASSES.footer;
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
      "Preview folder contents",
      previewInputElement,
      previewSliderElement,
    );
    footerElement.append(previewControlElement);
    sectionElement.append(footerElement);

    let pointedNodeElement = null;
    let lastPointerEvent = null;
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

    function getSiblingNavigation(node) {
      const syntheticNavigation = syntheticGroupNavigation.get(node);
      if (syntheticNavigation !== undefined) {
        return {
          siblings: syntheticNavigation.groups,
          index: syntheticNavigation.index,
        };
      }
      const parent = nodeParents.get(node);
      if (parent === undefined) {
        return { siblings: [node], index: 0 };
      }
      return {
        siblings: parent.children,
        index: parent.children.indexOf(node),
      };
    }

    function navigateToSibling(offset) {
      const navigation = getSiblingNavigation(getFocusedNode());
      const sibling = navigation.siblings[navigation.index + offset];
      if (sibling === undefined) {
        return false;
      }
      // Sibling browsing stays within one history step. Back returns to the
      // node from which the user entered this level, not every sibling seen.
      visitHistory[visitHistory.length - 1] = sibling;
      renderFocusedNode();
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

    function renderInfoPanel(nodeElement, pointerEvent) {
      const rows = [
        ["Title", nodeElement.dataset.nodeTitle],
        ["MID", nodeElement.dataset.nodeMid],
        ["UID", nodeElement.dataset.nodeUid],
      ];
      infoTableElement.replaceChildren();
      for (const [name, value] of rows) {
        if (value === undefined) {
          continue;
        }
        const termElement = document.createElement("dt");
        termElement.textContent = name;
        const valueElement = document.createElement("dd");
        valueElement.textContent = value;
        infoTableElement.append(termElement, valueElement);
      }
      infoPanelElement.style.left =
        `${Math.min(pointerEvent.clientX + 12, window.innerWidth - 272)}px`;
      infoPanelElement.style.top =
        `${Math.min(pointerEvent.clientY + 12, window.innerHeight - 120)}px`;
    }

    function renderAncestors(focusedNode) {
      ancestorsElement.replaceChildren();
      for (const ancestor of getNodeAncestors(focusedNode)) {
        const ancestorButton = createAncestorButton(ancestor);
        ancestorsElement.append(ancestorButton);
      }
    }

    function createAncestorButton(ancestor) {
      const ancestorButton = document.createElement("button");
      ancestorButton.className = CSS_CLASSES.ancestor;
      ancestorButton.type = "button";
      ancestorButton.append(
        createLabel(ancestor.label, CSS_CLASSES.labelAncestor),
      );
      applyNodeColor(ancestorButton, ancestor);
      ancestorButton.addEventListener("click", () => navigateTo(ancestor));
      return ancestorButton;
    }

    function getNavigationLabel(node, isCurrent) {
      if (node.isSyntheticGroup === true && isCurrent) {
        return `${node.firstItem}–${node.lastItem} of ${node.totalItems}`;
      }
      return node.label;
    }

    function setSiblingLabel(labelElement, node, isCurrent = false) {
      if (node === undefined) {
        labelElement.textContent = "";
        labelElement.removeAttribute("title");
        return;
      }
      const label = getNavigationLabel(node, isCurrent);
      labelElement.textContent = label;
      labelElement.title = label;
    }

    function renderSiblingNavigation(
      focusedNode,
      focusedHeaderElement,
      focusedActionsElement,
    ) {
      siblingNavigationElement.remove();
      const navigation = getSiblingNavigation(focusedNode);
      siblingNavigationElement.classList.toggle(
        CSS_CLASSES.siblingNavigationProjectRoot,
        focusedNode === treeMap.root,
      );
      const previousSibling = navigation.siblings[navigation.index - 1];
      const nextSibling = navigation.siblings[navigation.index + 1];

      setSiblingLabel(previousSiblingLabel, previousSibling);
      setSiblingLabel(currentSiblingLabel, focusedNode, true);
      setSiblingLabel(nextSiblingLabel, nextSibling);
      currentSiblingElement.replaceChildren(currentSiblingLabel);
      if (focusedActionsElement !== null) {
        currentSiblingElement.append(focusedActionsElement);
      }

      previousSiblingButton.disabled = previousSibling === undefined;
      previousSiblingButton.setAttribute(
        "aria-label",
        previousSibling === undefined
          ? "No previous item"
          : `Previous: ${getNavigationLabel(previousSibling, false)}`,
      );
      nextSiblingButton.disabled = nextSibling === undefined;
      nextSiblingButton.setAttribute(
        "aria-label",
        nextSibling === undefined
          ? "No next item"
          : `Next: ${getNavigationLabel(nextSibling, false)}`,
      );
      previousSiblingButton.onclick = () => navigateToSibling(-1);
      nextSiblingButton.onclick = () => navigateToSibling(1);
      focusedHeaderElement.prepend(siblingNavigationElement);
    }

    function renderHistoryBreadcrumb() {
      const historyLabels = visitHistory
        .slice(0, -1)
        .map((node) => node.label);
      backIconElement.toggleAttribute("hidden", historyLabels.length === 0);

      function renderVisibleItems(firstVisibleIndex) {
        historyBreadcrumbElement.replaceChildren();
        if (firstVisibleIndex > 0) {
          const ellipsisElement = document.createElement("span");
          ellipsisElement.className = CSS_CLASSES.historyBreadcrumbEllipsis;
          ellipsisElement.textContent = "…";
          historyBreadcrumbElement.append(ellipsisElement);
        }
        for (
          let index = firstVisibleIndex;
          index < historyLabels.length;
          index += 1
        ) {
          if (index > firstVisibleIndex || firstVisibleIndex > 0) {
            const separatorElement = document.createElement("span");
            separatorElement.className =
              CSS_CLASSES.historyBreadcrumbSeparator;
            separatorElement.textContent = "•";
            historyBreadcrumbElement.append(separatorElement);
          }
          const itemElement = document.createElement("span");
          itemElement.className = CSS_CLASSES.historyBreadcrumbItem;
          itemElement.textContent = historyLabels[index];
          historyBreadcrumbElement.append(itemElement);
        }
      }

      // Start with the complete history, then remove the oldest entries until
      // the remaining tail fits. The latest entry stays visible and may use a
      // conventional right-side ellipsis when its own label is too long.
      let firstVisibleIndex = 0;
      renderVisibleItems(firstVisibleIndex);
      while (
        historyBreadcrumbElement.scrollWidth >
          historyBreadcrumbElement.clientWidth &&
        firstVisibleIndex < historyLabels.length - 1
      ) {
        firstVisibleIndex += 1;
        renderVisibleItems(firstVisibleIndex);
      }
      historyBreadcrumbElement.lastElementChild?.classList.add(
        CSS_CLASSES.historyBreadcrumbLatest,
      );
    }

    function renderFocusedNode() {
      const focusedNode = getFocusedNode();
      const canvasRectangle = canvasElement.getBoundingClientRect();
      canvasElement.replaceChildren();
      renderHistoryBreadcrumb();
      renderAncestors(focusedNode);
      const rootRecord = renderNodeTree(
        focusedNode,
        canvasRectangle,
        navigateTo,
        mapOptions,
      );
      canvasElement.append(rootRecord.nodeElement);
      renderSiblingNavigation(
        focusedNode,
        rootRecord.headerElement,
        rootRecord.actionsElement,
      );
    }

    document.addEventListener("keydown", (event) => {
      // Keyboard navigation belongs to the complete map section under the
      // pointer, including its toolbar, ancestors, and canvas. Other maps and
      // the rest of the page keep native keys.
      if (!sectionElement.matches(":hover")) {
        return;
      }
      if (event.key === "Shift") {
        if (pointedNodeElement !== null && lastPointerEvent !== null) {
          renderInfoPanel(pointedNodeElement, lastPointerEvent);
          infoPanelElement.hidden = false;
        }
        return;
      }
      let didNavigate = false;
      if (event.key === "ArrowLeft") {
        didNavigate = navigateToSibling(-1);
      } else if (event.key === "ArrowRight") {
        didNavigate = navigateToSibling(1);
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

    sectionElement.addEventListener("pointermove", (event) => {
      lastPointerEvent = event;
      pointedNodeElement =
        event.target instanceof Element
          ? event.target.closest(`.${CSS_CLASSES.node}`)
          : null;
      if (
        pointedNodeElement === null ||
        pointedNodeElement.dataset.nodeMid === undefined
      ) {
        infoPanelElement.hidden = true;
        return;
      }
      renderInfoPanel(pointedNodeElement, event);
      infoPanelElement.hidden = !event.shiftKey;
    });
    sectionElement.addEventListener("pointerleave", () => {
      pointedNodeElement = null;
      lastPointerEvent = null;
      infoPanelElement.hidden = true;
    });
    document.addEventListener("keyup", (event) => {
      if (event.key === "Shift") {
        infoPanelElement.hidden = true;
      }
    });
    window.addEventListener("blur", () => {
      infoPanelElement.hidden = true;
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
