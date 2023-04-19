
const __log = (topic, ...payload) => {
  console.log(`%c ${topic} `, 'background:yellow;color:black',
    ...payload
  );
}

__log('start', 'i am here, resizable!');

// Expected:
// js-resizable-bar="tree"
// data-state="open"
// data-position="left"

const BAR_ATTRIBUTE = 'js-resizable-bar';
const BAR_MIN_WIDTH = 100;
const BAR_CLOSED_WIDTH = 32;
const BAR_MAX_VW = '25vw';

const BAR_HANDLER_WIDTH = 18;

const BAR_COLOR_MAIN = 'var(--color-fg-main, Black)';
const BAR_COLOR_BACKGROUND = 'var(--color-bg-main, White)';
const BAR_COLOR_ACTIVE = 'var(--color-fg-accent, currentColor)';
const BAR_COLOR_BORDER = 'var(--color-border, rgba(0,0,0,0.1))';

const STYLE = `
[${BAR_ATTRIBUTE}] {
  position: relative;
  height: 100%;
  overflow: hidden;
  width: fit-content;
  max-width: ${BAR_MAX_VW};
}

[${BAR_ATTRIBUTE}][data-state="open"] {
  min-width: ${BAR_MIN_WIDTH}px;
  pointer-events: auto;
}
[${BAR_ATTRIBUTE}][data-state="closed"] {
  max-width: ${BAR_CLOSED_WIDTH}px;
  pointer-events: none;
}

[${BAR_ATTRIBUTE}][data-position="left"] {
  border-left: none;
  padding-right: ${BAR_HANDLER_WIDTH * 0.5}px;
}
[${BAR_ATTRIBUTE}][data-position="right"] {
  border-right: none;
  padding-left: ${BAR_HANDLER_WIDTH  * 0.5}px;
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
  /* background: ${BAR_COLOR_BACKGROUND}; */
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
  left: calc(50%);
  width: 1px;
  background: ${BAR_COLOR_BORDER};
  transition: .3s;
}

[${BAR_ATTRIBUTE}-border]::after {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  left: calc(50% - 2px);
  width: 4px;
  background: transparent;
  transition: .3s;
}

[${BAR_ATTRIBUTE}-border]:hover::after {
  background: ${BAR_COLOR_ACTIVE};
}

[${BAR_ATTRIBUTE}-button] {
  cursor: pointer;
  position: absolute;
  z-index: 2;
  left: 0;
  top: ${BAR_HANDLER_WIDTH * 0.88}px;
  box-sizing: border-box;
  width: ${BAR_HANDLER_WIDTH}px;
  height: ${BAR_HANDLER_WIDTH}px;
  font-size: ${BAR_HANDLER_WIDTH * 0.77}px;
  font-weight: bold;
  border-radius: 50%;
  border-width: 1px;
  border-style: solid;
  border-color: ${BAR_COLOR_BACKGROUND};
  background: ${BAR_COLOR_BACKGROUND};
  color: ${BAR_COLOR_ACTIVE};
  transition: .3s;
}

[${BAR_ATTRIBUTE}-button]::after {
  content: '❮';   /* ❮❯ */
  position: absolute;
  display: flex;
  align-items: center;
  justify-content: center;
  left: ${-0.5 * BAR_HANDLER_WIDTH}px;
  right: ${-0.5 * BAR_HANDLER_WIDTH}px;
  top: ${-0.5 * BAR_HANDLER_WIDTH}px;
  bottom: ${-0.5 * BAR_HANDLER_WIDTH}px;
}

[${BAR_ATTRIBUTE}-button]:hover {
  color: ${BAR_COLOR_MAIN};
  border-color: ${BAR_COLOR_MAIN};
}

[${BAR_ATTRIBUTE}][data-state="open"] [${BAR_ATTRIBUTE}-button]::after {
  content: '❮';
}
[${BAR_ATTRIBUTE}][data-state="closed"] [${BAR_ATTRIBUTE}-button]::after {
  content: '❯';
}
`;

class ResizableBar {
  constructor({
    barAttribute,
    barStyle,
    barGravity,
  }) {
    this.barAttribute = barAttribute || 'js-resizable-bar';
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

    console.info(this.state)
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

    console.info(this.state)
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

      bar.append(this._createHandler(id));
    });
  }

  _createHandler(id) {
    const handler = document.createElement('div');
    handler.setAttribute(`${this.barAttribute}-handler`, '');
    handler.dataset.parent = id;
    handler.style[this.state[id].position] = 'unset'; // 'left | right'

    const border = document.createElement('div');
    border.setAttribute(`${this.barAttribute}-border`, '');
    border.dataset.parent = id;
    border.title = `Resize ${id}`;
    border.addEventListener('mousedown', this._mouseDownHandler);

    const button = document.createElement('div');
    button.setAttribute(`${this.barAttribute}-button`, '');
    button.dataset.parent = id;
    button.title = `Toggle ${id}`;
    button.addEventListener('mousedown', this._toggleHandler);

    handler.append(border, button);
    __log('create', '');
    return handler;
  }

  _insertStyle() {
    const style = document.createElement('style');
    // style.id = 'resizable-bar-style';
    style.setAttribute("resizable-bar-style", '');
    style.textContent = this.barStyle;
    // Add style
    document.head.append(style);
  }

  _updateCurrents(e) {
    if (e.type == "mousedown") {
      __log('down', this.activeID);
      // When we start a new resize, we update the currents:
      this.activeID = e.target.dataset.parent;
      this.pageX = e.pageX;
      __log('down', this.activeID);
    } else {
      __log('up', this.activeID);
      // e.type == "mouseup"
      // At the end of the resize:
      this.activeID = null;
      this.x = null;
      __log('up', this.activeID);
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
      const id = e.target.dataset.parent;
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
