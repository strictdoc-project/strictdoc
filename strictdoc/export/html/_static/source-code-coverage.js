

const __log = (topic, ...payload) => {
  console.log(`%c ${topic} `, 'background:yellow;color:black',
    ...payload
  );
}

class Highlighter {
  constructor({
    target,
    rgb,
    alpha,
  }) {
    this.target = target || document.body;
    this.rgb = rgb || '75,255,0';
    this.alpha = alpha || '0.2';
  }

  create(top = 0, height = 0) {
    const element = document.createElement('div');
    this._addBaseStyle(element);
    this.target.prepend(element);
    this.move(element, top, height);
    this.on(element);
    return element
  }

  off(element) {
    this._colorize(element, this.rgb, 0)
  }

  on(element) {
    this._colorize(element)
  }

  toggleVisibility(element, toggler) {
    if (toggler) {
      this.on(element)
    } else {
      this.off(element)
    }
  }

  move(element, top, height) {
    element.style.top = top + 'px';
    element.style.height = height + 'px';
  }

  _colorize(element, rgb, alpha = 1) {
    element.style.background = rgb ? `rgba(${rgb}, ${alpha})` : `rgba(${this.rgb}, ${this.alpha})`;
  }

  _addBaseStyle(element) {
    element.style.position = 'absolute';
    element.style.zIndex = '-1';
    element.style.left = '0';
    element.style.right = '0';
    element.style.transition = 'height 0.3s ease-in, top 0.3s ease-in, background 0.15s ease-in';
  }
}

class Switch {
  constructor({
    callback,
    labelText,
    checked,
    componentClass,
    colorOn,
    colorOff,
    size,
    stroke,
    units,
  }) {
    this.colorOn = colorOn || 'rgb(100, 200, 50)';
    this.colorOff = colorOff || 'rgb(200, 200, 200)';
    this.labelText = labelText || '';
    this.checked = checked || true;

    this.componentClass = componentClass || 'std-switch-scc';
    this.size = size || 0.75;
    this.stroke = stroke || 0.25;
    this.units = units || 'rem';

    this.callback = callback;
  }

  create() {
    const block = document.createElement('div');
    block.classList.add(this.componentClass);
    const label = document.createElement('label');
    label.classList.add(`${this.componentClass}__label`);
    const input = document.createElement('input');
    input.classList.add(`${this.componentClass}__input`);
    input.type = 'checkbox';
    input.checked = this.checked;
    const slider = document.createElement('span');
    slider.classList.add(`${this.componentClass}__slider`);
    const text = document.createElement('span');
    text.innerHTML = this.labelText;

    input.addEventListener('change', () => this.callback(input.checked));

    label.append(input, slider, text);
    block.append(label);
    this.insertStyle();

    return block;
  }

  insertStyle() {

    const css = `
    .${this.componentClass} {
      display: inline-block;
      line-height: 0;
    }
    .${this.componentClass}__label {
      display: inline-flex;
      line-height: ${this.size}${this.units};
      align-items: center;
      justify-content: flex-start;
      user-select: none;
      cursor: pointer;
    }
    .${this.componentClass}__input {
      opacity: 0;
      width: 0;
      height: 0;
      position: absolute;
    }
    .${this.componentClass}__slider {
      position: relative;
      cursor: pointer;
      background-color: ${this.colorOff};
      -webkit-transition: .4s;
      transition: .4s;
      display: inline-block;
      width: ${this.size * 2 + this.stroke * 2}${this.units};
      height: ${this.size + this.stroke * 2}${this.units};
      margin-right: ${this.size * 0.5}${this.units};
      border-radius: ${this.size * 0.5 + this.stroke}${this.units};
    }
    .${this.componentClass}__slider::before  {
      position: absolute;
      content: "";
      height: ${this.size}${this.units};
      width: ${this.size}${this.units};
      left: ${this.stroke}${this.units};
      bottom: ${this.stroke}${this.units};
      background-color: white;
      -webkit-transition: .4s;
      transition: .4s;
      border-radius: 50%;
    }
    input:checked + .${this.componentClass}__slider {
      background-color: ${this.colorOn};
    }
    input:focus + .${this.componentClass}__slider {
      box-shadow: 0 0 1px ${this.colorOn};
    }
    input:checked + .${this.componentClass}__slider::before {
      -webkit-transform: translateX(${this.size}${this.units});
      -ms-transform: translateX(${this.size}${this.units});
      transform: translateX(${this.size}${this.units});
    }
    `;

    const head = document.querySelector('head');
    const style = document.createElement('style');
    style.append(document.createTextNode(css));
    style.setAttribute("data-slider-styles", '');
    head.append(style);
  }

}

class Dom {
  constructor({
    sourceId,
    hashSplitter,
    strictdocCommentSelector,
    strictdocCommentBeginString,
    strictdocCommentEndString,
  }) {

    // CONSTANTS
    this.sourceId = sourceId || 'source';
    this.hashSplitter = hashSplitter || '#';

    // STRICTDOC SPECIFIC
    this.strictdocCommentSelector = strictdocCommentSelector || 'pre span';
    this.strictdocCommentBeginString = strictdocCommentBeginString || '# STRICTDOC RANGE BEGIN: ';
    this.strictdocCommentEndString = strictdocCommentEndString || '# STRICTDOC RANGE END: ';

    // objects
    this.greenHighlighter;
    this.yellowHighlighter;

    // elements
    this.sourceContainer;
    this.source;
    this.lines = {};
    this.requirements = {};
    this.ranges = {};
    this.highlightedRange;

    // state
    this.active = {
      range: null,
      requirement: null,
      pointers: [],
    };
  }

  prepare() {

    this.sourceContainer = document.getElementById('sourceContainer');

    this.sourceContainer.style.position = 'absolute';
    this.sourceContainer.style.top = 0;
    this.sourceContainer.style.bottom = 0;
    this.sourceContainer.style.right = 0;
    this.sourceContainer.style.left = 0;
    this.sourceContainer.style.overflow = 'auto';

    console.log(this.sourceContainer);

    this._prepareSourceBlock();

    this.yellowHighlighter = new Highlighter({
      target: this.source,
      rgb: '255,255,155',
      alpha: '1',
    });
    this.highlightedRange = this.yellowHighlighter.create();

    this.greenHighlighter = new Highlighter({
      target: this.source,
      rgb: '75,255,0',
      alpha: '0.2',
    });

    this._prepareLines();
    this._prepareRequirements();
    this._prepareRanges();

  }

  useLocationHash() {
    const [_, reqId, rangeBegin, rangeEnd] = window.location.hash.split(this.hashSplitter);
    const rangeAlliace = rangeBegin ? this._generateRangeAlias(rangeBegin, rangeEnd) : undefined;

    this.changeActive({
      requirement: this.requirements[reqId],
      pointers: rangeAlliace ? this.ranges[rangeAlliace].pointers : null,
      range: rangeAlliace ? this.ranges[rangeAlliace].highlighter : null,
    });

    this.highlightRange(this.active.range);
  }

  changeActive = ({
    range,
    requirement,
    pointers,
  }) => {

    // remove old 'active'
    this.active.requirement?.classList.remove('active');
    this.active.pointers?.forEach(pointer => pointer?.classList.remove('active'));

    // make changes to state
    this.active.range = range;
    this.active.requirement = requirement;
    this.active.pointers = pointers;

    // add new 'active'
    this.active.requirement?.classList.add('active');
    this.active.pointers?.forEach(pointer => pointer.classList.add('active'));

  };

  toggleRangesVisibility(toggler) {
    for (let key in this.ranges) {
      this.greenHighlighter.toggleVisibility(this.ranges[key].highlighter, toggler)
    }
  }

  highlightRange(range) {
    const top = range?.offsetTop || 0;
    const height = range?.offsetHeight || 0;
    this.yellowHighlighter.move(this.highlightedRange, top, height);

    if (range) {
      // range.scrollIntoView({ block: "center", inline: "nearest", behavior: "smooth" });
      this.sourceContainer.scrollTo({
        top: top - 200, // TODO 200 to config
        behavior: 'smooth',
      });
    } else {
      // this.source.scrollIntoView({ block: "start", inline: "nearest", behavior: "smooth" });
      this.sourceContainer.scrollTo({
        top: 0,
        behavior: 'smooth',
      });
    }
  }

  _prepareSourceBlock() {
    this.source = document.getElementById(this.sourceId);
    this.source.style.position = 'relative';
    this.source.style.zIndex = '1';
  }

  _prepareLines() {
    this.lines = [...document.querySelectorAll('[data-line]')]
      .reduce((acc, line) => {
        acc[line.dataset.line] = line;
        return acc
      }, {});
  }

  _prepareRequirements() {
    this.requirements = [...document.querySelectorAll('.requirement')]
      .reduce((acc, requirement) => {
        acc[requirement.dataset.reqid] = requirement;
        return acc
      }, {});
  }

  _prepareRanges() {
    const ranges = this.ranges;

    [...document.querySelectorAll('.pointer')]
      .map(pointer => {
        const rangeBegin = pointer.dataset.begin;
        const rangeEnd = pointer.dataset.end;

        const range = this._generateRangeAlias(rangeBegin, rangeEnd);

        if (!ranges[range]) {
          ranges[range] = {};
          ranges[range].pointers = [];

          ranges[range].beginLine = this.lines[rangeBegin];
          ranges[range].endLine = this.lines[rangeEnd];

          const top = ranges[range].beginLine.offsetTop;
          const height = ranges[range].endLine.offsetTop + ranges[range].endLine.offsetHeight - top;
          ranges[range].highlighter = this.greenHighlighter.create(top, height);
        }

        ranges[range].pointers.push(pointer);
      });

    // put pointers from code to this.ranges
    this._prepareInlinePointers();
  }

  _prepareInlinePointers() {
    for (var range in this.ranges) {

      const beginLine = this.ranges[range].beginLine
        .querySelector(this.strictdocCommentSelector);
      const endLine = this.ranges[range].endLine
        .querySelector(this.strictdocCommentSelector);

      this._processLine(
        range,
        beginLine,
        this.strictdocCommentBeginString
      );
      this._processLine(
        range,
        endLine,
        this.strictdocCommentEndString
      );
    }
  }

  _processLine(range, element, string) {

    // Assume that the requirments ID in the code and the links in the menu are correct and the same
    const newHTML = this.ranges[range].pointers
      .map(pointer => `<a href="${pointer.href}">${pointer.dataset.reqid}</a>`)
      .join(', ');
    element.innerHTML = string + newHTML;
  }

  _generateRangeAlias(begin, end) { return `${begin}${this.hashSplitter}${end}` };
}

const dom = new Dom({
  sourceId: 'source',
  hashSplitter: '#',
  strictdocCommentSelector: 'pre span',
  strictdocCommentBeginString: '# STRICTDOC RANGE BEGIN: ',
  strictdocCommentEndString: '# STRICTDOC RANGE END: ',
});

window.addEventListener("load", function () {
  __log(
    'start',
    window.location.hash
  )

  dom.prepare();
  dom.useLocationHash();

  const switcher = new Switch(
    {
      labelText: 'Coverage',
      checked: true,
      callback: (checked) => dom.toggleRangesVisibility(checked),
    }
  );
  document.getElementById('sorceCodeCoverageSwitch').append(switcher.create());

});

window.addEventListener("hashchange", () => dom.useLocationHash());
