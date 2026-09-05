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
    minNodeHeight: 32,
    minNodeWidth: 24,
    minLabelWidth: 56,
    labelLineHeight: 12,
    currentLevelLabelLineHeight: 16,
    labelVerticalPadding: 4,
    targetNodeArea: 1200,
    // 1 restores classic square-oriented squarify behavior. Values above 1
    // prefer wider rectangles for text without forcing a fixed orientation.
    targetNodeAspectRatio: 1.6,
  });
  const INFO_PANEL_POINTER_OFFSET = 12;
  const INFO_PANEL_VIEWPORT_PADDING = 8;
  const URL_PARAMETERS = Object.freeze({
    map: "map",
    node: "node",
    preview: "preview",
  });
  const CSS_CLASSES = Object.freeze({
    ancestor: "tree-map__ancestor",
    ancestors: "tree-map__ancestors",
    back: "tree-map__back",
    canvas: "tree-map__canvas",
    children: "tree-map__children",
    description: "tree-map__description",
    descriptionText: "tree-map__description-text",
    siblingCurrent: "tree-map__sibling-current",
    siblingLabel: "tree-map__sibling-label",
    siblingLabelNext: "tree-map__sibling-label--next",
    siblingLabelPrevious: "tree-map__sibling-label--previous",
    siblingNavigation: "tree-map__sibling-navigation",
    siblingNavigationProjectRoot:
      "tree-map__sibling-navigation--project-root",
    labelSymbol: "tree-map__label-symbol",
    infoPanel: "tree-map__info-panel",
    infoTable: "tree-map__info-table",
    infoPanelTip: "tree-map__info-panel-tip",
    label: "tree-map__label",
    labelAncestor: "tree-map__label--ancestor",
    labelBranch: "tree-map__label--branch",
    labelLeaf: "tree-map__label--leaf",
    labelMultiline: "tree-map__label--multiline",
    labelRoot: "tree-map__label--root",
    labelText: "tree-map__label-text",
    labelCurrentLevel: "tree-map__label--current-level",
    legend: "tree-map__legend",
    legendItem: "tree-map__legend-item",
    legendSwatch: "tree-map__legend-swatch",
    historyBreadcrumb: "tree-map__history-breadcrumb",
    historyBreadcrumbEllipsis:
      "tree-map__history-breadcrumb-ellipsis",
    historyBreadcrumbItem: "tree-map__history-breadcrumb-item",
    historyBreadcrumbLatest:
      "tree-map__history-breadcrumb-item--latest",
    historyBreadcrumbSeparator:
      "tree-map__history-breadcrumb-separator",
    nextSibling: "tree-map__next-sibling",
    node: "tree-map__node",
    nodeBranch: "tree-map__node--branch",
    nodeCurrentLevel: "tree-map__node--current-level",
    nodeFocusedRoot: "tree-map__node--focused-root",
    nodeHeader: "tree-map__node-header",
    nodeHeaderFixed: "tree-map__node-header--fixed",
    nodeLeaf: "tree-map__node--leaf",
    nodeSurface: "tree-map__node-surface",
    nodeAction: "tree-map__node-action",
    nodeActions: "tree-map__node-actions",
    nodeGoToDocument: "tree-map__node-action--go-to-document",
    nodePreview: "tree-map__node-action--preview",
    previousSibling: "tree-map__previous-sibling",
    previewControl: "tree-map__preview-control",
    previewInput: "tree-map__preview-input",
    previewSlider: "tree-map__preview-slider",
    section: "tree-map__section",
    sectionShiftActive: "tree-map__section--shift-active",
    toolbar: "tree-map__toolbar",
    footer: "tree-map__footer",
    footerTip: "tree-map__footer-tip",
  });
  const DOM_IDS = Object.freeze({
    backIconTemplate: "tree-map-back-icon",
    data: "tree-map-data",
    modal: "modal",
    root: "tree-map-root",
    goToDocumentIconTemplate: "tree-map-go-to-document-icon",
    previewIconTemplate: "tree-map-preview-icon",
    selectorLabel: "tree-map-selector-label",
    selectorMenu: "tree-map-selector-menu",
    tipsButton: "tree-map-tips-button",
    tipsModalTemplate: "tree-map-tips-modal-template",
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

  function indexNodesByIdentifier(node, options, nodesByIdentifier) {
    if (nodesByIdentifier.has(node.identifier)) {
      throw new Error(`Duplicate tree map node identifier: ${node.identifier}`);
    }
    nodesByIdentifier.set(node.identifier, node);
    for (const child of node.children) {
      indexNodesByIdentifier(child, options, nodesByIdentifier);
    }
    for (const child of getRenderableChildren(node, options)) {
      if (child.isSyntheticGroup === true) {
        nodesByIdentifier.set(child.identifier, child);
      }
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

  function createLabel(text, modifierClass, count = null) {
    // Labels in nodes and ancestor navigation share their markup. A semantic
    // modifier lets CSS add the right icon without depending on DOM depth.
    const labelElement = document.createElement("span");
    labelElement.classList.add(CSS_CLASSES.label, modifierClass);
    const textElement = document.createElement("span");
    textElement.className = CSS_CLASSES.labelText;
    labelElement.append(textElement);
    updateLabel(labelElement, text, count);
    return labelElement;
  }

  function updateLabel(labelElement, text, count = null) {
    const textElement = labelElement.querySelector(
      `:scope > .${CSS_CLASSES.labelText}`,
    );
    if (textElement === null) {
      throw new Error("Tree map label has no text element.");
    }
    textElement.textContent = text;
    labelElement.title = text;
    if (Number.isInteger(count)) {
      labelElement.dataset.count = count;
    } else {
      delete labelElement.dataset.count;
    }
  }

  function createMapDescription(treeMap) {
    const descriptionElement = document.createElement("div");
    descriptionElement.className = CSS_CLASSES.description;
    descriptionElement.dataset.testid =
      `tree-map-description-${treeMap.identifier}`;

    const descriptionTextElement = document.createElement("p");
    descriptionTextElement.className = CSS_CLASSES.descriptionText;
    descriptionTextElement.textContent = treeMap.description;
    descriptionElement.append(descriptionTextElement);

    if (treeMap.legend.length > 0) {
      const legendElement = document.createElement("ul");
      legendElement.className = CSS_CLASSES.legend;
      for (const legendItem of treeMap.legend) {
        const itemElement = document.createElement("li");
        itemElement.className = CSS_CLASSES.legendItem;
        const swatchElement = document.createElement("span");
        swatchElement.className = CSS_CLASSES.legendSwatch;
        swatchElement.style.backgroundColor = legendItem.color;
        itemElement.append(swatchElement, legendItem.text);
        legendElement.append(itemElement);
      }
      descriptionElement.append(legendElement);
    }
    return descriptionElement;
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

  function calculateLabelLineClamp(
    surfaceHeight,
    labelModifier,
    options,
  ) {
    // Current-level labels use a 16px line; compact branch and leaf labels use
    // 12px. Subtract the shared 4px vertical padding once, then count how many
    // complete lines fit in the remaining surface height.
    const lineHeight =
      labelModifier === CSS_CLASSES.labelCurrentLevel
        ? options.currentLevelLabelLineHeight
        : options.labelLineHeight;
    return Math.max(
      1,
      Math.floor(
        (surfaceHeight - options.labelVerticalPadding) /
          lineHeight,
      ),
    );
  }

  function openDocumentView(url) {
    const linkElement = document.createElement("a");
    linkElement.href = url;
    linkElement.target = "_blank";
    linkElement.rel = "noopener";
    linkElement.click();
  }

  function createNodeAction(node, kind) {
    const isDocumentAction = kind === "document";
    const url = isDocumentAction ? node.document_url : node.preview_url;
    if (typeof url !== "string") {
      return null;
    }
    const actionElement = document.createElement("a");
    actionElement.dataset.testid = "tree-map-node-action";
    actionElement.dataset.action = isDocumentAction
      ? "document"
      : "preview";
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
    } else {
      actionElement.target = "_blank";
      actionElement.rel = "noopener";
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
    // Prefer the server-only modal. Static output has no preview URL, so the
    // same node falls back to its Document view URL with the anchor intact.
    const primaryAction =
      typeof node.preview_url === "string" ? "preview" : "document";
    const actionElement = createNodeAction(node, primaryAction);
    if (actionElement === null) {
      return null;
    }
    if (primaryAction === "preview") {
      // DEEP-TRACE scopes the full-node action through a Turbo frame. The
      // frame has no visual box but lets Turbo process the stream response.
      const turboFrameElement = document.createElement("turbo-frame");
      turboFrameElement.append(actionElement);
      actionsElement.append(turboFrameElement);
    } else {
      actionsElement.append(actionElement);
    }
    return actionsElement;
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
    const heightAdjusted = enforceMinimumHeight(
      positionedItems,
      minimumHeight,
    );
    const squarifiedItemsFit =
      heightAdjusted &&
      positionedItems.every((item) => item.width >= minimumWidth);
    const constrainedItems = squarifiedItemsFit
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
        identifier:
          `${node.identifier}:items:${firstChildNumber}-${lastChildNumber}`,
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
    nodeElement.dataset.testid = "tree-map-node";
    nodeElement.dataset.nodeIdentifier = node.identifier;
    nodeElement.dataset.depth = depth;
    if (depth === 0) {
      // The focused node remains the visible geometry and header around its
      // children, but it is already open and therefore is not interactive.
      nodeElement.classList.add(CSS_CLASSES.nodeFocusedRoot);
      nodeElement.dataset.nodeKind = "focused-root";
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
    if (depth === 0) {
      headerElement.classList.add(CSS_CLASSES.nodeHeaderFixed);
    }
    surfaceElement.append(headerElement);
    let labelElement = null;
    if (depth !== 0) {
      const labelModifier =
        depth === 0
          ? CSS_CLASSES.labelRoot
          : depth === 1
            ? CSS_CLASSES.labelCurrentLevel
            : node.children.length === 0
              ? CSS_CLASSES.labelLeaf
              : CSS_CLASSES.labelBranch;
      labelElement = createLabel(node.label, labelModifier, node.count);
      // A label starts multiline because its node has no rendered children
      // yet. Expansion below removes this class when it adds the child layer.
      labelElement.classList.add(CSS_CLASSES.labelMultiline);
      const surfaceHeight = Math.max(
        0,
        pixelRectangle.height - options.nodeGap,
      );
      labelElement.style.setProperty(
        "--tree-map-label-lines",
        calculateLabelLineClamp(surfaceHeight, labelModifier, options),
      );
      labelElement.firstElementChild.hidden = !(
        pixelRectangle.width >= options.minLabelWidth &&
        pixelRectangle.height >= options.nodeHeaderHeight
      );
      headerElement.append(labelElement);
    }

    const actionsElement = createNodeActions(node);
    if (actionsElement !== null) {
      nodeElement.dataset.hasPrimaryAction = "true";
      nodeElement.dataset.primaryAction =
        typeof node.preview_url === "string" ? "preview" : "document";
    }
    if (actionsElement !== null && depth !== 0) {
      // FIXME
      // if (node.children.length === 0) {
      // // Leaf node:
      //   surfaceElement.append(actionsElement);
      // } else {
      // // Folder (section) node:
      //   headerElement.append(actionsElement);
      // }
      surfaceElement.append(actionsElement);
    }

    nodeElement.addEventListener("pointerdown", (event) => {
      if (event.shiftKey) {
        event.preventDefault();
      }
    });
    nodeElement.addEventListener("click", (event) => {
      if (!event.shiftKey) {
        return;
      }
      // Modifier-click belongs to the tile, including its visible action.
      // Always suppress the browser's modifier behavior, even when the
      // requested action is unavailable.
      event.preventDefault();
      event.stopImmediatePropagation();
      if (event.altKey) {
        if (typeof node.document_url === "string") {
          openDocumentView(node.document_url);
        }
        return;
      }
      if (
        nodeElement.dataset.primaryAction === "document" &&
        typeof node.document_url === "string"
      ) {
        openDocumentView(node.document_url);
        return;
      }
      const primaryActionElement = nodeElement.querySelector(
        `.${CSS_CLASSES.nodeAction}`,
      );
      if (primaryActionElement instanceof HTMLAnchorElement) {
        primaryActionElement.click();
      }
    });

    if (node.children.length === 0) {
      nodeElement.classList.add(CSS_CLASSES.nodeLeaf);
      nodeElement.dataset.nodeKind = "leaf";
      return {
        node,
        nodeElement,
        headerElement,
        depth,
        pixelRectangle,
        renderableChildren,
        actionsElement,
        labelElement,
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
        labelElement,
      };
    }

    nodeElement.classList.add(CSS_CLASSES.nodeBranch);
    nodeElement.dataset.nodeKind = "branch";
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
      labelElement,
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
          headerElement,
          labelElement,
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
          options.minNodeWidth,
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
            childPixelRectangle.width >= options.minNodeWidth &&
            childPixelRectangle.height >= options.minNodeHeight,
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
        headerElement.classList.add(CSS_CLASSES.nodeHeaderFixed);
        labelElement?.classList.remove(CSS_CLASSES.labelMultiline);
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
      "--tree-map-node-gap-half",
      `${options.nodeGap / 2}px`,
    );
    rootElement.style.setProperty(
      "--tree-map-node-header-height",
      `${options.nodeHeaderHeight}px`,
    );
    rootElement.style.setProperty(
      "--tree-map-node-padding",
      `${options.nodePadding}px`,
    );
    rootElement.style.setProperty(
      "--tree-map-label-line-height",
      `${options.labelLineHeight}px`,
    );
    rootElement.style.setProperty(
      "--tree-map-current-level-label-line-height",
      `${options.currentLevelLabelLineHeight}px`,
    );
    rootElement.style.setProperty(
      "--tree-map-label-vertical-padding",
      `${options.labelVerticalPadding}px`,
    );
  }

  function createTreeMap(treeMap, options, onStateChange) {
    // Every map owns its navigation and display state. Switching maps only
    // detaches its section, so returning to it restores the previous view.
    const mapOptions = { ...options };
    const sectionElement = document.createElement("section");
    sectionElement.className = CSS_CLASSES.section;
    sectionElement.dataset.testid = "tree-map-section";

    const toolbarElement = document.createElement("div");
    toolbarElement.className = CSS_CLASSES.toolbar;

    const historyBreadcrumbElement = document.createElement("span");
    historyBreadcrumbElement.className = CSS_CLASSES.historyBreadcrumb;
    historyBreadcrumbElement.dataset.testid =
      "tree-map-history-breadcrumb";
    toolbarElement.append(historyBreadcrumbElement);

    const backIconElement = createTemplateIcon(DOM_IDS.backIconTemplate);
    backIconElement.classList.add(CSS_CLASSES.back);
    backIconElement.dataset.testid = "tree-map-back";
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
    currentSiblingElement.dataset.testid = "tree-map-focused-node";
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
    previousSiblingButton.dataset.testid = "tree-map-previous-sibling";
    previousSiblingButton.type = "button";
    const previousSiblingSymbol = document.createElement("span");
    previousSiblingSymbol.className = CSS_CLASSES.labelSymbol;
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
    nextSiblingButton.dataset.testid = "tree-map-next-sibling";
    nextSiblingButton.type = "button";
    const nextSiblingSymbol = document.createElement("span");
    nextSiblingSymbol.className = CSS_CLASSES.labelSymbol;
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
    sectionElement.append(createMapDescription(treeMap));

    // ***

    const ancestorsElement = document.createElement("nav");
    ancestorsElement.className = CSS_CLASSES.ancestors;
    ancestorsElement.dataset.testid = "tree-map-ancestors";
    ancestorsElement.setAttribute("aria-label", "Tree map ancestors");
    sectionElement.append(ancestorsElement);

    const canvasElement = document.createElement("div");
    canvasElement.className = CSS_CLASSES.canvas;
    canvasElement.dataset.testid = "tree-map-canvas";
    sectionElement.append(canvasElement);

    const infoPanelElement = document.createElement("div");
    infoPanelElement.className = CSS_CLASSES.infoPanel;
    infoPanelElement.dataset.testid = "tree-map-info-panel";
    infoPanelElement.hidden = true;
    const infoEmptyElement = document.createElement("div");
    infoEmptyElement.textContent = "No data";
    infoEmptyElement.hidden = true;
    const infoTableElement = document.createElement("dl");
    infoTableElement.className = CSS_CLASSES.infoTable;
    infoPanelElement.append(infoEmptyElement, infoTableElement);
    sectionElement.append(infoPanelElement);

    const footerTip = document.createElement("span");
    footerTip.className = CSS_CLASSES.footerTip;
    footerTip.innerHTML = `<span> Use <kbd>SHIFT</kbd> to get more info.</span>`;

    const footerElement = document.createElement("footer");
    footerElement.className = CSS_CLASSES.footer;
    const previewControlElement = document.createElement("label");
    previewControlElement.className = CSS_CLASSES.previewControl;
    previewControlElement.dataset.testid =
      "tree-map-preview-folder-contents-control";
    const previewInputElement = document.createElement("input");
    previewInputElement.className = CSS_CLASSES.previewInput;
    previewInputElement.type = "checkbox";
    previewInputElement.checked = mapOptions.showCollapsedFolderContent;
    previewInputElement.dataset.testid =
      "tree-map-preview-folder-contents";
    const previewSliderElement = document.createElement("span");
    previewSliderElement.className = CSS_CLASSES.previewSlider;
    previewControlElement.append(
      "Preview folder contents",
      previewInputElement,
      previewSliderElement,
    );
    footerElement.append(footerTip, previewControlElement);
    sectionElement.append(footerElement);

    let pointedNodeElement = null;
    let lastPointerEvent = null;
    let infoPanelContentNodeElement = null;
    let infoPanelSize = null;
    const nodesByIdentifier = new Map();
    indexNodeParents(treeMap.root);
    indexNodesByIdentifier(treeMap.root, mapOptions, nodesByIdentifier);
    const visitHistory = [treeMap.root];

    function getFocusedNode() {
      return visitHistory[visitHistory.length - 1];
    }

    function notifyStateChange() {
      const focusedNode = getFocusedNode();
      onStateChange({
        nodeIdentifier:
          focusedNode === treeMap.root ? null : focusedNode.identifier,
        preview: mapOptions.showCollapsedFolderContent,
      });
    }

    function navigateTo(node) {
      const focusedNode = getFocusedNode();
      if (node !== focusedNode) {
        visitHistory.push(node);
        renderFocusedNode();
        notifyStateChange();
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
      notifyStateChange();
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
      notifyStateChange();
      return true;
    }

    function isTextEditingTarget(target) {
      return (
        target instanceof HTMLElement &&
        (target.matches("input, textarea") || target.isContentEditable)
      );
    }

    function renderInfoPanel(nodeElement, pointerEvent) {
      if (
        nodeElement !== infoPanelContentNodeElement ||
        infoPanelSize === null
      ) {
        const rows = [
          ["Title", nodeElement.dataset.nodeTitle],
          ["MID", nodeElement.dataset.nodeMid],
          ["UID", nodeElement.dataset.nodeUid],
        ].filter(([, value]) => value !== undefined);
        infoEmptyElement.hidden = rows.length !== 0;
        const tipLine = document.createElement("div");
        tipLine.className = CSS_CLASSES.infoPanelTip;
        tipLine.innerHTML =
          nodeElement.dataset.primaryAction === "preview"
            ? `<kbd>SHIFT</kbd>+<kbd>CLICK</kbd> to view node in modal.`
            : `<kbd>SHIFT</kbd>+<kbd>CLICK</kbd> to open document.`;

        infoTableElement.replaceChildren();
        for (const [name, value] of rows) {
          const termElement = document.createElement("dt");
          termElement.textContent = name;
          const valueElement = document.createElement("dd");
          valueElement.textContent = value;
          infoTableElement.append(termElement, valueElement);
        }
        infoPanelElement.replaceChildren(infoEmptyElement, infoTableElement);
        if (nodeElement.dataset.hasPrimaryAction === "true") {
          infoPanelElement.append(tipLine);
        }
        // Hidden elements have no measurable box. Reveal the panel only when
        // its content changes, then reuse the measured size while it moves.
        const wasHidden = infoPanelElement.hidden;
        infoPanelElement.hidden = false;
        const panelRectangle = infoPanelElement.getBoundingClientRect();
        infoPanelSize = {
          width: panelRectangle.width,
          height: panelRectangle.height,
        };
        infoPanelElement.hidden = wasHidden;
        infoPanelContentNodeElement = nodeElement;
      }
      infoPanelElement.style.left = `${Math.max(
        INFO_PANEL_VIEWPORT_PADDING,
        Math.min(
          pointerEvent.clientX + INFO_PANEL_POINTER_OFFSET,
          window.innerWidth -
            infoPanelSize.width -
            INFO_PANEL_VIEWPORT_PADDING,
        ),
      )}px`;
      infoPanelElement.style.top = `${Math.max(
        INFO_PANEL_VIEWPORT_PADDING,
        Math.min(
          pointerEvent.clientY + INFO_PANEL_POINTER_OFFSET,
          window.innerHeight -
            infoPanelSize.height -
            INFO_PANEL_VIEWPORT_PADDING,
        ),
      )}px`;
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
      ancestorButton.dataset.testid = "tree-map-ancestor";
      ancestorButton.type = "button";
      const ancestorSymbol = document.createElement("span");
      ancestorSymbol.className = CSS_CLASSES.labelSymbol;
      ancestorSymbol.textContent = "↰";
      const ancestorLabel = createLabel(
        ancestor.label,
        CSS_CLASSES.labelAncestor,
        ancestor.count,
      );
      ancestorButton.append(
        ancestorSymbol,
        ancestorLabel,
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
        if (labelElement.classList.contains(CSS_CLASSES.label)) {
          updateLabel(labelElement, "");
        } else {
          labelElement.textContent = "";
          delete labelElement.dataset.count;
        }
        labelElement.removeAttribute("title");
        return;
      }
      const label = getNavigationLabel(node, isCurrent);
      if (labelElement.classList.contains(CSS_CLASSES.label)) {
        updateLabel(labelElement, label, node.count);
      } else {
        labelElement.textContent = label;
        labelElement.title = label;
        if (Number.isInteger(node.count)) {
          labelElement.dataset.count = node.count;
        } else {
          delete labelElement.dataset.count;
        }
      }
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
        sectionElement.classList.add(CSS_CLASSES.sectionShiftActive);
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
      sectionElement.classList.toggle(
        CSS_CLASSES.sectionShiftActive,
        event.shiftKey,
      );
      lastPointerEvent = event;
      pointedNodeElement =
        event.target instanceof Element
          ? event.target.closest(`.${CSS_CLASSES.node}`)
          : null;
      if (pointedNodeElement === null) {
        infoPanelElement.hidden = true;
        return;
      }
      renderInfoPanel(pointedNodeElement, event);
      infoPanelElement.hidden = !event.shiftKey;
    });
    sectionElement.addEventListener("pointerleave", () => {
      sectionElement.classList.remove(CSS_CLASSES.sectionShiftActive);
      pointedNodeElement = null;
      lastPointerEvent = null;
      infoPanelElement.hidden = true;
    });
    document.addEventListener("keyup", (event) => {
      if (event.key === "Shift") {
        sectionElement.classList.remove(CSS_CLASSES.sectionShiftActive);
        infoPanelElement.hidden = true;
      }
    });
    window.addEventListener("blur", () => {
      sectionElement.classList.remove(CSS_CLASSES.sectionShiftActive);
      infoPanelElement.hidden = true;
    });
    window.addEventListener("resize", () => {
      infoPanelSize = null;
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
      notifyStateChange();
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
    return {
      identifier: treeMap.identifier,
      title: treeMap.title,
      sectionElement,
      getUrlState() {
        const focusedNode = getFocusedNode();
        return {
          nodeIdentifier:
            focusedNode === treeMap.root ? null : focusedNode.identifier,
          preview: mapOptions.showCollapsedFolderContent,
        };
      },
      restoreUrlState(urlState) {
        const focusedNode = nodesByIdentifier.get(urlState.nodeIdentifier) ??
          treeMap.root;
        const parentNode = nodeParents.get(focusedNode);
        visitHistory.splice(
          0,
          visitHistory.length,
          ...(parentNode === undefined
            ? [treeMap.root]
            : [parentNode, focusedNode]),
        );
        mapOptions.showCollapsedFolderContent = urlState.preview;
        previewInputElement.checked = urlState.preview;
      },
      render() {
        // Record the attached canvas size before rendering. The observer then
        // ignores its initial notification instead of rebuilding the same DOM.
        const canvasRectangle = canvasElement.getBoundingClientRect();
        canvasWidth = canvasRectangle.width;
        canvasHeight = canvasRectangle.height;
        renderFocusedNode();
      },
    };
  }

  function readUrlState() {
    const parameters = new URLSearchParams(window.location.search);
    return {
      mapIdentifier: parameters.get(URL_PARAMETERS.map),
      nodeIdentifier: parameters.get(URL_PARAMETERS.node),
      preview: parameters.get(URL_PARAMETERS.preview) === "1",
    };
  }

  function writeUrlState(mapIdentifier, mapState) {
    const url = new URL(window.location.href);
    url.searchParams.set(URL_PARAMETERS.map, mapIdentifier);
    if (mapState.nodeIdentifier === null) {
      url.searchParams.delete(URL_PARAMETERS.node);
    } else {
      url.searchParams.set(URL_PARAMETERS.node, mapState.nodeIdentifier);
    }
    if (mapState.preview) {
      url.searchParams.set(URL_PARAMETERS.preview, "1");
    } else {
      url.searchParams.delete(URL_PARAMETERS.preview);
    }
    window.history.replaceState(window.history.state, "", url);
  }

  function renderTreeMaps(renderOptions = {}) {
    const rootElement = document.getElementById(DOM_IDS.root);
    const dataElement = document.getElementById(DOM_IDS.data);
    const selectorLabelElement = document.getElementById(
      DOM_IDS.selectorLabel,
    );
    const selectorMenuElement = document.getElementById(
      DOM_IDS.selectorMenu,
    );
    if (
      rootElement === null ||
      dataElement === null ||
      selectorLabelElement === null ||
      selectorMenuElement === null
    ) {
      return;
    }

    const options = {
      ...DEFAULT_RENDER_OPTIONS,
      ...renderOptions,
    };
    applyPageGeometryProperties(rootElement, options);
    const treeMapData = JSON.parse(dataElement.textContent);
    const controllers = new Map();
    const selectorItems = new Map();
    let activeIdentifier = null;

    function selectTreeMap(identifier, updateUrl = true) {
      const controller = controllers.get(identifier);
      if (controller === undefined) {
        return;
      }
      activeIdentifier = identifier;
      rootElement.replaceChildren(controller.sectionElement);
      selectorLabelElement.textContent = controller.title;
      for (const [itemIdentifier, itemElement] of selectorItems) {
        const isActive = itemIdentifier === identifier;
        itemElement.classList.toggle("active", isActive);
        itemElement.toggleAttribute("aria-current", isActive);
      }
      controller.render();
      if (updateUrl) {
        writeUrlState(identifier, controller.getUrlState());
      }
    }

    for (const treeMap of treeMapData.tree_maps) {
      if (controllers.has(treeMap.identifier)) {
        throw new Error(`Duplicate tree map identifier: ${treeMap.identifier}`);
      }
      const controller = createTreeMap(treeMap, options, (mapState) => {
        if (activeIdentifier === treeMap.identifier) {
          writeUrlState(treeMap.identifier, mapState);
        }
      });
      controllers.set(controller.identifier, controller);

      const itemElement = document.createElement("a");
      itemElement.className = "dropdown_menu_item";
      itemElement.href = "#";
      itemElement.textContent = controller.title;
      itemElement.dataset.testid =
        `tree-map-selector-option-${controller.identifier}`;
      itemElement.addEventListener("click", (event) => {
        event.preventDefault();
        selectTreeMap(controller.identifier);
      });
      const listItemElement = document.createElement("li");
      listItemElement.append(itemElement);
      selectorMenuElement.append(listItemElement);
      selectorItems.set(controller.identifier, itemElement);
    }

    const firstController = controllers.values().next().value;
    if (firstController !== undefined) {
      const urlState = readUrlState();
      const initialController =
        controllers.get(urlState.mapIdentifier) ?? firstController;
      initialController.restoreUrlState(urlState);
      selectTreeMap(initialController.identifier);
    }

    window.addEventListener("popstate", () => {
      const urlState = readUrlState();
      const controller =
        controllers.get(urlState.mapIdentifier) ?? firstController;
      if (controller === undefined) {
        return;
      }
      controller.restoreUrlState(urlState);
      selectTreeMap(controller.identifier, false);
    });
  }

  function initializeModifierClickGuard() {
    const rootElement = document.getElementById(DOM_IDS.root);
    if (rootElement === null) {
      return;
    }
    document.addEventListener(
      "click",
      (event) => {
        if (!event.shiftKey) {
          return;
        }
        const nodeElement =
          event.target instanceof Element
            ? event.target.closest(`.${CSS_CLASSES.node}`)
            : null;
        if (nodeElement !== null) {
          return;
        }
        // Tree map reserves both Shift+Click combinations for node actions.
        // Suppress them elsewhere on this screen so a modifier left pressed
        // after using the map cannot trigger a link or button action.
        event.preventDefault();
        event.stopImmediatePropagation();
      },
      true,
    );
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
  initializeModifierClickGuard();
  renderTreeMaps();
})();
