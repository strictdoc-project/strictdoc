// @relation(SDOC-SRS-208, scope=file)
//
// Link widget: the "link" widget of field_widgets.js. It writes a
// [LINK: <UID>] tag into an RST or Markdown field.
//
// A popup at the caret lists the link targets from /autocomplete/link:
// documents, sections, nodes, and anchors with a UID. The targets of the
// current document (the form's "context_document_mid" input) come first.
// The popup opens when the user types one of the triggers:
// - "@" at the start of a word. The query is the text after "@", up to the
// caret. The tag replaces "@" and the query.
// - "[LINK:". The query is the text after "[LINK:", up to the caret. The
// tag replaces "[LINK:" and the query.
// The Link item of the insert menu writes "@" on the blank caret line, so
// the popup opens there.
//
// A query can have several words: the server matches each word separately.
// After "@", a space can also mean that the user writes plain text, for
// example "meet @ 10:00". So a query with a space that has no matches
// closes the popup. A query without a space that has no matches shows
// "No matches found".
//
// The popup is hidden until the first response arrives, so a query without
// matches never flashes an empty popup. While the popup is hidden, the keys
// work as usual.
//
// The popup is a child of <body> with a fixed position, see placeFixed()
// in field_widgets.js.
//
// Arrow keys move the selection, Enter or Tab chooses the target, Escape
// closes the popup and leaves the typed text as it is. After Escape, or
// after a query with a space finds nothing, the popup stays closed until
// the user starts another trigger.

(() => {

  const fieldWidgets = window.StrictDoc.fieldWidgets;

  const AUTOCOMPLETE_URL = '/autocomplete/link';
  // The delay in milliseconds between the last keystroke and the request.
  const REQUEST_DELAY = 150;
  const SEL_OPTION = '[role="option"]:not([aria-disabled])';
  const CLASS_ACTIVE = 'autocomplete-active';
  // The same markup as in autocompletable_field.js: keep both in sync.
  const NO_RESULTS_HTML =
    '<li class="autocompletable-result-item autocompletable-result-item_no-results" ' +
    'role="option" aria-disabled="true">No matches found</li>';

  //
  // LINK syntax.
  //

  // Returns the trigger that ends at the caret as {start, query}, or null.
  // `start` is the offset of "@" or "[LINK:" in the field text.
  // @relation(SDOC-SRS-149, scope=function)
  function findTrigger(textBefore) {
    const lineStart = textBefore.lastIndexOf('\n') + 1;
    const line = textBefore.slice(lineStart);

    const tag = line.match(/\[LINK:\s?([^[\],]*)$/);
    if (tag) return {
      start: lineStart + tag.index,
      query: tag[1]
    };

    // The query can contain spaces (see the file comment). It ends at the
    // last "@" of the line.
    const mention = line.match(/(^|\s)@([^@[\]]*)$/);
    if (mention) return {
      start: lineStart + mention.index + mention[1].length,
      query: mention[2]
    };
    return null;
  }

  // @relation(SDOC-SRS-149, scope=function)
  function linkTag(uid) {
    return `[LINK: ${uid}]`;
  }

  //
  // Popup.
  //

  // The open popup: { field, start, element, controller, timer }, or null.
  let popup = null;
  // {field, start} of the trigger closed with Escape or by a query with a
  // space that has no matches, or null. The popup does not open again for
  // this trigger while the user types after it.
  let dismissed = null;

  function dismiss() {
    dismissed = {
      field: popup.field,
      start: popup.start
    };
    closePopup();
  }

  function currentTrigger(field) {
    const textBefore = fieldWidgets.textBeforeCaret(field);
    return textBefore === null ? null : findTrigger(textBefore);
  }

  function closePopup() {
    if (!popup) return;
    clearTimeout(popup.timer);
    popup.controller?.abort();
    popup.element.remove();
    popup = null;
  }

  function options() {
    return [...popup.element.querySelectorAll(SEL_OPTION)];
  }

  function setActive(option) {
    options().forEach((item) => {
      const isActive = item === option;
      item.classList.toggle(CLASS_ACTIVE, isActive);
      item.setAttribute('aria-selected', String(isActive));
    });
    option?.scrollIntoView({
      block: 'nearest'
    });
  }

  function moveActive(step) {
    const items = options();
    if (items.length === 0) return;
    const index = items.findIndex((item) => item.classList.contains(CLASS_ACTIVE));
    setActive(items[(index + step + items.length) % items.length]);
  }

  function choose(option) {
    const {
      field,
      start
    } = popup;
    const uid = option.dataset.autocompletableValue;
    const end = fieldWidgets.textBeforeCaret(field).length;
    closePopup();
    fieldWidgets.replaceText(field, start, end, linkTag(uid));
  }

  // Puts the visible popup under the caret line.
  function placePopup() {
    const selection = window.getSelection();
    const caret = selection.rangeCount ? selection.getRangeAt(0) : null;
    const rect = caret?.getClientRects()[0] ?? popup.field.getBoundingClientRect();
    fieldWidgets.placeFixed(popup.element, rect);
  }

  function requestTargets(query) {
    clearTimeout(popup.timer);
    popup.timer = setTimeout(async () => {
      popup.controller?.abort();
      const controller = new AbortController();
      popup.controller = controller;
      const params = new URLSearchParams({
        q: query
      });
      const documentMid = popup.field.closest('form')
        ?.querySelector('[name="context_document_mid"]')?.value;
      if (documentMid) params.set('document_mid', documentMid);
      const url = `${AUTOCOMPLETE_URL}?${params}`;
      try {
        const response = await fetch(url, {
          signal: controller.signal
        });
        const html = await response.text();
        if (popup?.controller !== controller) return;
        if (!html.trim() && query.includes(' ')) {
          // The user writes plain text after "@" (see the file comment).
          dismiss();
          return;
        }
        popup.element.innerHTML = html.trim() ? html : NO_RESULTS_HTML;
        popup.element.hidden = false;
        placePopup();
        setActive(options()[0] ?? null);
      } catch (error) {
        if (error.name !== 'AbortError') throw error;
      }
    }, REQUEST_DELAY);
  }

  function openPopup(field, trigger) {
    if (popup && (popup.field !== field || popup.start !== trigger.start)) {
      closePopup();
    }
    if (!popup) {
      const element = document.createElement('ul');
      element.className = 'autocomplete-items field-widgets-link-popup';
      element.dataset.testid = 'field-widgets-link-popup';
      element.setAttribute('role', 'listbox');
      // Shown when the first response arrives (see requestTargets()).
      element.hidden = true;
      // Keep the caret in the field: choose() reads its position.
      element.addEventListener('mousedown', (event) => event.preventDefault());
      element.addEventListener('click', (event) => {
        // The table view must not see this click (see field_widgets.js).
        event.stopPropagation();
        const option = event.target.closest(SEL_OPTION);
        if (option) choose(option);
      });
      document.body.appendChild(element);
      popup = {
        field,
        start: trigger.start,
        element,
        controller: null,
        timer: null
      };
    }
    if (!popup.element.hidden) placePopup();
    requestTargets(trigger.query);
  }

  //
  // Listeners.
  //

  document.addEventListener('input', (event) => {
    const field = event.target;
    if (!fieldWidgets.hasWidget(field, 'link')) return;
    const trigger = currentTrigger(field);
    // The closed trigger is identified by its offset. Once the text before
    // the caret has no trigger at that offset (for example, the user deleted
    // the "@"), a new trigger at the same offset is a new one.
    if (dismissed && (dismissed.field !== field || trigger?.start !== dismissed.start)) {
      dismissed = null;
    }
    if (trigger && !dismissed) openPopup(field, trigger);
    else closePopup();
  });

  // The popup closes when the caret leaves the trigger. Only typing opens
  // it, so a click into old text such as an e-mail address does not.
  document.addEventListener('selectionchange', () => {
    if (!popup) return;
    const trigger = currentTrigger(popup.field);
    if (!trigger || trigger.start !== popup.start) closePopup();
  });

  // The popup keys must not reach the field or the table view, which
  // cancels the edited cell on Escape.
  document.addEventListener('keydown', (event) => {
    if (!popup || popup.element.hidden || event.target !== popup.field) return;
    if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
      moveActive(event.key === 'ArrowDown' ? 1 : -1);
    } else if (event.key === 'Enter' || event.key === 'Tab') {
      // With "No matches found", no option is active, so the key works as
      // usual in the field.
      const active = popup.element.querySelector(`.${CLASS_ACTIVE}`);
      if (!active) return;
      choose(active);
    } else if (event.key === 'Escape') {
      dismiss();
    } else {
      return;
    }
    event.preventDefault();
    event.stopPropagation();
  }, true);

  document.addEventListener('focusout', (event) => {
    if (popup && event.target === popup.field) closePopup();
  });

  // The popup has a fixed position, so it follows the caret line when the
  // page or a container scrolls, and when the window size changes.
  function replacePopup() {
    if (popup && !popup.element.hidden) placePopup();
  }
  document.addEventListener('scroll', replacePopup, true);
  window.addEventListener('resize', replacePopup);

  fieldWidgets.register({
    id: 'link',
    label: 'Link',
    supports: (markup) => markup === 'RST' || markup === 'Markdown',

    insert(field, line) {
      fieldWidgets.insertBlock(field, line, ['@']);
    },
  });

})();
