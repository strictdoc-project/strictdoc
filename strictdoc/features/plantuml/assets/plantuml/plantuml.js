/*
 * Finds <pre class="plantuml"> blocks and renders each one in place as an
 * inline SVG, using the locally vendored PlantUML engine (plantuml-core.js
 * plus its Graphviz/Viz.js dependency, viz-global.js). No server round trip
 * is involved: diagram source never leaves the browser.
 *
 * Loaded as a classic script, not a module: ES module scripts are
 * CORS-blocked when a document is opened via file:// (e.g. StrictDoc's own
 * HTML2PDF export, or a user opening exported HTML directly from disk),
 * while classic scripts are not. plantuml-core.js is likewise vendored as a
 * classic script exposing window.PlantUMLCore instead of using ESM export.
 */
(function () {
  "use strict";

  function renderBlock(block) {
    var diagramText = block.textContent;
    var lines = diagramText.split(/\r\n|\r|\n/);
    return new Promise(function (resolve, reject) {
      window.PlantUMLCore.renderToString(
        lines,
        function (svg) {
          block.innerHTML = svg;
          resolve();
        },
        function (message) {
          reject(new Error(message));
        }
      );
    });
  }

  async function renderPlantUMLBlocks() {
    // "data-processed" mirrors Mermaid's own marker: it lets repeated
    // calls (e.g. after a Turbo Stream node update) skip diagrams that are
    // already rendered, since their pre.plantuml text content has been
    // replaced by rendered SVG markup and re-rendering it would fail.
    var blocks = document.querySelectorAll(
      "pre.plantuml:not([data-processed])"
    );
    for (var i = 0; i < blocks.length; i++) {
      var block = blocks[i];
      await renderBlock(block);
      block.setAttribute("data-processed", "true");
    }
  }

  window.strictdocRenderPlantUML = renderPlantUMLBlocks;
})();
