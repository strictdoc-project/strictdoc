// from GRAPH-NESTOR; disable fit on start

class Styles {
  constructor(text) {
    this.text = text;
  }

  add(text) {
    const headElement = document.querySelector('head');
    const bodyElement = document.body;

    if (!headElement && !bodyElement) {
      console.error('Check the structure of your document. We didn`t find HEAD and BODY tags. HTML2PDF4DOC expects valid HTML.');
      return
    };

    const styleElement = document.createElement('style');
    styleElement.setAttribute("graph-nestor-styles", "css");
    styleElement.innerHTML = text || this.text;

    if (headElement) {
      headElement.append(styleElement);
    } else if (bodyElement) {
      bodyElement.before(styleElement);
    } else {
      console.assert(false, 'We expected to find the HEAD and BODY tags.');
    }
  }
}

class Preloader {
  constructor({
    // optional:
    background,
    color,
    preloaderClass,
    fadeTime,
  } = {}) {
    this._preloader;
    this._preloaderFadeTime = fadeTime || 50;
    this._preloaderContainer;
    this._contentContainer;

    this._background = background || 'transparent';
    this._color = color || 'orangered';
    this._preloaderClass = preloaderClass || 'lds-dual-ring';
    this._css = `
    /* PRELOADER */
    .${this._preloaderClass} {
      position: absolute;
      z-index: 99999;
      top: 0; left: 0; bottom: 0; right: 0;
      display: flex;
      justify-content: center;
      align-items: center;
      background: ${this._background};
    }
    .${this._preloaderClass}:after {
      content: " ";
      display: block;
      width: 64px;
      height: 64px;
      margin: 8px;
      border-radius: 50%;
      border: 6px solid ${this._color};
      border-color: ${this._color} ${this._background} ${this._color} ${this._background};
      animation: ${this._preloaderClass} 1.2s linear infinite;
    }
    @keyframes ${this._preloaderClass} {
      0% {
        transform: rotate(0deg);
      }
      100% {
        transform: rotate(360deg);
      }
    }
    `;
  }

  add({
    preloaderContainer,
    contentContainer,
  }) {
    new Styles(this._css).add();
    this._preloaderContainer = preloaderContainer;
    this._contentContainer = contentContainer;

    this._create();
    this._contentContainer.style.opacity = 0;

  }

  remove() {
    if (!this._preloader) { return }

    let _opacity = 1;  // initial opacity

    const fadeTimer = setInterval(() => {
        if (_opacity <= 0.1){
            clearInterval(fadeTimer);
            this._preloader.remove();
            this._contentContainer.style.opacity = 1; // ''
        }

        this._preloader.style.opacity = _opacity;
        this._contentContainer.style.opacity = 1 - _opacity;
        _opacity -= _opacity * 0.1;
    }, this._preloaderFadeTime);
  }

  _create() {
    this._preloader = document.createElement('div');
    this._preloader.classList.add('nestor-preloader');
    this._preloader.innerHTML = `<div class="${this._preloaderClass}"></div>`;
    this._preloaderContainer.append(this._preloader);
  }
}

class Canvas {
  constructor({
    content,
    initScale,
    minScale,
    maxScale,
    initSpeed,
  }) {
    this._canvas;
    this._container;
    this._content = content;

    this._listeners = {};

    this._css = `
    html, body {
      min-height: 100vh;
      min-width: 100vw;
      height: 100vh;
      width: 100vw;
    }
    .nestor-canvas {
      box-sizing: border-box;
      height: 100%;
      width: 100%;
      max-height: 100vh;
      max-width: 100vw;
      overflow: hidden;
      position: relative;
    }
    .nestor-preloader {
      position: absolute;
      left: 0;
      top: 0;
      bottom: 0;
      right: 0;
      pointer-events: none;
      z-index: 10;
    }
    .nestor-container {
      position: absolute;
      left: 0;
      top: 0;
      transform-origin: 0 0;
      pointer-events: none;
    }
    .nestor-container > * {
      pointer-events: all;
    }
    .nestor-control {
      position: absolute;
      right: 10px;
      top: 10px;
      pointer-events: all;
    }
    .nestor-control-button {
      width: 20px;
      height: 20px;
      background: red;
    }
    `;
    this._scale = initScale || 1;
    this._scaleMin = minScale || 0.25;
    this._scaleMax = maxScale || 1;
    this._speed = initSpeed || 0.001;
    this._x = 0;
    this._y = 0;
    this._isSpacePressed = false;
    this._mouseDown = false;
    this._isCtrlPressed = false;
    this._isShiftPressed = false;

    this._style = new Styles(this._css);
    this._preloader = new Preloader({
      fadeTime: 20
    });

    this._init();
  }

  get scale() {
    return this._scale;
  }

  addEventListener(type, listener) {
    // Method for adding a listener
    if (!this._listeners[type]) {
      this._listeners[type] = [];
    }
    this._listeners[type].push(listener);
  }

  _init() {
    this._style.add();
    this._createCanvas();
    // this.addPreloader(); // TODO

    // Event handlers initialization
    this._initEventListeners();
    // Fit content in container at 0:0
    // this._fitContent(); // TODO
  }

  _createCanvas() {

    this._canvas = document.createElement('div');
    this._canvas.classList.add('nestor-canvas');

    this._container = document.createElement('div');
    this._container.classList.add('nestor-container');

    this._content.before(this._canvas);
    this._canvas.append(this._container);
    this._container.append(this._content);

    // TODO
    // const controlContainer = document.createElement('div');
    // controlContainer.classList.add('nestor-control');
    // const controlButton = document.createElement('button');
    // controlButton.classList.add('nestor-control-button');
    // this._canvas.append(controlContainer);
    // controlContainer.append(controlButton);
  }

  addPreloader() {
    this._preloader.add({
      preloaderContainer: this._canvas,
      contentContainer: this._container,
    });
  }

  removePreloader() {
    this._preloader.remove();
  }

  _fitContent(x = 0, y = 0) {
    this._x = x;
    this._y = y;

    const scaleX = this._canvas.offsetWidth / this._container.offsetWidth || 1;
    const scaleY = this._canvas.offsetHeight / this._container.offsetHeight || 1;

    // The optimal scaling factor is the smaller of the two,
    // so that the content fits into the container without distorting its proportions
    this._scale = Math.min(scaleX, scaleY);
    this._scale = (this._scale > 1) ? 1 : this._scale;
    this._updateTransform();
  }

  _initEventListeners() {
    // Scaling and vertical/horizontal scrolling
    this._canvas.addEventListener('wheel', this._handleWheel.bind(this));

    // Free moving
    this._canvas.addEventListener('mousedown', this._handleMouseDown.bind(this));
    this._canvas.addEventListener('mouseup', this._handleMouseUp.bind(this));
    this._canvas.addEventListener('mouseleave', this._handleMouseLeave.bind(this));

    // Keys
    document.addEventListener('keydown', this._handleKeyDown.bind(this));
    document.addEventListener('keyup', this._handleKeyUp.bind(this));
  }

  _handleWheel(e) {
    e.preventDefault();

    if (this._isCtrlPressed) {
      // Scaling with mouse wheel while pressing the Ctrl/Command key
      const rect = this._container.getBoundingClientRect();
      const mouseX = (e.clientX - rect.left);
      const mouseY = (e.clientY - rect.top);
      const oldScale = this._scale;

      this._scale += e.deltaY * (-1) * this._speed;
      this._scale = Math.min(Math.max(this._scaleMin, this._scale), this._scaleMax);

      this._x -= (mouseX / oldScale) * (this._scale - oldScale);
      this._y -= (mouseY / oldScale) * (this._scale - oldScale);
    } else if (this._isShiftPressed) {
      // Horizontal moving with mouse wheel while pressing the Shift key
      this._x += e.deltaX || e.deltaY; // Add deltaX check, use deltaY as a backup
    } else {
      // Vertical moving without keys (with mouse wheel only)
      this._y -= e.deltaY;
    }

    this._updateTransform();
  }

  _handleMouseDown(e) {
    if (this._isSpacePressed) {
      e.preventDefault();
      this._mouseDown = true;
      this.startX = e.clientX - this._x;
      this.startY = e.clientY - this._y;
      this._canvas.style.cursor = 'grabbing';
      this._canvas.addEventListener('mousemove', this._handleMouseMove.bind(this));
    }
  }

  _handleMouseMove(e) {
    if (this._mouseDown) {
      this._x = e.clientX - this.startX;
      this._y = e.clientY - this.startY;
      this._updateTransform();
    }
  }

  _handleMouseUp() {
    if (this._mouseDown) {
      this._mouseDown = false;
      this._canvas.style.cursor = 'grab';
      this._canvas.removeEventListener('mousemove', this._handleMouseMove);
    }
  }

  _handleMouseLeave() {
    if (this._mouseDown) {
      this._mouseDown = false;
      this._canvas.style.cursor = 'grab';
      this._canvas.removeEventListener('mousemove', this._handleMouseMove);
    }
  }

  _handleKeyDown(e) {
    if (e.code === 'Space' && !this._isSpacePressed) {
      this._isSpacePressed = true;
      this._canvas.style.cursor = 'grab';
    }
    if (e.key === 'Control' || e.key === 'Meta') {
      this._isCtrlPressed = true;
    }
    if (e.key === 'Shift') {
      this._isShiftPressed = true;
    }
  }

  _handleKeyUp(e) {
    if (e.code === 'Space') {
      this._isSpacePressed = false;
      this._canvas.style.cursor = 'default';
    }
    if (e.key === 'Control' || e.key === 'Meta') {
      this._isCtrlPressed = false;
    }
    if (e.key === 'Shift') {
      this._isShiftPressed = false;
    }
  }

  _updateTransform() {
    this._container.style.transform = `translate(${this._x}px, ${this._y}px) scale(${this._scale})`;
    this._dispatchEvent('scaleChange', this._scale); // Notify listeners of the change in scale
  }

  _dispatchEvent(type, data) {
    // Method for notifying listeners
    if (this._listeners[type]) {
      this._listeners[type].forEach(listener => listener(data));
    }
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const canvas = new Canvas({
    content: document.querySelector('.main'),
    initScale: 1
  });
});
