/*
 * Finds <pre class="plantuml"> blocks, encodes their text content using
 * PlantUML's text-encoding format (raw DEFLATE + a custom 6-bit alphabet),
 * and replaces each block with an <img> pointing at a PlantUML server that
 * renders the diagram to SVG.
 */
(function () {
  "use strict";

  function encode6bit(b) {
    if (b < 10) {
      return String.fromCharCode(48 + b);
    }
    b -= 10;
    if (b < 26) {
      return String.fromCharCode(65 + b);
    }
    b -= 26;
    if (b < 26) {
      return String.fromCharCode(97 + b);
    }
    b -= 26;
    if (b === 0) {
      return "-";
    }
    if (b === 1) {
      return "_";
    }
    return "?";
  }

  function append3bytes(b1, b2, b3) {
    var c1 = b1 >> 2;
    var c2 = ((b1 & 0x3) << 4) | (b2 >> 4);
    var c3 = ((b2 & 0xf) << 2) | (b3 >> 6);
    var c4 = b3 & 0x3f;
    return (
      encode6bit(c1 & 0x3f) +
      encode6bit(c2 & 0x3f) +
      encode6bit(c3 & 0x3f) +
      encode6bit(c4 & 0x3f)
    );
  }

  function encode64(data) {
    var result = "";
    for (var i = 0; i < data.length; i += 3) {
      if (i + 2 === data.length) {
        result += append3bytes(data[i], data[i + 1], 0);
      } else if (i + 1 === data.length) {
        result += append3bytes(data[i], 0, 0);
      } else {
        result += append3bytes(data[i], data[i + 1], data[i + 2]);
      }
    }
    return result;
  }

  async function deflateRaw(bytes) {
    var stream = new Blob([bytes])
      .stream()
      .pipeThrough(new CompressionStream("deflate-raw"));
    var buffer = await new Response(stream).arrayBuffer();
    return new Uint8Array(buffer);
  }

  async function encodePlantUML(text) {
    var utf8Bytes = new TextEncoder().encode(text);
    var deflated = await deflateRaw(utf8Bytes);
    return encode64(deflated);
  }

  async function renderPlantUMLBlocks(serverUrl) {
    var blocks = document.querySelectorAll("pre.plantuml");
    for (var i = 0; i < blocks.length; i++) {
      var block = blocks[i];
      var diagramText = block.textContent;
      var encoded = await encodePlantUML(diagramText);
      var img = document.createElement("img");
      img.className = "plantuml";
      img.src = serverUrl.replace(/\/$/, "") + "/svg/" + encoded;
      img.alt = "PlantUML diagram";
      block.replaceWith(img);
    }
  }

  window.strictdocRenderPlantUML = renderPlantUMLBlocks;
})();
