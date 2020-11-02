// This code in this file is a simplified version of the StackOverflow answer
// taken from: https://stackoverflow.com/a/33948409/598057.

var state = {
  spacePressed: false,
  isDown: false,
  startX: 0,
  startY: 0
}

$(window).keydown(function (e) {
  if (e.key === ' ' || e.key === 'Spacebar') {
    // ' ' is standard, 'Spacebar' was used by IE9 and Firefox < 37
    e.preventDefault();
    // console.log('Space pressed');
    state.spacePressed = true;
  }
})

$(window).keyup(function (e) {
  if (e.key === ' ' || e.key === 'Spacebar') {
    // ' ' is standard, 'Spacebar' was used by IE9 and Firefox < 37
    e.preventDefault();
    //console.log('Space keyup');
    state.spacePressed = false;
  }
})

$(document).mousedown(function (e) {
  // console.log("mouse down");

  if (!state.spacePressed) {
    return;
  }

  // tell the browser we're handling this event
  e.preventDefault();
  e.stopPropagation();

  // calc the starting mouse X,Y for the drag
  state.startX = parseInt(e.clientX);
  state.startY = parseInt(e.clientY);

  state.isDown = true;
});

$(document).mouseup(function (e) {
  // console.log("mouse up");
  // tell the browser we're handling this event

  if (!state.spacePressed) {
    return;
  }

  e.preventDefault();
  e.stopPropagation();

  state.isDown = false;
});

$(document).mousemove(function (e) {
  // console.log("mouse move");

  // only do this code if the mouse is being dragged
  if (!state.isDown){
    return;
  }

  if (!state.spacePressed) {
    return;
  }

  // tell the browser we're handling this event
  e.preventDefault();
  e.stopPropagation();

  // get the current mouse position
  var mouseX = parseInt(e.clientX);
  var mouseY = parseInt(e.clientY);

  // dx & dy are the distance the mouse has moved since
  // the last mousemove event
  var dx = mouseX - state.startX;
  var dy = mouseY - state.startY;

  // reset the vars for next mousemove
  state.startX = mouseX;
  state.startY = mouseY;

  if (state.spacePressed) {
    window.scrollBy(-dx, -dy);
  }
});

$(document).mouseleave(function (e) {
  // console.log("mouse out");

  // tell the browser we're handling this event
  e.preventDefault();
  e.stopPropagation();

  state.isDown=false;
});
