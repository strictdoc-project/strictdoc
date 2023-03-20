// This code in this file is a simplified version of the StackOverflow answer
// taken from: https://stackoverflow.com/a/33948409/598057.

window.addEventListener('load', function () {
  var state = {
    spacePressed: false,
    isDown: false,
    startX: 0,
    startY: 0
  }

  const element = document.getElementById('pan_with_space');
  console.assert(!!element, "Expected a valid element.");

  document.addEventListener("keydown", function (e) {
    if (e.key === ' ' || e.key === 'Spacebar') {
      // ' ' is standard, 'Spacebar' was used by IE9 and Firefox < 37

      e.preventDefault();
      e.stopPropagation();
      state.spacePressed = true;
      element.style.cursor = 'move';
      return;
    }

    var moveFactor = 20;
    if (e.altKey) {
      moveFactor = 250;
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

    var speedupFactor = 10;
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
});

// When a window is loaded, scroll to the central column of the DTR tree.
// The central column is the one where the current document's requirements are
// listed top-to-bottom.
document.addEventListener("DOMContentLoaded", function(event) {
  const element = document.getElementById('pan_with_space');
  const firstNode = document.querySelector('.content_item[data-role="current"]');

  const elementViewportOffset = element.getBoundingClientRect();
  const firstNodeViewportOffset = firstNode.getBoundingClientRect();

  const leftDiff = firstNodeViewportOffset.x - elementViewportOffset.x;

  element.scrollTo(
    leftDiff - window.screen.width / 2 + firstNode.offsetWidth / 2,
    0,
  );
});
