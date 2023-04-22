


// Expected:
// js-resizable_bar="tree"
// data-state="open"
// data-position="left"

// ! Right now, the code only considers one possibility for the panels
// ! to the left of the main part.

const BAR_ATTRIBUTE = 'js-resizable_bar';
const BAR_MIN_WIDTH = 100;
const BAR_CLOSED_WIDTH = 12;
const BAR_MAX_VW = '25vw';

const BAR_HANDLER_WIDTH = 8;

const BAR_COLOR_MAIN = 'var(--color-fg-main, Black)';
const BAR_COLOR_BACKGROUND = 'var(--color-bg-main, White)';
const BAR_COLOR_ACTIVE = 'var(--color-fg-accent, currentColor)';
const BAR_COLOR_BORDER = 'var(--color-border, rgba(0,0,0,0.1))';

const STYLE = `
[${BAR_ATTRIBUTE}]::after {
  opacity: 0;
  transition: .3s;
  pointer-events: none;
}

[${BAR_ATTRIBUTE}] {
  position: relative;
  height: 100%;
  max-width: ${BAR_MAX_VW};
}

[${BAR_ATTRIBUTE}]:hover {
  z-index: 22;
}

[${BAR_ATTRIBUTE}][data-state="open"] {
  min-width: ${BAR_MIN_WIDTH}px;
  pointer-events: auto;
}
[${BAR_ATTRIBUTE}][data-state="closed"] {
  max-width: ${BAR_CLOSED_WIDTH}px;
  min-width: ${BAR_CLOSED_WIDTH}px;
  pointer-events: none;
  transition: .5s;
}

[${BAR_ATTRIBUTE}][data-position="left"] {
  border-left: none;
}
[${BAR_ATTRIBUTE}][data-position="right"] {
  border-right: none;
}

[${BAR_ATTRIBUTE}-handler] {
  pointer-events: auto;
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 10;
  width: ${BAR_HANDLER_WIDTH}px;
  color: ${BAR_COLOR_ACTIVE};
}

[${BAR_ATTRIBUTE}-border] {
  pointer-events: auto;
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  width: ${BAR_HANDLER_WIDTH}px;
  background: transparent;
  transition: .3s;
  cursor: col-resize;
}

[${BAR_ATTRIBUTE}][data-state="closed"] [${BAR_ATTRIBUTE}-border] {
  cursor: e-resize;
}

[${BAR_ATTRIBUTE}-border]::before {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  width: 1px;
  background: ${BAR_COLOR_BORDER};
  transition: .3s;
}

[${BAR_ATTRIBUTE}-border]::after {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  width: ${0.5 * BAR_HANDLER_WIDTH}px;
  background: transparent;
  transition: .3s;
}

[${BAR_ATTRIBUTE}][data-position="left"] [${BAR_ATTRIBUTE}-border]::before {
  right: 0;
  left: unset;
}
[${BAR_ATTRIBUTE}][data-position="left"] [${BAR_ATTRIBUTE}-border]::after {
  right: ${-0.25 * BAR_HANDLER_WIDTH}px;
  left: unset;
}

[${BAR_ATTRIBUTE}][data-position="right"] [${BAR_ATTRIBUTE}-border]::before {
  right: unset;
  left: 0;
}
[${BAR_ATTRIBUTE}][data-position="right"] [${BAR_ATTRIBUTE}-border]::after {
  right: unset;
  left: ${-0.25 * BAR_HANDLER_WIDTH}px;
}

[${BAR_ATTRIBUTE}-border]:hover::after {
  background: ${BAR_COLOR_ACTIVE};
}

[${BAR_ATTRIBUTE}-button] {
  cursor: pointer;
  position: absolute;
  z-index: 2;
  left: 0;
  top: ${-1 * BAR_HANDLER_WIDTH}px;
  box-sizing: border-box;
  width: ${2 * BAR_HANDLER_WIDTH}px;
  height: ${2 * BAR_HANDLER_WIDTH}px;
  font-size: ${1.5 * BAR_HANDLER_WIDTH}px;
  font-weight: bold;
  border-radius: 50%;
  border-width: 1px;
  border-style: solid;
  border-color: ${BAR_COLOR_BACKGROUND};
  background: ${BAR_COLOR_BACKGROUND};
  color: ${BAR_COLOR_ACTIVE};
  transition: .3s;
}

[${BAR_ATTRIBUTE}-button]:hover {
  color: ${BAR_COLOR_MAIN};
  border-color: ${BAR_COLOR_MAIN};
}

/* ❮❯ */
[${BAR_ATTRIBUTE}-button]::after {
  content: '❮';
  position: absolute;
  display: flex;
  align-items: center;
  justify-content: center;
  left: 0;
  right: 0;
  top: ${-1 * BAR_HANDLER_WIDTH}px;
  bottom: ${-1 * BAR_HANDLER_WIDTH}px;
}
[${BAR_ATTRIBUTE}][data-state="open"] [${BAR_ATTRIBUTE}-button]::after {
  content: '❮';
}
[${BAR_ATTRIBUTE}][data-state="closed"] [${BAR_ATTRIBUTE}-button]::after {
  content: '❯';
}

[${BAR_ATTRIBUTE}-scroll] {
  height: 100%;
  overflow-x: hidden;
  overflow-y: scroll;
  padding: calc(var(--base-rhythm)*2);
  padding-bottom: calc(var(--base-rhythm)*8);
  scrollbar-color: transparent var(--scrollbarBG);
  /* scrollbar-width: thin; */
}
[${BAR_ATTRIBUTE}-scroll='y'] {
  overflow-x: hidden;
  overflow-y: scroll;
}
[${BAR_ATTRIBUTE}-scroll]:hover {
  scrollbar-color: var(--thumbBG) var(--scrollbarBG);
}
[${BAR_ATTRIBUTE}-scroll]::-webkit-scrollbar {
  /* width: var(--base-rhythm); */
}
[${BAR_ATTRIBUTE}-scroll]::-webkit-scrollbar-thumb {
  background-color: transparent;
}
[${BAR_ATTRIBUTE}-scroll]:hover::-webkit-scrollbar-thumb {
  background-color: var(--thumbBG)
}

[data-state="closed"] [${BAR_ATTRIBUTE}-scroll] {
  display: none;
}
`;

class ResizableBar {
  constructor({
    barAttribute,
    barStyle,
    barGravity,
  }) {
    this.barAttribute = barAttribute || 'js-resizable_bar';
    this.barStyle = barStyle;
    this.barGravity = barGravity || 100;

    // state
    this.state = [];

    // current
    this.activeID = null;
    this.pageX = null;

    // subscribe
    const _this = this;
    this._mouseDownHandler = (e) => {_this._onMouseDown(e)};
    this._mouseMoveHandler = (e) => {_this._onMouseMove(e)};
    this._mouseUpHandler = (e) => {_this._onMouseUp(e)};
    this._toggleHandler = (e) => {_this._toggle(e)};
  }

  init() {
    this._insertStyle();
    this._renderBars();
  }

  _setState({
    id,
    element,
    state,
    position,
    width,
  }) {
    this.state[id] = {
      element: element,
      state: state,
      position: position,
      width: width,
    };
  }

  _updateState({
    id,
    element,
    state,
    position,
    width,
  }) {
    console.assert(id, '_updateState(): ID must be provided');
    if (!this.state[id]) { this.state[id] = {} }

    if(element) { this.state[id].element = element; }
    if(state) { this.state[id].state = state; }
    if(position) { this.state[id].position = position; }
    if(width) { this.state[id].width = width; }
  }

  _updateBar(id) {
    const bar = this.state[id].element;
    const barState = this.state[id];
    bar.style.width = barState.width + 'px';
    bar.dataset.position = barState.position;
    bar.dataset.state = barState.state;
  }

  _renderBars() {
    [...document.querySelectorAll(`[${this.barAttribute}]`)]
    .forEach((bar) => {
      const id = bar.getAttribute(this.barAttribute);

      // READ DATA FROM STORAGE
      // AND SET TO STATE:

      this._setState({
        id: id,
        element: bar,
        state: bar.dataset.state,
        position: bar.dataset.position,
        width: bar.offsetWidth,
      })

      // TODO AND UPDATE BAR WITH DATA FROM STORAGE
      // this._updateState({ id: id, width: 123 });
      // this._updateBar(id);

      // Check if there is a scrollable element
      let wrapper = bar.querySelector(`${this.barAttribute}-scroll`);
      if(wrapper) {
        console.log('wrapper is here')
      } else {
        wrapper = this._createScrollableWrapper(id);
        [ ...bar.childNodes ].forEach(child => wrapper.appendChild(child));
        bar.appendChild(wrapper);
      }

      bar.append(this._createHandler(id));
    });
  }

  _createHandler(id) {
    const handler = document.createElement('div');
    handler.setAttribute(`${this.barAttribute}-handler`, '');
    handler.dataset.content = id;
    handler.style[this.state[id].position] = 'unset'; // 'left | right'

    const border = document.createElement('div');
    border.setAttribute(`${this.barAttribute}-border`, '');
    border.dataset.content = id;
    border.title = `Resize ${id}`;
    border.addEventListener('mousedown', this._mouseDownHandler);

    const button = document.createElement('div');
    button.setAttribute(`${this.barAttribute}-button`, '');
    button.dataset.content = id;
    button.title = `Toggle ${id}`;
    button.addEventListener('mousedown', this._toggleHandler);

    handler.append(border, button);
    return handler;
  }

  _createScrollableWrapper(id, direction = 'y') {
    const wrapper = document.createElement('div');
    wrapper.setAttribute(`${this.barAttribute}-scroll`, direction);
    wrapper.dataset.content = id;
    return wrapper;
  }

  _insertStyle() {
    const style = document.createElement('style');
    // style.id = 'resizable_bar-style';
    style.setAttribute("resizable_bar-style", '');
    style.textContent = this.barStyle;
    // Add style
    document.head.append(style);
  }

  _updateCurrents(e) {
    if (e.type == "mousedown") {
      // When we start a new resize, we update the currents:
      this.activeID = e.target.dataset.content;
      this.pageX = e.pageX;
      // When we start a new resize, we take the current width of the element:
      this.state[this.activeID].width = this.state[this.activeID].element.offsetWidth;
    } else {
      // e.type == "mouseup"
      // At the end of the resize:
      this.activeID = null;
      this.pageX = null;
      // We leave the last adjusted width,
      // * this.state[this.activeID].width
      // and if the panel is opened/closed with a button,
      // this adjusted width will be used.
    }
  }

  _onMouseDown(e) {
    // Init resizing
    if(e.button == 0) {
      e.preventDefault();
      this._updateCurrents(e);
      window.addEventListener('mousemove', this._mouseMoveHandler);
      window.addEventListener('mouseup', this._mouseUpHandler);
    }
  }

  _toggle(e) {
    if(e.button == 0) {
      const id = e.target.dataset.content;
      this.state[id].state = this.state[id].state === 'open'
        ? 'closed'
        : 'open';
      this._updateBar(id);
    }
  }

  _open(id) {
    this.state[id].state = 'open';
    this._updateBar(id);
  }

  _close(id) {
    this.state[id].state = 'closed';
    this._updateBar(id);
  }

  _onMouseMove(e) {
    // Resizing
    requestAnimationFrame(() => {
      if(this.activeID) {
        const delta = e.pageX - this.pageX;
        const w = this.state[this.activeID].width + delta;

        this.state[this.activeID].element.style.width = w + 'px';

        if(w < this.barGravity) {
          if(this.state[this.activeID].state == 'open') {
            this._close(this.activeID);
          }
        } else {
          if(this.state[this.activeID].state == 'closed') {
            this._open(this.activeID);
          }
        }

      }
    })
  }

  _onMouseUp(e) {
    // Clean up after work
    window.removeEventListener('mousemove', this._mouseMoveHandler);
    window.removeEventListener('mouseup', this._mouseUpHandler);

    const currentWidth = this.state[this.activeID].element.offsetWidth;
    this._updateState({ id: this.activeID, width: currentWidth });
    this._updateBar(this.activeID);
    this._updateCurrents(e);

    // WRITE DATA TO STORAGE!
  }
}

const resizableBar = new ResizableBar({
  barAttribute: BAR_ATTRIBUTE,
  barStyle: STYLE,
  barGravity: BAR_MIN_WIDTH,
});

window.addEventListener("load", function () {
  resizableBar.init();
});
