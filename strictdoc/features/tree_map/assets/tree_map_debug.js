// @relation(SDOC-SRS-157, scope=file)

(function () {
  "use strict";

  const searchParameters = new URLSearchParams(window.location.search);
  if (searchParameters.get("debug") !== "1") {
    return;
  }

  function createLeaf(identifier, label, weight, color) {
    return {
      identifier,
      label,
      weight,
      color,
      children: [],
    };
  }

  function createDeepBranch(depth, maximumDepth) {
    const children = [
      createLeaf(
        `debug-depth-${depth}-leaf`,
        `Depth ${depth} leaf`,
        10,
        "#b8d8f0",
      ),
    ];
    if (depth < maximumDepth) {
      children.push(createDeepBranch(depth + 1, maximumDepth));
    }
    return {
      identifier: `debug-deep-${depth}`,
      label: `Deep branch level ${depth}`,
      weight: 0,
      color: "#8fbfe0",
      children,
    };
  }

  function createWideBranch(size) {
    return {
      identifier: `debug-wide-${size}`,
      label: `Wide branch: ${size} leaves`,
      weight: 0,
      color: "#a8ddb5",
      children: Array.from({ length: size }, (_, index) =>
        createLeaf(
          `debug-wide-${size}-leaf-${index + 1}`,
          `Wide leaf ${index + 1}`,
          10,
          "#c7e9c0",
        ),
      ),
    };
  }

  function createUnevenBranch(weights) {
    return {
      identifier: "debug-uneven",
      label: "Uneven weights",
      weight: 0,
      color: "#fdae6b",
      children: weights.map((weight, index) =>
        createLeaf(
          `debug-uneven-${index + 1}`,
          `Weight ${weight}`,
          weight,
          "#fdd0a2",
        ),
      ),
    };
  }

  function createNodeBudgetBranch(size) {
    return {
      identifier: `debug-budget-${size}`,
      label: `Node budget: ${size} leaves`,
      weight: 0,
      color: "#dadaeb",
      children: Array.from({ length: size }, (_, index) =>
        createLeaf(
          `debug-budget-${size}-leaf-${index + 1}`,
          `Budget leaf ${index + 1}`,
          1,
          "#bcbddc",
        ),
      ),
    };
  }

  function generateDebugData() {
    return {
      identifier: "renderer-debug",
      title: "Renderer debug tree",
      root: {
        identifier: "debug-root",
        label: "Debug root",
        weight: 0,
        color: "#d8d8d8",
        children: [
          createDeepBranch(1, 10),
          createWideBranch(24),
          createUnevenBranch([80, 30, 12, 5, 2, 1]),
          createNodeBudgetBranch(666),
        ],
      },
    };
  }

  const dataElement = document.getElementById("tree-map-data");
  if (dataElement !== null) {
    const treeMapData = JSON.parse(dataElement.textContent);
    treeMapData.tree_maps.push(generateDebugData());
    dataElement.textContent = JSON.stringify(treeMapData);
  }
})();
