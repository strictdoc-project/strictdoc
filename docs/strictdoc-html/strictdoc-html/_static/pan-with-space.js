// This code in this file is a simplified version of the StackOverflow answer
// taken from: https://stackoverflow.com/a/33948409/598057.

$(document).ready(function () {
  var state = {
    spacePressed: false,
    isDown: false,
    startX: 0,
    startY: 0
  }

  var element = '.layout_main';

  $(window).keydown(function (e) {
    if (e.key === ' ' || e.key === 'Spacebar') {
      // ' ' is standard, 'Spacebar' was used by IE9 and Firefox < 37

      e.preventDefault();
      e.stopPropagation();
      state.spacePressed = true;
      $(element).css('cursor', 'move');
    }

    var moveFactor = 20;
    if (e.altKey) {
      moveFactor = 250;
    }

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      e.stopPropagation();
      $(element).scrollTop($(element).scrollTop() + moveFactor);
    }
    else if (e.key === 'ArrowUp') {
      e.preventDefault();
      e.stopPropagation();
      $(element).scrollTop($(element).scrollTop() - moveFactor);
    }
    else if (e.key === 'ArrowLeft') {
      e.preventDefault();
      e.stopPropagation();
      $(element).scrollLeft($(element).scrollLeft() - moveFactor);
    }
    else if (e.key === 'ArrowRight') {
      e.preventDefault();
      e.stopPropagation();
      $(element).scrollLeft($(element).scrollLeft() + moveFactor);
    }
  })

  $(window).keyup(function (e) {
    if (e.key === ' ' || e.key === 'Spacebar') {
      // ' ' is standard, 'Spacebar' was used by IE9 and Firefox < 37
      e.preventDefault();
      e.stopPropagation();
      state.spacePressed = false;
      $(element).css('cursor', 'default');
    }
  })

  $(element).mousedown(function (e) {
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

  $(element).mouseup(function (e) {
    if (!state.spacePressed) {
      return;
    }

    e.preventDefault();
    e.stopPropagation();

    state.isDown = false;
  });

  $(element).mousemove(function (e) {
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
    $(element).scrollTop($(element).scrollTop() - dy * speedupFactor);
    $(element).scrollLeft($(element).scrollLeft() - dx * speedupFactor);
  });

  $(element).mouseleave(function (e) {
    // tell the browser we're handling this event
    e.preventDefault();
    e.stopPropagation();

    state.isDown = false;
  });
});
