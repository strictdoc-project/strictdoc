// @relation(SDOC-SRS-157, scope=file)

(function () {
  "use strict";

  function createLeaf(label, weight, color) {
    return {
      label,
      weight,
      color,
      children: [],
    };
  }

  function createDeepBranch(depth, maximumDepth) {
    const children = [
      createLeaf(`Depth ${depth} leaf`, 10, "#b8d8f0"),
    ];
    if (depth < maximumDepth) {
      children.push(createDeepBranch(depth + 1, maximumDepth));
    }
    return {
      label: `Deep branch level ${depth}`,
      weight: 0,
      color: "#8fbfe0",
      children,
    };
  }

  function createWideBranch(size) {
    return {
      label: `Wide branch: ${size} leaves`,
      weight: 0,
      color: "#a8ddb5",
      children: Array.from({ length: size }, (_, index) =>
        createLeaf(`Wide leaf ${index + 1}`, 10, "#c7e9c0"),
      ),
    };
  }

  function createUnevenBranch(weights) {
    return {
      label: "Uneven weights",
      weight: 0,
      color: "#fdae6b",
      children: weights.map((weight) =>
        createLeaf(`Weight ${weight}`, weight, "#fdd0a2"),
      ),
    };
  }

  function createNodeBudgetBranch(size) {
    return {
      label: `Node budget: ${size} leaves`,
      weight: 0,
      color: "#dadaeb",
      children: Array.from({ length: size }, (_, index) =>
        createLeaf(`Budget leaf ${index + 1}`, 1, "#bcbddc"),
      ),
    };
  }

  function generateDebugData() {
    return {
      tree_maps: [
        {
          title: "Renderer debug tree",
          root: {
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
        },
      ],
    };
  }

  const dataElement = document.getElementById("tree-map-html-data");
  if (dataElement !== null) {
    dataElement.textContent = JSON.stringify(generateDebugData());
  }
})();
