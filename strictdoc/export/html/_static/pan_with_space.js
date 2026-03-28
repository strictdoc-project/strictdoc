// This code in this file is a simplified version of the StackOverflow answer
// taken from: https://stackoverflow.com/a/33948409/598057.

(function () {
const MOUSEMOVE_SPEED_FACTOR = 1;
const KEYDOWN_SPEED_FACTOR = 20;
const PWS_SELECTOR = "[js-pan_with_space]";
const GLOBAL_BIND_FLAG = "__strictdocPanWithSpaceBound";

function getPanElement() {
  return document.querySelector(PWS_SELECTOR);
}

function getPanElements() {
  return document.querySelectorAll(PWS_SELECTOR);
}

const state = {
  spacePressed: false,
  isDown: false,
  startX: 0,
  startY: 0,
  activeElement: null,
};

function getActivePanElement() {
  if (state.activeElement && state.activeElement.isConnected) {
    return state.activeElement;
  }
  return getPanElement();
}

function normalizeTarget(target) {
  if (target instanceof Element) {
    return target;
  }
  if (target instanceof Node) {
    return target.parentElement;
  }
  return null;
}

function getPanElementFromTarget(target) {
  const element = normalizeTarget(target);
  if (!element) {
    return null;
  }
  return element.closest(PWS_SELECTOR);
}

function setPanCursor(element, active) {
  if (!element) {
    return;
  }
  element.style.cursor = active ? "move" : "";
  element.style.scrollBehavior = active ? "auto" : "";
}

function setPanCursorOnAll(active) {
  getPanElements().forEach((element) => {
    setPanCursor(element, active);
  });
}

function clearPanState() {
  setPanCursorOnAll(false);
  state.spacePressed = false;
  state.isDown = false;
  state.activeElement = null;
}

function installGlobalListeners() {
  if (window[GLOBAL_BIND_FLAG] === true) {
    return;
  }
  window[GLOBAL_BIND_FLAG] = true;

  document.addEventListener("keydown", function (e) {
    const element = getPanElement();
    if (!element) {
      return;
    }
    if (e.key === ' ' || e.key === 'Spacebar') {
      // ' ' is standard, 'Spacebar' was used by IE9 and Firefox < 37
      e.preventDefault();
      e.stopPropagation();
      state.spacePressed = true;
      setPanCursorOnAll(true);
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
  });

  document.addEventListener("keyup", function (e) {
    if (e.key !== ' ' && e.key !== 'Spacebar') {
      return;
    }
    // ' ' is standard, 'Spacebar' was used by IE9 and Firefox < 37
    e.preventDefault();
    e.stopPropagation();
    clearPanState();
  });

  document.addEventListener("mouseup", function () {
    state.isDown = false;
  });

  document.addEventListener("mousedown", function (e) {
    if (!state.spacePressed) {
      return;
    }

    const element = getPanElementFromTarget(e.target);
    if (!element) {
      return;
    }

    e.preventDefault();
    e.stopPropagation();

    state.activeElement = element;
    state.startX = parseInt(e.clientX);
    state.startY = parseInt(e.clientY);
    state.isDown = true;
    setPanCursor(element, true);
  });

  document.addEventListener("mousemove", function (e) {
    const element = getActivePanElement();
    if (!state.isDown || !state.spacePressed || !element) {
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

  // Work planner cards are draggable, which otherwise steals the gesture
  // before the scroll container receives mousemove events.
  document.addEventListener("dragstart", function (e) {
    if (!state.spacePressed) {
      return;
    }
    const element = getPanElementFromTarget(e.target);
    if (!element) {
      return;
    }
    e.preventDefault();
    e.stopPropagation();
    state.isDown = false;
  });

  window.addEventListener("blur", clearPanState);

  document.addEventListener("turbo:before-stream-render", function () {
    clearPanState();
  });

  document.addEventListener("turbo:frame-render", function () {
    if (state.spacePressed) {
      setPanCursorOnAll(true);
    }
  });
}

window.addEventListener('load', installGlobalListeners);
document.addEventListener("DOMContentLoaded", installGlobalListeners);

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
})();
