window.onload = function () {

  console.log('I am in _print.js',);

  // Preparing the DOM elements.
  const {
    printable,
    frontpage,
    runningHeaderTemplate,
    runningFooterTemplate,
  } = prepareDomElements({
    printable: '#printable',
    frontpage: '.frontpage',
    runningHeaderTemplate: '#runningHeaderTemplate',
    runningFooterTemplate: '#runningFooterTemplate',
  });

  // Defining the constant printAreaHeight corresponding frontpage offsetHeight.
  const printAreaHeight = frontpage.offsetHeight;

  // Adding IDs to nodes (that) we don't want to break,
  // and collecting their heights
  // to then break down the content into pages.
  // ? level articles ???
  // const offsetHeightsOfPageElements = useArticles();
  // ? level sections ???
  // const offsetHeightsOfPageElements = useSections('section, .frontpage');
  const offsetHeightsOfPageElements = usePrintableElements('.printable_element');

  const pageBreaks = makePageBreaks({
    offsetHeightsOfPageElements,
    printAreaHeight
  });

  // Splitting content into virtual pages
  // and generating previews that look like PDF.
  makePreview({
    printable,
    frontpage,
    runningFooterTemplate,
    runningHeaderTemplate,
    pageBreaks,
    printAreaHeight
  });

};

// USED FUNCTIONS

function prepareDomElements({
  printable,
  frontpage,
  runningHeaderTemplate,
  runningFooterTemplate,
}) {

  // Get printable wrapper.
  const _printable = document.querySelector(printable);

  // Get frontpage.
  const _frontpage = _printable.querySelector(frontpage);

  // Get templates.
  const _runningHeaderTemplate = document.querySelector(runningHeaderTemplate).content;
  const _runningFooterTemplate = document.querySelector(runningFooterTemplate).content;

  return {
    printable: _printable,
    frontpage: _frontpage,
    runningHeaderTemplate: _runningHeaderTemplate,
    runningFooterTemplate: _runningFooterTemplate,
  }
}

function usePrintableElements(selectors) {

  let offsetHeightsOfPageElements = [];

  // Get printable NodeList,
  // from all <sections> tags.
  const sections = [...document.querySelectorAll(selectors)];
  sections.map((element, id) => {
    // Get offsetHeight and push to accumulator,
    offsetHeightsOfPageElements.push(element.offsetHeight);
    // set ID to element, corresponding ID in accumulator.
    element.id = `printable${offsetHeightsOfPageElements.length - 1}`;
  })

  console.log(offsetHeightsOfPageElements);
  return offsetHeightsOfPageElements;
}

function useArticles(selectors) {

  let offsetHeightsOfPageElements = [];

  // Get printable NodeList,
  // for all children that are tags,
  // add IDs and collect their heights to offsetHeightsOfPageElements.
  if (printable.hasChildNodes()) {
    // So first we check to see if the object is empty, if it has children.

    let children = printable.childNodes;

    // children.forEach()
    for (let i = 0; i < children.length; ++i) {

      // Check that the element is a tag and not '#text'.
      // https://developer.mozilla.org/ru/docs/Web/API/Node/nodeName
      if (children[i].tagName) {

        // Get offsetHeight and push to accumulator,
        offsetHeightsOfPageElements.push(children[i].offsetHeight);
        // set ID to element, corresponding ID in accumulator.
        children[i].id = `printable${offsetHeightsOfPageElements.length - 1}`;

      }
    }
  }

  return offsetHeightsOfPageElements;
}

function makePageBreaks({
  offsetHeightsOfPageElements,
  printAreaHeight
}) {

  // Calculate from which elements new pages will start.
  // We will accumulate the height of the elements in the heightAccumulator
  // and compare it to the printAreaHeight - maximum height of the printed area.
  let heightAccumulator = 0;
  // We will collect the IDs of the page breaks and height of contents
  // into the 'pageBreaks' array.
  // Initiate it with a page break after the frontpage.
  let pageBreaks = [
    {
      id: 0,
      previousPageContentHeight: printAreaHeight
    }
  ];

  // We start the loop with 1 because the frontpage has a fixed height
  // and we've already added a page break after frontpage when initializing 'pageBreaks'.
  for (let i = 1; i < offsetHeightsOfPageElements.length; ++i) {

    const currentElementHeight = offsetHeightsOfPageElements[i];

    // TODO the case when the element is larger than the printable area, we will handle later:
    // // if the item fits in the height of the printing area
    // if (offsetHeightsOfPageElements[i] <= printAreaHeight) {
    //   // add its height to the accumulator
    //   heightAccumulator = heightAccumulator + currentElementHeight;
    // }

    // Reserve the previous accumulator value.
    const previousPageContentHeight = heightAccumulator;

    // Add elements height to the accumulator.
    heightAccumulator = heightAccumulator + currentElementHeight;

    // If the accumulator is overflowed,
    if (heightAccumulator >= printAreaHeight) {
      // // NOT: mark current element as the beginning of a new page,
      // mark the PREVIOUS element as a page break,
      pageBreaks.push({
        id: i - 1,
        previousPageContentHeight: previousPageContentHeight
      });
      // reset the accumulator and add current element height.
      heightAccumulator = currentElementHeight;
    }

    // register the last element as a page break
    // and store the resulting content height of the last page.
    if (i === offsetHeightsOfPageElements.length - 1) {
      pageBreaks.push({
        id: i,
        previousPageContentHeight: heightAccumulator
      });
    }
  }

  return pageBreaks;
}

function makePreview({
  printable,
  frontpage,
  runningFooterTemplate,
  runningHeaderTemplate,
  pageBreaks,
  printAreaHeight,
}) {

  // Set the header for the frontpage here,
  // because it cannot be set in the loop.
  frontpage.before(runningHeaderTemplate.cloneNode(true));

  // Set the header and footer for all pages in loop:
  // // pageBreaks.forEach(({ id, previousPageContentHeight }) => {
  for (let i = 0; i < pageBreaks.length; ++i) {

    const { id, previousPageContentHeight } = pageBreaks[i];

    // Close the current page,
    // which ends with a page break.
    const pageEnd = printable.querySelector(`#printable${id}`);
    const runningFooter = runningFooterTemplate.cloneNode(true);
    // Add page number.
    runningFooter.querySelector('.page-number').innerHTML = ` ${i + 1} / ${pageBreaks.length}`;
    pageEnd?.after(runningFooter);


    // To compensate for the empty space at the end of the page, add a padding to footer.
    const compensateDiv = document.createElement('div');
    const paddingCompensation = printAreaHeight - previousPageContentHeight
    compensateDiv.style.paddingTop = paddingCompensation + 'px';
    pageEnd?.after(compensateDiv);

    // Starting a new page,
    //which begins after a page break.
    const pageStart = printable.querySelector(`#printable${id + 1}`);
    // In the case of the last page we use the optionality.
    pageStart?.before(runningHeaderTemplate.cloneNode(true));

  };
}
