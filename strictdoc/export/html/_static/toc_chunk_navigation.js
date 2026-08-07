(() => {
  // Behavior for chunked (lazily loaded) documents: deep-link navigation,
  // clearing the placeholder's reserved scroll space once a chunk has
  // loaded, and preloading chunks slightly ahead of scroll.
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
  const CONTENT_FRAME_SELECTOR = "[js-toc_highlighting-content_root]";
  const CHUNK_PLACEHOLDER_CLASS = "document-chunk-placeholder";
  const PRELOAD_MARGIN = "800px 0px";
  const observedPlaceholders = new WeakSet();

  function scrollToFragment(fragment) {
    const target = document.getElementById(fragment);
    if (!target) return;
    const scrollElementToOffset =
      window.StrictDoc.contentViewport?.scrollElementToOffset;
    if (scrollElementToOffset) {
      scrollElementToOffset(target, 0);
      return;
    }
    // The scroll container has scroll-behavior: smooth (content.css), so a
    // plain scrollIntoView() animates toward an endpoint computed once, up
    // front. Chunks between the old position and the target can still be
    // resolving from their estimated placeholder height to their real
    // rendered height while that animation is in flight (preloadObserver
    // below fetches them slightly ahead of scroll), shifting the target's
    // actual position mid-animation - the scroll then lands short of it.
    // Jump instantly instead: this removes the animation window entirely,
    // so there is nothing left for a mid-flight layout shift to race
    // against. Only this programmatic jump is affected - manual scrolling
    // keeps the smooth behavior from the CSS.
    const scrollContainer = document.querySelector(CONTENT_FRAME_SELECTOR);
    const previousScrollBehavior = scrollContainer?.style.scrollBehavior;
    if (scrollContainer) scrollContainer.style.scrollBehavior = "auto";
    target.scrollIntoView();
    if (scrollContainer) {
      scrollContainer.style.scrollBehavior = previousScrollBehavior || "";
    }
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

  function refreshTargetElement(fragment) {
    // Fragment navigation (a TOC click, hashchange, or the initial page
    // load) may already have run before this chunk had loaded, at which
    // point no element matched the fragment. Browsers decide CSS :target
    // once, when the "scroll to the fragment" algorithm runs for a
    // navigation event (a real hash assignment, history traversal, or page
    // load) - they do not re-run it later just because a matching element
    // now exists in the DOM. This function forces that algorithm to run
    // again now that the target actually exists.
    //
    // Re-assigning the exact same hash value is a no-op (no navigation, no
    // "hashchange", no :target re-evaluation), so the current entry's hash
    // is first changed to a placeholder via history.replaceState() - in
    // place, no new history entry, and (like pushState) it does not run
    // the fragment-navigation algorithm either. The placeholder is
    // deliberately non-empty and never matches a real id: an *empty*
    // fragment is special-cased by browsers to scroll to the top of the
    // document, which a non-matching-but-non-empty one is not.
    //
    // The location.hash assignment that follows is then a genuine change
    // from that placeholder, so it *does* run the fragment-navigation
    // algorithm (finding the target and setting :target) and fires
    // "hashchange" - which the listener below already handles, calling
    // scrollToFragment() once it re-reads window.location.hash. It is also
    // the only step that pushes a history entry, so back/forward behaves
    // exactly as for a single, ordinary navigation to the fragment - the
    // placeholder bounce leaves no trace in history.
    const encoded = encodeURIComponent(fragment);
    history.replaceState(
      null,
      "",
      location.pathname + location.search + `#${encoded}--sdoc-target-refresh`
    );
    location.hash = encoded;
  }

  function loadChunkThenScroll(frameId, fragment) {
    const frame = document.getElementById(frameId);
    if (!frame) return;
    if (!frame.classList.contains(CHUNK_PLACEHOLDER_CLASS)) {
      // The frame is loaded, but confirm the target actually exists before
      // refreshing it. If it does not (e.g. a stale/renamed anchor whose
      // TOC entry still points at an old id), refreshTargetElement()
      // would bounce the hash, which fires "hashchange", which re-enters
      // navigateToFragment() and right back here - an infinite loop, since
      // nothing about the missing target would ever change.
      if (document.getElementById(fragment)) {
        refreshTargetElement(fragment);
      }
      return;
    }
    // Register the load listener before triggering the fetch to avoid a race.
    const onFrameLoad = (event) => {
      if (event.target !== frame) return;
      document.removeEventListener("turbo:frame-load", onFrameLoad);
      // Same guard as above: only refresh if the target actually loaded
      // into this chunk.
      if (document.getElementById(fragment)) {
        refreshTargetElement(fragment);
      }
    };
    document.addEventListener("turbo:frame-load", onFrameLoad);
    // Switching loading from "lazy" to "eager" makes Turbo fetch src now.
    frame.setAttribute("loading", "eager");
  }

  function navigateToFragment(fragment, link) {
    if (!fragment) return;
    // Target already in the DOM: scroll it ourselves rather than deferring
    // to native fragment navigation. Native navigation also respects
    // scroll-behavior: smooth on .main, and unloaded chunk placeholders can
    // still sit between the current position and the target - the same
    // mid-scroll layout-shift race scrollToFragment() guards against.
    if (document.getElementById(fragment)) {
      window.StrictDoc.contentViewport?.beginExplicitNavigation?.(null);
      scrollToFragment(fragment);
      return;
    }
    const tocLink = link || tocLinkForFragment(fragment);
    if (!tocLink) return;
    const frameId = chunkFrameForLink(tocLink);
    if (frameId) {
      window.StrictDoc.contentViewport?.beginExplicitNavigation?.(frameId);
      loadChunkThenScroll(frameId, fragment);
    }
  }

  // TOC click. Drive navigation via location.hash (not history.pushState(),
  // which fires neither "hashchange" nor :target) so native hashchange and
  // :target fire correctly. The same-hash case is handled separately just
  // below. An unloaded target's chunk is refreshed once loaded - see
  // refreshTargetElement().
  document.addEventListener("click", (event) => {
    const link = event.target.closest
      ? event.target.closest("a[anchor]")
      : null;
    if (!link || !link.closest(TOC_FRAME_SELECTOR)) return;
    const fragment = link.getAttribute("anchor");
    if (!fragment) return;
    event.preventDefault();

    // Assigning the same value to location.hash is a no-op (no navigation,
    // no "hashchange") - clicking the TOC entry for the section the URL is
    // already on (e.g., after scrolling away manually and wanting to jump
    // back to it) needs its own explicit scroll instead of relying on a
    // hash change that will not happen.
    if (decodeURIComponent(location.hash.slice(1)) === fragment) {
      navigateToFragment(fragment, link);
      return;
    }

    // The browser performs its own native scroll-to-fragment as part of
    // processing the hash change below, using whatever scrollBehavior is
    // current at that point - force it instant first, same reasoning as
    // scrollToFragment(). If the target is not loaded yet, this native
    // scroll silently finds nothing (same as always), and
    // scrollToFragment() (invoked later, once the chunk loads) does its
    // own instant scroll independently.
    const scrollContainer = document.querySelector(CONTENT_FRAME_SELECTOR);
    const previousScrollBehavior = scrollContainer?.style.scrollBehavior;
    if (scrollContainer) scrollContainer.style.scrollBehavior = "auto";

    location.hash = encodeURIComponent(fragment);

    setTimeout(() => {
      if (scrollContainer) {
        scrollContainer.style.scrollBehavior = previousScrollBehavior || "";
      }
    }, 0);
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

  // Clear a chunk's reserved scroll space once its content has loaded.
  //
  // node.css reserves an approximate min-height on
  // turbo-frame.document-chunk-placeholder so the browser does not fetch all
  // below-the-fold chunks immediately. That reservation is only ever an
  // estimate (average node height * chunk size), and this Turbo build never
  // reflects load completion as an HTML attribute (it observes only
  // "disabled", "loading", "src", and toggles "busy" while a fetch is
  // in-flight -- there is no "complete" attribute to select against). Left
  // alone, the estimated min-height would apply forever, leaving a permanent
  // blank gap whenever the real content is shorter than the estimate.
  // Removing the placeholder class on load hands sizing back to the actual
  // rendered content.
  document.addEventListener("turbo:frame-load", (event) => {
    const frame = event.target;
    if (!frame.id?.startsWith("document-chunk-")) return;
    // Loaded chunks no longer need preload observation.
    preloadObserver.unobserve(frame);
    frame.classList.remove(CHUNK_PLACEHOLDER_CLASS);
  });

  // Preload chunks slightly ahead of scroll.
  //
  // Beyond the permanent-gap issue above, an unloaded chunk's fetch is only
  // triggered once its placeholder has already scrolled into the viewport
  // (Turbo's lazy-loading IntersectionObserver uses no rootMargin), so even
  // a correctly-sized placeholder can show a brief blank flash while the
  // fetch is in flight. Watch placeholders with a lead margin and switch
  // them to eager loading before they are actually visible.
  //
  // Do not collect placeholders here. StrictDoc.onInsert below registers both
  // existing placeholders and placeholders inserted later by Turbo updates.
  const preloadObserver = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        preloadObserver.unobserve(entry.target);
        entry.target.setAttribute("loading", "eager");
      }
    }, {
      rootMargin: PRELOAD_MARGIN
    },
  );

  function observePlaceholder(frame) {
    // Only document chunk frames own this placeholder contract.
    if (!frame.id?.startsWith("document-chunk-")) return;
    if (!frame.classList.contains(CHUNK_PLACEHOLDER_CLASS)) return;
    if (observedPlaceholders.has(frame)) return;
    observedPlaceholders.add(frame);
    preloadObserver.observe(frame);
  }

  // Covers placeholders rendered now and inserted later by Turbo updates.
  window.StrictDoc.onInsert(
    `.${CHUNK_PLACEHOLDER_CLASS}`,
    observePlaceholder,
  );
})();
