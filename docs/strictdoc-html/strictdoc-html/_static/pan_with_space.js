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

  document.addEventListener("mousedown", function (e) {
    if (!state.spacePressed) {
      return;
    }

    // tell the browser we're handling this event
    e.preventDefault();
    e.stopPropagation();

    // calc the starting mouse X,Y for the drag
    state.startX = parseInt(e.clientX);
    state.startY = parseInt(e.clientY);

    var mouseX = parseInt(e.clientX);
    var mouseY = parseInt(e.clientY);

    state.isDown = true;
  });

  document.addEventListener("mouseup", function (e) {
    if (!state.spacePressed) {
      return;
    }

    e.preventDefault();
    e.stopPropagation();

    state.isDown = false;
  });

  document.addEventListener("mousemove", function (e) {
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

    var speedupFactor = 2;
    element.scrollTop = element.scrollTop - dy * speedupFactor;
    element.scrollLeft = element.scrollLeft - dx * speedupFactor;
  });

  document.addEventListener("mouseleave", function (e) {
    // tell the browser we're handling this event
    e.preventDefault();
    e.stopPropagation();

    state.isDown = false;
  });
});
