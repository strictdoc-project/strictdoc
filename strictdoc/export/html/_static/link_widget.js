// @relation(SDOC-SRS-208, scope=file)
//
// Link widget: the "link" widget of field_widgets.js. It writes a
// [LINK: <UID>] tag into an RST or Markdown field.
//
// A popup at the caret lists the link targets from /autocomplete/link:
// documents, sections, nodes, and anchors with a UID. The targets of the
// current document come first: the form's "context_document_mid" input, or
// the data-field-widgets-document-mid attribute of a field outside a form.
// The popup opens when the user types "[LINK:". The query is the text
// after "[LINK:", up to the caret. The tag replaces "[LINK:" and the
// query. The Link item of the insert menu writes "[LINK: " at the caret
// position, so the popup opens there.
//
// The query can contain "/", because a UID can contain it. So while the
// caret is after "[LINK:", the widget captures the input (capturesInput()),
// and a typed "/" does not open the insert menu. This also holds after
// Escape, while the user still types the UID.
//
// A query can have several words: the server matches each word separately.
// A query that has no matches shows "No matches found".
//
// The popup is hidden until the first response arrives, so a query without
// matches never flashes an empty popup. While the popup is hidden, the keys
// work as usual.
//
// The popup is a child of <body> with a fixed position, see placeFixed()
// in field_widgets.js.
//
// Arrow keys move the selection, Enter or Tab chooses the target, Escape
// closes the popup and leaves the typed text as it is. After Escape, the
// popup stays closed until the user starts another trigger.

(() => {

  const fieldWidgets = window.StrictDoc.fieldWidgets;

  const AUTOCOMPLETE_URL = '/autocomplete/link';
  // The delay in milliseconds between the last keystroke and the request.
  const REQUEST_DELAY = 150;

  //
  // LINK syntax.
  //

  // Returns the trigger that ends at the caret as {start, query}, or null.
  // `start` is the offset of "[LINK:" in the field text.
  // @relation(SDOC-SRS-149, scope=function)
  function findTrigger(textBefore) {
    const lineStart = textBefore.lastIndexOf('\n') + 1;
    const tag = textBefore.slice(lineStart).match(/\[LINK:\s?([^[\],]*)$/);
    return tag ? {
      start: lineStart + tag.index,
      query: tag[1]
    } : null;
  }

  // @relation(SDOC-SRS-149, scope=function)
  function linkTag(uid) {
    return `[LINK: ${uid}]`;
  }

  //
  // Popup.
  //

  // The open popup: { field, start, element, list, controller, timer }, or
  // null. `list` is the StrictDoc.autocomplete controller of `element`.
  let popup = null;
  // {field, start} of the trigger closed with Escape, or null. The popup
  // does not open again for this trigger while the user types after it.
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
    popup.list.detach();
    popup.element.remove();
    popup = null;
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
      // A field outside a form gives its document in an attribute (see
      // "Fields outside a form" in field_widgets.js).
      const documentMid = popup.field.closest('form')
        ?.querySelector('[name="context_document_mid"]')?.value ??
        popup.field.dataset.fieldWidgetsDocumentMid;
      if (documentMid) params.set('document_mid', documentMid);
      const url = `${AUTOCOMPLETE_URL}?${params}`;
      try {
        const response = await fetch(url, {
          signal: controller.signal
        });
        const html = await response.text();
        if (popup?.controller !== controller) return;
        popup.list.render(html, query);
        popup.element.hidden = false;
        placePopup();
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
      element.className = 'autocomplete field-widgets-link-popup';
      element.dataset.testid = 'field-widgets-link-popup';
      // Shown when the first response arrives (see requestTargets()).
      element.hidden = true;
      // The list keeps the caret in the field, and choose() reads its
      // position.
      const list = window.StrictDoc.autocomplete.listbox(element, field, choose);
      // The table view must not see this click (see field_widgets.js).
      element.addEventListener('click', (event) => event.stopPropagation());
      document.body.appendChild(element);
      popup = {
        field,
        start: trigger.start,
        element,
        list,
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
    // the "["), a new trigger at the same offset is a new one.
    if (dismissed && (dismissed.field !== field || trigger?.start !== dismissed.start)) {
      dismissed = null;
    }
    if (trigger && !dismissed) openPopup(field, trigger);
    else closePopup();
  });

  // The popup closes when the caret leaves the trigger. Only typing opens
  // it, so a click into an old trigger does not.
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
      popup.list.move(event.key === 'ArrowDown' ? 1 : -1);
    } else if (event.key === 'Enter' || event.key === 'Tab') {
      // With "No matches found", no option is active, so the key works as
      // usual in the field.
      const active = popup.list.active();
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
    // A LINK tag is inline text, so it fits every context, also a table cell.
    supports: (markup) => markup === 'RST' || markup === 'Markdown',
    inline: true,

    capturesInput(field) {
      return currentTrigger(field) !== null;
    },

    // "[LINK: " is a draft: the tag gets highlighted when the user chooses
    // a target.
    insert(field, offset) {
      fieldWidgets.insertInline(field, offset, '[LINK: ', {
        highlight: false
      });
    },
  });

})();
