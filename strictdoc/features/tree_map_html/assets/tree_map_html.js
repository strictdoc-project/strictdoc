// @relation(SDOC-SRS-157, scope=file)

(function () {
  "use strict";

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

  function layoutChildren(children) {
    const totalWeight = children.reduce(
      (total, child) => total + getNodeWeight(child),
      0,
    );
    if (totalWeight <= 0) {
      return [];
    }

    const remainingItems = children
      .map((node) => ({
        node,
        area: (getNodeWeight(node) / totalWeight) * 10000,
      }))
      .sort((left, right) => right.area - left.area);
    const rectangle = { x: 0, y: 0, width: 100, height: 100 };
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
    return positionedItems;
  }

  function applyRectangle(nodeElement, rectangle) {
    nodeElement.style.left = `${rectangle.x}%`;
    nodeElement.style.top = `${rectangle.y}%`;
    nodeElement.style.width = `${rectangle.width}%`;
    nodeElement.style.height = `${rectangle.height}%`;
  }

  function createNode(node, depth, rectangle) {
    const nodeElement = document.createElement("div");
    nodeElement.className = "tree-map-html__node";
    nodeElement.dataset.depth = depth;
    const nodeWeight = getNodeWeight(node);
    nodeElement.dataset.weight = nodeWeight;
    nodeElement.style.backgroundColor = node.color;
    nodeElement.title = `${node.label} (${node.weight})`;
    applyRectangle(nodeElement, rectangle);

    const labelElement = document.createElement("span");
    labelElement.className = "tree-map-html__label";
    labelElement.textContent = node.label;
    nodeElement.append(labelElement);

    if (node.children.length === 0) {
      nodeElement.classList.add("tree-map-html__node--leaf");
      return nodeElement;
    }

    const childrenElement = document.createElement("div");
    childrenElement.className = "tree-map-html__children";
    for (const childRectangle of layoutChildren(node.children)) {
      childrenElement.append(
        createNode(childRectangle.node, depth + 1, childRectangle),
      );
    }
    nodeElement.append(childrenElement);
    return nodeElement;
  }

  function createTreeMap(treeMap) {
    const sectionElement = document.createElement("section");
    sectionElement.className = "tree-map-html__section";

    const titleElement = document.createElement("h2");
    titleElement.className = "tree-map-html__title";
    titleElement.textContent = treeMap.title;
    sectionElement.append(titleElement);

    const canvasElement = document.createElement("div");
    canvasElement.className = "tree-map-html__canvas";
    canvasElement.append(
      createNode(treeMap.root, 0, {
        x: 0,
        y: 0,
        width: 100,
        height: 100,
      }),
    );
    sectionElement.append(canvasElement);
    return sectionElement;
  }

  function renderTreeMaps() {
    const rootElement = document.getElementById("tree-map-html-root");
    const dataElement = document.getElementById("tree-map-html-data");
    if (rootElement === null || dataElement === null) {
      return;
    }

    const treeMapData = JSON.parse(dataElement.textContent);
    for (const treeMap of treeMapData.tree_maps) {
      rootElement.append(createTreeMap(treeMap));
    }
  }

  renderTreeMaps();
})();
