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
  // data-chunk-frame="document-chunk-N" (see toc.jinja), and each unloaded
  // chunk placeholder carries its own data-anchors list (see
  // document_chunk_lazy_placeholder.jinja.html) naming every node's anchor
  // in that chunk, including nodes without a TITLE that have no TOC entry
  // at all. When the target is missing we resolve its chunk from that list
  // (falling back to the TOC for a link that already carries its own
  // chunk-frame data, e.g. a TOC click) and force-load that one frame, then
  // scroll once its content arrives. Loading a single chunk is enough: the
  // unloaded placeholders above it reserve their height, so the target's
  // scroll position holds.

  if (window.__sdocTocChunkNavWired) return;
  window.__sdocTocChunkNavWired = true;

  const TOC_FRAME_SELECTOR = "turbo-frame#frame-toc";
  const CONTENT_FRAME_SELECTOR = "[js-toc_highlighting-content_root]";
  const CHUNK_PLACEHOLDER_CLASS = "document-chunk-placeholder";
  const PRELOAD_MARGIN = "800px 0px";
  const observedPlaceholders = new WeakSet();

  // The fragment the user most recently navigated to. A chunk requested for
  // an earlier navigateToFragment() call can still be mid-flight (loading or
  // fetching) when a later one starts and resolves first - without this,
  // the earlier chunk's load listener would fire afterwards and bounce
  // location.hash back to its now-stale fragment. Comparing against this on
  // resolution lets a superseded load recognize itself and skip the bounce.
  let pendingFragment = null;

  // Server mode fetches a chunk from /fragments/document/.../chunk via a
  // Turbo frame (loading="eager" flips a lazy frame to load its src). Static
  // export has no server for that route, so its chunks are pre-rendered to
  // .js files and delivered as a <script src> instead (see
  // document_chunk_lazy_placeholder_static.jinja.html and
  // DocumentHTMLGenerator._export_static_chunks) - only loadStaticChunk()
  // and its two call sites differ; TOC click/hashchange handling, scrolling,
  // and the turbo:frame-load cleanup listener below are delivery-agnostic.
  // loadStaticChunk() also dispatches a synthetic "turbo:before-fetch-response"
  // that real Turbo frame loads emit natively, so content_viewport_restoration.js
  // (loaded for both modes when the document is chunked) treats both delivery
  // paths the same.
  const IS_STATIC_EXPORT = document.querySelector(
    'meta[name="strictdoc-export-type"]'
  )?.content === "static";

  // Load a static chunk's .js file, splice its rendered HTML into the
  // placeholder, and dispatch the same "turbo:before-fetch-response" and
  // "turbo:frame-load" events Turbo fires around a server-mode frame load,
  // so every existing listener (content_viewport_restoration.js's geometry
  // snapshot/compensation, the preload observer's unobserve, the
  // placeholder-class cleanup below, and this file's own onFrameLoad
  // handlers) keeps working unchanged.
  async function loadStaticChunk(frame) {
    const src = frame.dataset.chunkSrc;
    const key = frame.dataset.chunkKey;
    if (!src || !key) return;
    await window.StrictDoc.loadScript(src);
    const html = window.StrictDoc.chunks?.[key];
    if (html === undefined) return;
    // The generated .js file wraps the chunk's HTML exactly as rendered by
    // document_chunk.jinja.html, i.e. a single <turbo-frame id="...">...
    // </turbo-frame> root. Splice in its *inner* content only, so this same
    // placeholder element (not a replacement) stays the live DOM node the
    // rest of this file dispatches/observes events on.
    const template = document.createElement("template");
    template.innerHTML = html.trim();
    // Fired before the placeholder's content changes so
    // content_viewport_restoration.js can snapshot the pre-load viewport
    // geometry, exactly as it does for the real fetch response server mode
    // gets from Turbo before that library inserts a frame's content.
    frame.dispatchEvent(
      new Event("turbo:before-fetch-response", { bubbles: true })
    );
    frame.innerHTML = template.content.firstElementChild.innerHTML;
    frame.dispatchEvent(new Event("turbo:frame-load", { bubbles: true }));
  }

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

  // A node without a TITLE has no TOC entry at all (see
  // SDocDocumentIterator.table_of_contents()), so tocLinkForFragment()
  // cannot resolve it. Every still-unloaded chunk placeholder carries its
  // own data-anchors list (see document_chunk_lazy_placeholder.jinja.html),
  // covering every content node in that chunk, TOC-listed or not - this is
  // the primary resolution path; the TOC lookup remains as a fallback.
  function chunkFrameForAnchor(fragment) {
    const placeholders = document.querySelectorAll(
      `.${CHUNK_PLACEHOLDER_CLASS}[data-anchors]`
    );
    for (const placeholder of placeholders) {
      if (placeholder.dataset.anchors.split(" ").includes(fragment)) {
        return placeholder.id;
      }
    }
    const tocLink = tocLinkForFragment(fragment);
    return tocLink ? chunkFrameForLink(tocLink) : null;
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
      // A newer navigateToFragment() call may have superseded this one
      // while its chunk was still loading - see pendingFragment above.
      if (fragment !== pendingFragment) return;
      // Same guard as above: only refresh if the target actually loaded
      // into this chunk.
      if (document.getElementById(fragment)) {
        refreshTargetElement(fragment);
      }
    };
    document.addEventListener("turbo:frame-load", onFrameLoad);
    if (IS_STATIC_EXPORT) {
      loadStaticChunk(frame);
    } else {
      // Switching loading from "lazy" to "eager" makes Turbo fetch src now.
      frame.setAttribute("loading", "eager");
    }
  }

  function navigateToFragment(fragment, link) {
    if (!fragment) return;
    // This is now the desired target - any chunk load still in flight for a
    // fragment requested by an earlier call is superseded (see
    // pendingFragment above).
    pendingFragment = fragment;
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
    const frameId = link
      ? chunkFrameForLink(link)
      : chunkFrameForAnchor(fragment);
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
        if (IS_STATIC_EXPORT) {
          loadStaticChunk(entry.target);
        } else {
          entry.target.setAttribute("loading", "eager");
        }
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
