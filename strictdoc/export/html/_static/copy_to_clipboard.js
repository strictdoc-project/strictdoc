(() => {

  // Turbo merges head scripts by their literal src attributes, so a visit
  // crossing document depths ("_static/..." vs "../_static/...") can execute
  // this file again (see the note in stimulus_application.js). Guard so the
  // document-level click listener is only registered once.
  if (window.__sdocCopyToClipboardWired) return;
  window.__sdocCopyToClipboardWired = true;

  const SEL_BUTTON = '[data-copy-clipboard-target="button"]';
  const SEL_COPY_ICON = '[data-copy-clipboard-target="copyIcon"]';
  const SEL_DONE_ICON = '[data-copy-clipboard-target="doneIcon"]';
  const SEL_COVER = '[data-copy-clipboard-target="cover"]';

  const SEL_FIELD = 'sdoc-field';
  const SEL_FIELD_SERVICE = 'sdoc-field-service';
  const SEL_FIELD_CONTENT = 'sdoc-field-content';

  function resolveURL(path) {
    // new URL(path, base) handles both cases without explicit absolute-check:
    // absolute URLs ignore the base and return as-is,
    // relative ones resolve against it.
    const resolved = new URL(path, window.location.href).href;
    // Expand folder to index if we run from the local file system.
    return (window.location.protocol === 'file:') ?
      resolved.replace(/#/, 'index.html?a=') :
      resolved.replace(/#/, '?a=');
  }

  // All copy buttons share data-copy-clipboard-target="button".
  // What to copy is determined by additional attributes on the button:
  //   data-anchor-id  → anchor ID (node anchor or inline RST anchor)
  //   data-path       → stable link URL (resolved at click time)
  //   neither         → text content of the parent sdoc-field
  function copyTextForButton(btn) {
    if (btn.dataset.anchorId) {
      return btn.dataset.anchorId;
    }
    if (btn.dataset.path) {
      return resolveURL(btn.dataset.path);
    }
    const field = btn.closest(SEL_FIELD);
    if (!field) {
      return null;
    }
    return field.querySelector(SEL_FIELD_CONTENT)?.innerText.trim() ?? '';
  }

  function feedbackRootForButton(btn) {
    if (btn.dataset.anchorId || btn.dataset.path) {
      return btn;
    }
    const field = btn.closest(SEL_FIELD);
    return field?.querySelector(SEL_FIELD_SERVICE) ?? btn;
  }

  function feedback(root, button) {
    const copyIcon = root.querySelector(SEL_COPY_ICON);
    const doneIcon = root.querySelector(SEL_DONE_ICON);
    const cover = root.querySelector(SEL_COVER);

    // make button visible
    if (button) button.style.opacity = 1;
    // make DONE icon visible (instead of default COPY)
    if (copyIcon) copyIcon.style.display = 'none';
    if (doneIcon) doneIcon.style.display = 'contents';

    if (cover) {
      // initial opacity
      let op = 1;
      cover.style.background = `rgba(242, 100, 42, ${op})`;
      const fadeTimer = setInterval(() => {
        // update cover
        cover.style.background = `rgba(242, 100, 42, ${op})`;
        if (op <= 0.1) {
          clearInterval(fadeTimer);
          // reset cover
          cover.style.background = '';
          // make button invisible
          if (button) button.style.opacity = '';
          // make COPY icon visible back
          if (copyIcon) copyIcon.style.display = 'contents';
          if (doneIcon) doneIcon.style.display = 'none';
        }
        op -= op * 0.1;
      }, 30);
    } else {
      setTimeout(() => {
        if (button) button.style.opacity = '';
        if (copyIcon) copyIcon.style.display = 'contents';
        if (doneIcon) doneIcon.style.display = 'none';
      }, 1500);
    }
  }

  function markMisconfigured(btn) {
    btn.title = 'Misconfigured: no sdoc-field context found';
    btn.style.cursor = 'not-allowed';
    btn.style.color = 'red';
    btn.style.background = 'rgb(255 0 0 / 10%)';
    btn.style.opacity = '1';
  }

  // One listener for the whole page. Works for content added later by
  // Turbo streams/frames with no re-wiring.
  document.addEventListener('click', (event) => {
    const btn = event.target.closest?.(SEL_BUTTON);
    if (!btn) return;
    event.preventDefault();
    const text = copyTextForButton(btn);
    if (text === null) {
      markMisconfigured(btn);
      return;
    }
    navigator.clipboard.writeText(text).then(
      () => feedback(feedbackRootForButton(btn), btn),
      () => console.warn('Clipboard write failed')
    );
  });

})();
