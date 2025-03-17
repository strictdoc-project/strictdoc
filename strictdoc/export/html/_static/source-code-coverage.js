

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
    alignRight,
  }) {
    this.colorOn = colorOn || 'rgb(100, 200, 50)';
    this.colorOff = colorOff || 'rgb(200, 200, 200)';
    this.labelText = labelText || '';
    this.checked = checked || true;

    this.componentClass = componentClass || 'std-switch-scc';
    this.size = size || 0.75;
    this.stroke = stroke || 0.25;
    this.units = units || 'rem';
    this.alignRight = alignRight || true;

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
      gap: ${this.size * 0.5}${this.units};
      font-size: ${this.size * 1.5}${this.units}; /* 0.75rem; */
      line-height: ${this.size}${this.units};
      align-items: center;
      justify-content: flex-start;
      user-select: none;
      cursor: pointer;
      flex-direction: ${this.alignRight ? "row-reverse" : "row"};
      text-align: ${this.alignRight ? "right" : "left"};
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
    sourceContainerId,
    referContainerId,
    hashSplitter,
    strictdocPointerSelector,
    strictdocRequirementSelector,
    strictdocLineNumberSelector,
    strictdocLineRangeSelector,
    strictdocSourceFilterClass,
    filteredClass,
    activeClass,
  }) {

    // CONSTANTS
    this.sourceId = sourceId || 'source';
    this.sourceContainerId = sourceContainerId || 'sourceContainer';
    this.referContainerId = referContainerId || 'referContainer';
    this.hashSplitter = hashSplitter || '#';

    // STRICTDOC SPECIFIC
    this.strictdocPointerSelector = strictdocPointerSelector || '.pointer';
    this.strictdocRequirementSelector = strictdocRequirementSelector || '.source-file__requirement';
    this.strictdocLineNumberSelector = strictdocLineNumberSelector || '.source__line-number';
    this.strictdocLineRangeSelector = strictdocLineRangeSelector || '.source__line-ranges';
    this.strictdocSourceFilterClass = strictdocSourceFilterClass || 'source__filter';
    this.filteredClass = filteredClass || 'filtered';
    this.activeClass = activeClass || 'active';

    // objects
    this.greenHighlighter;
    this.yellowHighlighter;

    // elements
    this.filterContainer;
    this.sourceContainer;
    this.referContainer;
    this.source;
    this.lines = {};
    this.requirements = {};
    this.ranges = {};
    this.highlightingElement; // yellow

    // state
    this.active = {
      range: null,
      requirement: null,
      pointers: [],
      // labels: [],
      filter: null,
    };
  }

  prepare() {

    this._prepareFilterContainer();
    this._prepareSourceContainer();
    this._prepareReferContainer();
    this._prepareSource();

    this.yellowHighlighter = new Highlighter({
      target: this.source,
      rgb: '255,255,155',
      alpha: '1',
    });
    this.highlightingElement = this.yellowHighlighter.create();

    this.greenHighlighter = new Highlighter({
      target: this.source,
      rgb: '75,255,0',
      alpha: '0.2',
    });

    this._prepareLines();
    this._prepareRequirements();
    this._prepareRanges();
    this._updateLinesWithRanges();

    console.log('this.lines', this.lines);
    console.log('this.requirements', this.requirements);
    console.log('this.ranges', this.ranges);
    console.log('this.active', this.active);
  }

  useLocationHash() {
    const [_, reqId, rangeBegin, rangeEnd] = window.location.hash.split(this.hashSplitter);
    const rangeAlias = rangeBegin ? this._generateRangeAlias(rangeBegin, rangeEnd) : undefined;

    this.changeActive({
      requirement: this.requirements[reqId],
      pointers: rangeAlias ? this.ranges[rangeAlias].pointers : null,
      range: rangeAlias ? this.ranges[rangeAlias].highlighter : null,
      // labels: (reqId && rangeAlias) ? this.ranges[rangeAlias][reqId] : null,
    });

    this.highlightRange(this.active.range);
  }

  changeActive = ({
    range,
    requirement,
    pointers,
    // labels,
  }) => {

    // remove old 'active'
    this.active.requirement?.classList.remove(this.activeClass);
    this.active.pointers?.forEach(pointer => pointer?.classList.remove(this.activeClass));
    // this.active.labels?.forEach(label => label?.classList.remove(this.activeClass));

    // make changes to state
    this.active.range = range;
    this.active.requirement = requirement;
    this.active.pointers = pointers;
    // this.active.labels = labels;

    // add new 'active'
    this.active.requirement?.classList.add(this.activeClass);
    this.active.pointers?.forEach(pointer => pointer.classList.add(this.activeClass));
    // this.active.labels?.forEach(label => label.classList.add(this.activeClass));

  };

  toggleRangesVisibility(toggler) {
    for (let key in this.ranges) {
      this.greenHighlighter.toggleVisibility(this.ranges[key].highlighter, toggler)
    }
  }

  highlightRange(range) {
    const top = range?.offsetTop || 0;
    const height = range?.offsetHeight || 0;
    this.yellowHighlighter.move(this.highlightingElement, top, height);

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

  _prepareSource() {
    this.source = document.getElementById(this.sourceId);
    this.source.style.position = 'relative';
    this.source.style.zIndex = '1';
  }

  _prepareSourceContainer() {
    this.sourceContainer = document.getElementById('sourceContainer');
  }

  _prepareReferContainer() {
    this.referContainer = document.getElementById('referContainer');
  }

  _prepareFilterContainer() {
    this.filterContainer = document.getElementById('sourceCodeCoverageFilter');
  }

  _prepareLines() {
    // Both .source__line-content and .source__line-number
    // have data-line={{ loop.index }}
    this.lines = [...document.querySelectorAll(this.strictdocLineNumberSelector)]
      .reduce((acc, line) => {
        acc[line.dataset.line] = {
          line: line,
          ranges: []
        };
        return acc
      }, {});
  }

  _prepareRequirements() {
    this.requirements = [...document.querySelectorAll(this.strictdocRequirementSelector)]
      .reduce((acc, requirement) => {
        acc[requirement.dataset.reqid] = requirement;
        return acc
      }, {});
  }

  _prepareRanges() {
    const ranges = this.ranges;

    [...document.querySelectorAll(this.strictdocPointerSelector)]
      .map(pointer => {
        const thisFileOrOther = pointer.dataset.traceabilityFileType;
        console.assert(!!thisFileOrOther, "The file type shall be specified.", pointer);
        if (thisFileOrOther !== "this_file") {
          return;
        }

        const rangeBegin = pointer.dataset.begin;
        const rangeEnd = pointer.dataset.end;
        const rangeReq = pointer.dataset.reqid;

        const range = this._generateRangeAlias(rangeBegin, rangeEnd);

        if (!ranges[range]) {
          // add new range
          ranges[range] = {};
          ranges[range].pointers = [];

          ranges[range].beginLine = this.lines[rangeBegin].line;
          ranges[range].endLine = this.lines[rangeEnd].line;
          ranges[range].begin = rangeBegin;
          ranges[range].end = rangeEnd;

          const top = ranges[range].beginLine.offsetTop;
          const height = ranges[range].endLine.offsetTop + ranges[range].endLine.offsetHeight - top;
          ranges[range].highlighter = this.greenHighlighter.create(top, height);
        }

        if (rangeReq) {
          // add pointer from code
          (ranges[range][rangeReq] ??= []).push(pointer);
        } else {
          // add pointer from menu
          ranges[range].pointers.push(pointer);
        }

        // const start = parseInt(rangeBegin, 10);
        // const end = parseInt(rangeEnd, 10);

        // for (let i = start; i <= end; i++) {
        //   (this.lines[i].ranges ??= []).push(range);
        //   console.assert(this.lines[i].line, `The line ${i} must be registered.`)
        //   this.lines[i].line?.classList.add(this.strictdocSourceFilterClass);
        // }

      });
  }

  _updateLinesWithRanges() {
    Object.entries(this.ranges).forEach(([key, value]) => {
      // console.log(value);

      const begin = parseInt(value.begin, 10);
      const end = parseInt(value.end, 10);

      for (let i = begin; i <= end; i++) {
        (this.lines[i].ranges ??= []).push(key);
        (this.lines[i].pointers ??= []).push(...value.pointers);

        const currentLine = this.lines[i].line;
        console.assert(this.lines[i].line, `The line ${i} must be registered.`);
        currentLine.classList.add(this.strictdocSourceFilterClass);
      }

      const rangeNumContainer = this.lines[begin].line.querySelector(this.strictdocLineRangeSelector);
      rangeNumContainer.innerHTML = this.lines[begin].pointers.length;
    });
  }

  _generateRangeAlias(begin, end) { return `${begin}${this.hashSplitter}${end}` };

  _createFilterInfoBlock(lineNumber) {
    const block = document.createElement('div');
    block.innerHTML = `
    The requirements related to&nbsp;the&nbsp;line&nbsp;<mark>${lineNumber}</mark>
    are&nbsp;shown. <a href="" class="strictdoc__link">Reset&nbsp;filter</a>`;

    const link = block.querySelector(".strictdoc__link");
    link.addEventListener("click", (event) => {
        event.preventDefault();
        this.removeActiveFilter();
        this.resetFilters();
    });

    return block;
  }

  filterRequirements(event) {
    const filterButton = event.target.closest(`.${this.strictdocSourceFilterClass}`);
    if (!filterButton) return;
    const clickedLineNumber = parseInt(filterButton.dataset.line, 10);
    console.log(`Clicked line:`, clickedLineNumber);

    const currentActiveLineNumber = parseInt(this.active.filter);

    this.active.filter && this.removeActiveFilter();
    this.active.filter && this.resetFilters();
    if(currentActiveLineNumber !== clickedLineNumber) {
      this.setFilter(clickedLineNumber);
    }

  }

  removeActiveFilter() {
    console.log('remove', this.active.filter);
    this.lines[parseInt(this.active.filter)].line.classList.remove(this.activeClass);
  }

  resetFilters() {
    console.log('reset filter');
    this.active.filter = null;
    this.filterContainer.innerHTML = '';

    // todo reset filtered requirements
    this.referContainer.classList.remove(this.filteredClass);
  }

  setFilter(clickedLineNumber) {
    this.lines[clickedLineNumber].line.classList.add(this.activeClass);
    this.active.filter = clickedLineNumber;
    this.filterContainer.append(this._createFilterInfoBlock(clickedLineNumber));

    // todo filter requirements
    this.referContainer.classList.add(this.filteredClass);
  }
}

const dom = new Dom({
  // sourceId: 'source',
  // sourceContainerId: 'sourceContainer',
  // hashSplitter: '#',
});

window.addEventListener("load", function () {
  dom.prepare();
  dom.useLocationHash();

  const switcher = new Switch(
    {
      labelText: 'Show coverage',
      size: 0.5,
      stroke: 0.2,
      checked: true,
      callback: (checked) => dom.toggleRangesVisibility(checked),
    }
  );
  document.getElementById('sourceCodeCoverageSwitch').append(switcher.create());

  dom.source.addEventListener("click", function (event) {
    dom.filterRequirements(event);
  });

});

window.addEventListener("hashchange", () => dom.useLocationHash());
