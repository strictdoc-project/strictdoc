window.onload = function () {

  console.log('I am in _print.js',);

  // Preparing templates.
  const {
    printableFlow,
    runningHeaderTemplate,
    runningFooterTemplate,
    printAreaHeight,
  } = prepareTemplates({
    printableFlow: '#printableFlow',
    pageTemplate: '#pageTemplate',
    printAreaTemplate: '#printAreaTemplate',
    runningHeaderTemplate: '#runningHeaderTemplate',
    runningFooterTemplate: '#runningFooterTemplate',
  });

  // The elementsPaddingCompensator is taken into account
  // in the calculation of page breaks in calculatePageBreaks().
  // It is used for Spacer that is added after each printable element
  // in makePreview().
  // This is done to make the page height predictable.
  const elementsPaddingCompensator = 16;

  // Adding IDs to nodes that we don't want to break,
  // and collecting their IDs and heights in printableElements
  // to then break down the content into pages.
  const printableElements = processPrintable({
    // use any selector:
    printable: '.printable',
    // use class selector:
    breakable: '.breakable',
  });

  // Calculate page breaks
  // and add flags to printableElements.
  // Returns pageBreaks.
  const pageBreaks = calculatePageBreaks({
    printableElements,
    printAreaHeight,
    elementsPaddingCompensator,
  });

  // Splitting content into virtual pages
  // and generating previews that look like PDF.
  makePreview({
    printableFlow,
    runningFooterTemplate,
    runningHeaderTemplate,
    printableElements,
    pageBreaks,
    printAreaHeight,
    elementsPaddingCompensator,
  });
};

// USED FUNCTIONS

function prepareTemplates({
  printableFlow,
  pageTemplate,
  printAreaTemplate,
  runningHeaderTemplate,
  runningFooterTemplate,
}) {

  // Get printable wrapper.
  const _printableFlow = document.querySelector(printableFlow);

  // Get page templates container.
  const _pageTemplate = document.querySelector(pageTemplate);

  // Get templates for cloning.
  const _printAreaTemplate = _pageTemplate.querySelector(printAreaTemplate);
  // const _runningHeaderTemplate = document.querySelector(runningHeaderTemplate).content;
  const _runningHeaderTemplate = _pageTemplate.querySelector(runningHeaderTemplate);
  const _runningFooterTemplate = _pageTemplate.querySelector(runningFooterTemplate);

  // Get print area height for calculating pages.
  const _printAreaHeight = _printAreaTemplate.offsetHeight;

  return {
    printableFlow: _printableFlow,
    runningHeaderTemplate: _runningHeaderTemplate,
    runningFooterTemplate: _runningFooterTemplate,
    printAreaHeight: _printAreaHeight,
  }
}

const processPrintable = ({
  printable,
  breakable,
}) => {

  // Checking for variable format.
  // Selector in breakable should be suitable for classList.contains
  if (breakable.charAt(0) === '.') {
    breakable = breakable.substring(1);
  }
  if (breakable.charAt(0) === '#') {
    console.error(` "breakable" var in processPrintable() should be suitable for classList.contains and contain only the class name!`);
  }

  // let accumulator of printable elements data
  const printableElements = [];

  // What we are going to do with the element:
  const processElement = (element) => {

    const elementId = printableElements.length;
    const elementHeight = element.offsetHeight;

    // Get offsetHeight and push to accumulator 'printableElements',
    printableElements.push({
      id: elementId, // is equal to id in array
      height: elementHeight,
    });

    // set ID to element, corresponding ID in accumulator 'printableElements'.
    element.id = `printable${elementId}`;

    // Add styles, compensate for visibility over the virtual page.
    element.style.position = 'relative';
  }

  // Get printable NodeList,
  // from all elements with selectors in 'printable'.
  [...document.querySelectorAll(printable)]
    .map((printableElement, id) => {

      // If the printable Element is breakable, process ONLY its child elements.
      if (printableElement.classList.contains(breakable) && printableElement.hasChildNodes()) {

        const breakableElement = printableElement;
        makeArrayOfNotTextChildNodes(breakableElement)
          .forEach((breakableElementChild) => {

            // The condition is specific to STRICTDOC:
            // '.document' is generated inside requirement statement,
            // so we have to process his children.
            if (breakableElementChild.classList.contains('document')) {

              const strictddocElement = breakableElementChild;
              makeArrayOfNotTextChildNodes(strictddocElement)

                .forEach((strictddocElementChild) => {
                  processElement(strictddocElementChild);
                })

            } else {
              // Else process other childs of breakable Element.
              processElement(breakableElementChild);
            }
          })

      } else {
        // Else process the printable Element.
        processElement(printableElement);
      }
    })

  console.log('printableElements: \n', printableElements);
  return printableElements;
}

function calculatePageBreaks({
  printableElements,
  printAreaHeight,
  // We take the padding compensator into account in this function in the calculation of the page breaks:
  // via compensatedCurrentElementHeight.
  // It is used for Spacer and is added after each printable element.
  elementsPaddingCompensator = 16
}) {

  // Calculate from which elements new pages will start.
  // We will accumulate the height of the elements in the heightAccumulator
  // and compare it to the printAreaHeight - maximum height of the printed area.
  let heightAccumulator = 0;

  // init with flagged front page
  const pageBreaks = [0];

  function registerPageStart(id) {
    // mark the (CURRENT) element as a page start,
    printableElements[id] = {
      ...printableElements[id],
      pageStart: true,
    };
  }

  function registerPageBreak(id, memorizedPageContentHeight) {
    // register the page break,
    pageBreaks.push(id);

    // mark the (PREVIOUS) element as a page break,
    // write the memorized pageContentHeight down,
    // write the page number down,
    printableElements[id] = {
      ...printableElements[id],
      pageBreak: memorizedPageContentHeight,
      pageNumber: pageBreaks.length,
    };
  }

  // We will collect the IDs of the page breaks and height of contents
  // into the 'printableElements' array.

  // Register the first element as a page start.
  registerPageStart(0);

  // process content flow
  printableElements.map((element, id) => {

    const compensatedCurrentElementHeight = element.height + elementsPaddingCompensator;

    // TODO the case when the element is larger than the printable area, we will handle later:

    // Memorize the previous accumulator value.
    const pageContentHeight = heightAccumulator;

    // Add element height to the accumulator.
    heightAccumulator = heightAccumulator + compensatedCurrentElementHeight;

    // If the accumulator is overflowed,
    if (heightAccumulator > printAreaHeight) {

      // mark the CURRENT element as a page start,
      registerPageStart(id);
      // mark the PREVIOUS element as a page break.
      registerPageBreak(id - 1, pageContentHeight);

      // reset the accumulator
      // and add to it the height of the current element,
      // which will be the start of the new page.
      heightAccumulator = compensatedCurrentElementHeight;
    }
  })

  // Register the last element as a page break
  // and assign the last heightAccumulator value
  // as the height of the last page.
  // We need it to generate the footer on the last page correctly.
  registerPageBreak(printableElements.length - 1, heightAccumulator);

  console.log('pageBreaks:\n', pageBreaks);
  return pageBreaks;
}

function makePreview({
  // elements
  printableFlow,
  runningFooterTemplate,
  runningHeaderTemplate,
  // data
  printableElements,
  pageBreaks,
  printAreaHeight,
  // Consider the height compensator.
  // It is taken into account in the calculation of page breaks.
  // It is used for Spacer and is added after each printable element.
  elementsPaddingCompensator = 16
}) {

  // Set the header and footer for all pages:

  printableElements.map((item) => {

    const { id, height, pageStart, pageBreak, pageNumber } = item;
    const element = printableFlow.querySelector(`#printable${id}`);

    if (pageStart) {
      // Starting a new virtual page.
      const runningHeader = runningHeaderTemplate.cloneNode(true);
      element.before(runningHeader);
    }

    if (pageBreak) {
      // Closing the current virtual page,
      // which ends with a page break.
      const runningFooter = runningFooterTemplate.cloneNode(true);
      // Add page number.
      runningFooter.querySelector('.page-number').innerHTML = ` ${pageNumber} / ${pageBreaks.length}`;
      element.after(runningFooter);

      // To compensate for the empty space at the end of the page, add a padding to footer.
      const pageHeightCompensatorDIV = document.createElement('div');
      pageHeightCompensatorDIV.style.paddingTop = printAreaHeight - pageBreak + 'px';
      element.after(pageHeightCompensatorDIV);
    }

    // Add elementPaddingCompensatorDIV after each printable element.
    const elementPaddingCompensatorDIV = document.createElement('div');
    elementPaddingCompensatorDIV.style.paddingTop = elementsPaddingCompensator + 'px';
    elementPaddingCompensatorDIV.style.position = 'relative';
    element.after(elementPaddingCompensatorDIV);
  })
}

function makeArrayOfNotTextChildNodes(element) {
  // Check that the element is a tag and not '#text'.
  // https://developer.mozilla.org/ru/docs/Web/API/Node/nodeName
  let children = element.childNodes;
  return [...children].filter(item => item.tagName);
}
