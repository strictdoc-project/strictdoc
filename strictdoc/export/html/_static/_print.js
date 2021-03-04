window.onload = function () {

  console.log('I am in _print.js',);

  // Preparing the DOM elements.
  const {
    printableFlow,
    frontpage,
    runningHeaderTemplate,
    runningFooterTemplate,
  } = prepareDomElements({
    printableFlow: '#printable',
    frontpage: '.frontpage',
    runningHeaderTemplate: '#runningHeaderTemplate',
    runningFooterTemplate: '#runningFooterTemplate',
  });

  // Defining the constant printAreaHeight corresponding frontpage offsetHeight.
  const printAreaHeight = frontpage.offsetHeight;

  // The height compensator is taken into account
  // in the calculation of page breaks
  // in makePageBreaks().
  // It is used for Spacer and is added after each printable element
  // in makePreview().
  const compensatorHeight = 16;

  // Adding IDs to nodes (that) we don't want to break,
  // and collecting their heights
  // to then break down the content into pages.
  // ? use articles level
  // const allPrinableElementsOffsetHeights = useArticles();
  // ? use elements level
  const allPrinableElementsOffsetHeights = processPrintable({
    // use any selector:
    printable: '.printable',
    // use class selector:
    breakable: '.breakable',
  });

  const pageBreaks = makePageBreaks({
    allPrinableElementsOffsetHeights,
    printAreaHeight,
    compensatorHeight,
  });

  // Splitting content into virtual pages
  // and generating previews that look like PDF.
  makePreview({
    printableFlow,
    frontpage,
    runningFooterTemplate,
    runningHeaderTemplate,
    pageBreaks,
    printAreaHeight,
    compensatorHeight,
  });

};

// USED FUNCTIONS

function prepareDomElements({
  printableFlow,
  frontpage,
  runningHeaderTemplate,
  runningFooterTemplate,
}) {

  // Get printable wrapper.
  const _printableFlow = document.querySelector(printableFlow);

  // Get frontpage.
  const _frontpage = _printableFlow.querySelector(frontpage);

  // Get templates.
  const _runningHeaderTemplate = document.querySelector(runningHeaderTemplate).content;
  const _runningFooterTemplate = document.querySelector(runningFooterTemplate).content;

  return {
    printableFlow: _printableFlow,
    frontpage: _frontpage,
    runningHeaderTemplate: _runningHeaderTemplate,
    runningFooterTemplate: _runningFooterTemplate,
  }
}

function makeArrayOfNotTextChildNodes(element) {
  // Check that the element is a tag and not '#text'.
  // https://developer.mozilla.org/ru/docs/Web/API/Node/nodeName
  let children = element.childNodes;
  return [...children].filter(item => item.tagName);
}

function processPrintable({
  printable,
  breakable,
  // The height compensator is taken into account in the calculation of page breaks.
  // It is used for Spacer and is added after each printable element.
  compensatorHeight = 16
}) {

  // Checking for variable format.
  // breakable should be suitable for classList.contains
  if (breakable.charAt(0) === '.') {
    breakable = breakable.substring(1);
  }
  if (breakable.charAt(0) === '#') {
    console.error('"breakable" var in processPrintable() should be suitable for classList.contains and contain only the class name!');
  }

  // let accumulator
  let allPrinableElementsOffsetHeights = [];

  // What we are going to do with the element:
  const processElement = (element) => {
    // Get offsetHeight and push to accumulator,
    allPrinableElementsOffsetHeights.push(element.offsetHeight);
    // set ID to element, corresponding ID in accumulator.
    element.id = `printable${allPrinableElementsOffsetHeights.length - 1}`;

    // If an element has no class '.printable' and is found as a child of content .printable, add a class to it.
    // element.classList.add(printable.substring(1));

    // Add styles, compensate for visibility over the virtual page.
    element.style.position = 'relative';

    // TODO
    // Add compensator after each printable element.
    // We will add a Footer after breakable in makePreview(),
    // and its compensator will go to the next page,
    // and it will turn out ...
    const compensator = document.createElement('div');
    compensator.style.paddingTop = compensatorHeight + 'px';
    compensator.style.background = 'red';
    element.after(compensator);
  }

  // Get printable NodeList,
  // from all .selectors elements.
  const sections = [...document.querySelectorAll(printable)];
  sections.map((element, id) => {

    // If the item is breakable, process ONLY its child elements.
    if (element.classList.contains(breakable) && element.hasChildNodes()) {

      const children = makeArrayOfNotTextChildNodes(element);

      children.forEach((element) => {
        if (element.classList.contains('document')) {
          // The condition is specific to STRICTDOC:
          // '.document' is generated inside requirement statement.
          const documentChildren = makeArrayOfNotTextChildNodes(element);

          documentChildren.forEach((element) => {
            processElement(element);
          })
        } else {
          processElement(element);
        }
      })
    } else {
      // Else process the elements.
      processElement(element);
    }
  })

  console.log('allPrinableElementsOffsetHeights: \n', allPrinableElementsOffsetHeights);
  return allPrinableElementsOffsetHeights;
}

function makePageBreaks({
  allPrinableElementsOffsetHeights,
  printAreaHeight,
  // We take the height compensator into account in this function in the calculation of the page breaks:
  // via compensatedCurrentElementHeight.
  // It is used for Spacer and is added after each printable element.
  compensatorHeight = 16
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
  for (let i = 1; i < allPrinableElementsOffsetHeights.length; ++i) {

    const currentElementHeight = allPrinableElementsOffsetHeights[i];
    const compensatedCurrentElementHeight = currentElementHeight + compensatorHeight;

    // TODO the case when the element is larger than the printable area, we will handle later:
    // // if the item fits in the height of the printing area
    // if (allPrinableElementsOffsetHeights[i] <= printAreaHeight) {
    //   // add its height to the accumulator
    //   heightAccumulator = heightAccumulator + currentElementHeight;
    // }

    // Reserve the previous accumulator value.
    const previousPageContentHeight = heightAccumulator;

    // Add elements height to the accumulator.
    heightAccumulator = heightAccumulator + compensatedCurrentElementHeight;

    // If the accumulator is overflowed,
    if (heightAccumulator >= printAreaHeight) {
      // // NOT: mark current element as the beginning of a new page,
      // mark the PREVIOUS element as a page break,
      pageBreaks.push({
        id: i - 1,
        previousPageContentHeight: previousPageContentHeight
      });
      // reset the accumulator and add current element height.
      heightAccumulator = compensatedCurrentElementHeight;
    }

    // register the last element as a page break
    // and store the resulting content height of the last page.
    if (i === allPrinableElementsOffsetHeights.length - 1) {
      pageBreaks.push({
        id: i,
        previousPageContentHeight: heightAccumulator
      });
    }
  }

  return pageBreaks;
}

function makePreview({
  printableFlow,
  frontpage,
  runningFooterTemplate,
  runningHeaderTemplate,
  pageBreaks,
  printAreaHeight,
  // Consider the height compensator.
  // It is taken into account in the calculation of page breaks.
  // It is used for Spacer and is added after each printable element.
  compensatorHeight = 16
}) {

  console.log('pageBreaks: \n', pageBreaks)

  // Set the header for the frontpage here,
  // because it cannot be set in the loop.
  frontpage.before(runningHeaderTemplate.cloneNode(true));

  // Set the header and footer for all pages in loop:
  // // pageBreaks.forEach(({ id, previousPageContentHeight }) => {

  // TODO  MAP?

  for (let i = 0; i < pageBreaks.length; ++i) {

    const { id, previousPageContentHeight } = pageBreaks[i];

    // Close the current page,
    // which ends with a page break.
    const pageEnd = printableFlow.querySelector(`#printable${id}`);
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
    const pageStart = printableFlow.querySelector(`#printable${id + 1}`);
    // In the case of the last page we use the optionality.
    pageStart?.before(runningHeaderTemplate.cloneNode(true));

  };
}

// NOT IN USE:

// function useArticles(selectors) {

//   let allPrinableElementsOffsetHeights = [];

//   // Get printable NodeList,
//   // for all children that are tags,
//   // add IDs and collect their heights to allPrinableElementsOffsetHeights.
//   if (printable.hasChildNodes()) {
//     // So first we check to see if the object is empty, if it has children.

//     let children = printable.childNodes;

//     // children.forEach()
//     for (let i = 0; i < children.length; ++i) {

//       // Check that the element is a tag and not '#text'.
//       // https://developer.mozilla.org/ru/docs/Web/API/Node/nodeName
//       if (children[i].tagName) {

//         // Get offsetHeight and push to accumulator,
//         allPrinableElementsOffsetHeights.push(children[i].offsetHeight);
//         // set ID to element, corresponding ID in accumulator.
//         children[i].id = `printable${allPrinableElementsOffsetHeights.length - 1}`;

//       }
//     }
//   }

//   return allPrinableElementsOffsetHeights;
// }
