(() => {
  // Deep-link navigation for chunked (lazily loaded) documents.
  //
  // TOC entries are <a anchor="X" href="#X" data-turbo="false">, so the
  // browser natively scrolls to the element with id="X". In chunked mode that
  // element lives inside a lazy <turbo-frame> that has not loaded yet, so
  // native navigation finds nothing and silently does not scroll.
  //
  // Each TOC <li> is stamped server-side with
  // data-chunk-frame="document-chunk-N" (see toc.jinja). When the target is
  // missing we force-load that one frame, then scroll once its content
  // arrives. Loading a single chunk is enough: the unloaded placeholders
  // above it reserve their height, so the target's scroll position holds.

  if (window.__sdocTocChunkNavWired) return;
  window.__sdocTocChunkNavWired = true;

  const TOC_FRAME_SELECTOR = "turbo-frame#frame-toc";

  function scrollToFragment(fragment) {
    const target = document.getElementById(fragment);
    if (target) target.scrollIntoView();
  }

  function chunkFrameForLink(link) {
    const item = link.closest("li");
    return item ? item.getAttribute("data-chunk-frame") : null;
  }

  function tocLinkForFragment(fragment) {
    const toc = document.querySelector(TOC_FRAME_SELECTOR);
    if (!toc) return null;
    return toc.querySelector(`a[anchor="${CSS.escape(fragment)}"]`);
  }

  function loadChunkThenScroll(frameId, fragment) {
    const frame = document.getElementById(frameId);
    if (!frame) return;
    if (frame.hasAttribute("complete")) {
      scrollToFragment(fragment);
      return;
    }
    // Register the load listener before triggering the fetch to avoid a race.
    const onFrameLoad = (event) => {
      if (event.target !== frame) return;
      document.removeEventListener("turbo:frame-load", onFrameLoad);
      scrollToFragment(fragment);
    };
    document.addEventListener("turbo:frame-load", onFrameLoad);
    // Switching loading from "lazy" to "eager" makes Turbo fetch src now.
    frame.setAttribute("loading", "eager");
  }

  function navigateToFragment(fragment, link) {
    if (!fragment) return;
    // Target already in the DOM: native navigation handles the scroll.
    if (document.getElementById(fragment)) return;
    const tocLink = link || tocLinkForFragment(fragment);
    if (!tocLink) return;
    const frameId = chunkFrameForLink(tocLink);
    if (frameId) loadChunkThenScroll(frameId, fragment);
  }

  // TOC click. data-turbo="false" means a native hash navigation; intercept
  // only when the target is missing so its chunk can be loaded first.
  document.addEventListener("click", (event) => {
    const link = event.target.closest
      ? event.target.closest("a[anchor]")
      : null;
    if (!link || !link.closest(TOC_FRAME_SELECTOR)) return;
    const fragment = link.getAttribute("anchor");
    if (!fragment || document.getElementById(fragment)) return;
    event.preventDefault();
    history.pushState(null, "", "#" + encodeURIComponent(fragment));
    navigateToFragment(fragment, link);
  });

  // Direct URL deep-links, browser back/forward, and other hash changes.
  window.addEventListener("hashchange", () => {
    navigateToFragment(decodeURIComponent(window.location.hash.slice(1)), null);
  });
  window.addEventListener("load", () => {
    if (window.location.hash) {
      navigateToFragment(
        decodeURIComponent(window.location.hash.slice(1)),
        null,
      );
    }
  });
})();
