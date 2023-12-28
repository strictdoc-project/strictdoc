

// *** IntersectionObserver

let data = {};

window.addEventListener("load",function(){

  const tocFrame = document.querySelector('#frame-toc');
  const contentFrame = document.querySelector('main');

  const linkList = tocFrame.querySelectorAll('a');
  const anchorList = contentFrame.querySelectorAll('sdoc-anchor');

  linkList.forEach(a => {
    const id = a.getAttribute('anchor');
    data[id] = {
      'a': a
    }
  });
  anchorList.forEach(anchor => {
    const id = anchor.id;
    data[id] = {
      'anchor': anchor,
      ...data[id]
    };
    createObserver(anchor);
  });

  // console.log(data);

  // *** handleHashChange

  const handleHashChange = () => {
    const hash = window.location.hash;
    // console.log("Hash changed:", hash);
    const match = hash.match(/#(.*)/);
    const fragment = match ? match[1] : null;
    // console.log("Fragment:", fragment);

    linkList.forEach(a => {
      a.removeAttribute('targeted');
    });
    data[fragment].a.setAttribute('targeted', '');
  }

  handleHashChange();
  window.addEventListener("hashchange", handleHashChange);

},false);

function createObserver(observedElement) {
  let observer;

  let options = {
    root: null,
    rootMargin: "0px",
  };

  observer = new IntersectionObserver(handleIntersect, options);
  observer.observe(observedElement);
}

function handleIntersect(entries, observer) {
  entries.forEach((entry) => {
    if (entry.intersectionRatio > 0) {
      data[entry.target.id].a.setAttribute('intersected', '');
    } else {
      data[entry.target.id].a.removeAttribute('intersected');
    }
  });
}


