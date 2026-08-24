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

  function createNode(node, depth) {
    const nodeElement = document.createElement("div");
    nodeElement.className = "tree-map-html__node";
    nodeElement.dataset.depth = depth;
    const nodeWeight = getNodeWeight(node);
    nodeElement.dataset.weight = nodeWeight;
    nodeElement.style.backgroundColor = node.color;
    nodeElement.style.flexGrow = nodeWeight;
    nodeElement.title = `${node.label} (${node.weight})`;

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
    childrenElement.dataset.direction = depth % 2 === 0 ? "row" : "column";
    for (const child of node.children) {
      childrenElement.append(createNode(child, depth + 1));
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
    canvasElement.append(createNode(treeMap.root, 0));
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
