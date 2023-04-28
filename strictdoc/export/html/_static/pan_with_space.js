// This code in this file is a simplified version of the StackOverflow answer
// taken from: https://stackoverflow.com/a/33948409/598057.

const MOUSEMOVE_SPEED_FACTOR = 1;
const KEYDOWN_SPEED_FACTOR = 20;
const PWS_SELECTOR = "[js-pan_with_space]";

function getPanElement() {
  const element = document.querySelector(PWS_SELECTOR);
  return element;
}

window.addEventListener('load', function () {
  var state = {
    spacePressed: false,
    isDown: false,
    startX: 0,
    startY: 0
  }

  const element = getPanElement();
  if (element) {
    console.assert(!!element, "Expected a valid element.");

    document.addEventListener("keydown", function (e) {
      if (e.key === ' ' || e.key === 'Spacebar') {
        // ' ' is standard, 'Spacebar' was used by IE9 and Firefox < 37

        e.preventDefault();
        e.stopPropagation();
        state.spacePressed = true;
        element.style.cursor = 'move';
        element.style.scrollBehavior = 'auto';
        return;
      }

      var moveFactor = KEYDOWN_SPEED_FACTOR;
      if (e.altKey) {
        moveFactor = KEYDOWN_SPEED_FACTOR * 10;
      }

      if (e.key === 'ArrowDown') {
        e.preventDefault();
        e.stopPropagation();
        element.scrollTop = element.scrollTop + moveFactor;
      }
      else if (e.key === 'ArrowUp') {
        e.preventDefault();
        e.stopPropagation();
        element.scrollTop = element.scrollTop - moveFactor;
      }
      else if (e.key === 'ArrowLeft') {
        e.preventDefault();
        e.stopPropagation();
        element.scrollLeft = element.scrollLeft - moveFactor;
      }
      else if (e.key === 'ArrowRight') {
        e.preventDefault();
        e.stopPropagation();
        element.scrollLeft = element.scrollLeft + moveFactor;
      }
    })

    document.addEventListener("keyup", function (e) {
      if (e.key === ' ' || e.key === 'Spacebar') {
        // ' ' is standard, 'Spacebar' was used by IE9 and Firefox < 37
        e.preventDefault();
        e.stopPropagation();
        state.spacePressed = false;
        element.style.cursor = 'default';
        element.style.scrollBehavior = '';
      }
    });

    element.addEventListener("mousedown", function (e) {
      if (!state.spacePressed) {
        return;
      }

      // Tell the browser we're handling this event.
      e.preventDefault();
      e.stopPropagation();

      // Calc the starting mouse X,Y for the drag.
      state.startX = parseInt(e.clientX);
      state.startY = parseInt(e.clientY);

      var mouseX = parseInt(e.clientX);
      var mouseY = parseInt(e.clientY);

      state.isDown = true;
    });

    element.addEventListener("mouseup", function (e) {
      if (!state.spacePressed) {
        return;
      }

      e.preventDefault();
      e.stopPropagation();

      state.isDown = false;
    });

    element.addEventListener("mousemove", function (e) {
      if (!state.isDown) {
        return;
      }

      if (!state.spacePressed) {
        return;
      }

      e.preventDefault();
      e.stopPropagation();

      var mouseX = parseInt(e.clientX);
      var mouseY = parseInt(e.clientY);

      var dx = mouseX - state.startX;
      var dy = mouseY - state.startY;

      state.startX = mouseX;
      state.startY = mouseY;

      var speedupFactor = MOUSEMOVE_SPEED_FACTOR;
      element.scrollTo(
        element.scrollLeft - dx * speedupFactor, element.scrollTop - dy * speedupFactor
      );
    });

    element.addEventListener("mouseleave", function (e) {
      // Tell the browser we're handling this event.
      e.preventDefault();
      e.stopPropagation();

      state.isDown = false;
    });
  }
});

// When a window is loaded, scroll to the central column of the DTR tree.
// The central column is the one where the current document's requirements are
// listed top-to-bottom.
document.addEventListener("DOMContentLoaded", function(event) {
  const element = getPanElement();
  if (element) {
    const firstNode = element.querySelector('.content_item[data-role="current"]');
    firstNode && firstNode.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
  }
});
