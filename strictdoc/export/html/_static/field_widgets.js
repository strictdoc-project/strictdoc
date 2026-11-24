// @relation(SDOC-SRS-208, scope=file)
//
// Field widgets for the multiline fields of the node form and of the table
// view cell form, and for the cells of the table editor (see "Fields outside
// a form").
//
// A widget inserts or edits one kind of markup element, for example a
// table. Each widget is a separate script that registers itself with
// StrictDoc.fieldWidgets.register(). This script owns what the widgets
// share:
// - the field text, its lines, and the mapping of text positions to the DOM
// - the button in the field's left margin
// - the insert menu
// - writing new text back into the field.
//
// While the caret is in a field, the button shows next to a block that a
// widget can edit ("edit"), or next to a blank caret line ("insert"). It
// hides while the user types.
//
// The insert menu has one item per widget that works in the field (see
// supports() in the widget contract). It opens at the caret when the user
// clicks the insert button or types "/" anywhere in the field. The text
// typed after "/" filters the items. The arrow keys move the active item,
// Enter or Tab chooses it. While the menu is open, a placeholder marks the
// caret position. The placeholder is not part of the field text. Escape or
// the last item of the menu closes the menu and keeps the typed text. When the user chooses a widget, the menu removes the "/"
// and the filter text, and the widget inserts its element:
// - an inline widget at the caret position, with spaces around it. On a
// blank line, the element forms a new paragraph (see
// inlineFormsParagraph());
// - a block widget as a new paragraph after the block of non-blank lines
// that holds the caret. On a blank line, the element takes its place.
//
// Widget contract. Every widget has:
// - id: the widget name. It names the insert menu item, its test ID
// "field-widgets-insert-<id>", and its icon in the
// #template-field-widgets-icons template
// (components/field_widgets/icons.jinja).
// - label: the text of the insert menu item.
// - supports(markup, context): returns true if the widget works in a field
// with this markup ("RST" or "Markdown") and in this context. The context
// says where the field is:
// - "field": a multiline field of a form (the node form, the table view
// cell form).
// - "table-cell": a cell of the table editor. A cell holds the text of
// one table cell, so the widget decides by the format what fits there.
// For example, in Markdown a table cell can hold only inline text, but in
// RST a cell can also hold blocks such as lists or code.
// - insert(field, at, rect): inserts a new element. For an inline widget,
// `at` is the text offset of the caret, for a block widget, the caret
// line. `rect` is the viewport rectangle of the caret position, for a
// widget that shows its own popup there.
// - inline: true for an inline widget (see insertInline()), false or
// absent for a block widget (see insertBlock()).
// Any widget can also have these optional hooks:
// - scan(field, lines, markup): called after every change of the text of
// a field where the widget works.
// - forget(field): called when the field is no longer in the DOM, so the
// widget can drop its data about the field.
// - capturesInput(field): returns true if the text at the caret belongs to
// the widget, for example, the query of an unfinished tag. Then a typed "/"
// is part of that text and does not open the insert menu.
// A widget that recognizes its own blocks in the field text (for example,
// tables) also has:
// - blockAt(field, line): returns the block {start, end, ...} that holds
// the line, or null. The edit button shows next to the block.
// - editTitle: the title of the edit button.
// - edit(field, block): edits a block returned by blockAt().
// - activate(field, block): called on every caret move with the block
// that holds the caret, or with null. Also called with null when the field
// loses focus.
// - extraAction(field, block): optional. Returns {icon, title, run} for a
// second button under the edit button, or null. `icon` names an icon in
// the #template-field-widgets-icons template. run() is called on click.
//
// Helpers for the widgets:
// - hasWidget(field, id): returns true if the widget works in the field.
// - lineRange(field, start, end, startColumn = 0): a DOM range for the
// lines [start, end], from the column startColumn of the first line,
// or null if the field DOM cannot be mapped to its text.
// - textBeforeCaret(field): the field text before the caret, or null if
// the caret is not in the field or the field DOM cannot be mapped to its
// text.
// - insertInline(field, offset, text, options): writes the text at the
// offset, with spaces around it, or as a new paragraph (see
// inlineFormsParagraph()), and puts the caret after the text.
// - insertBlock(field, line, blockLines, options): writes the lines as a new
// paragraph after the block that holds the line, or in place of the line
// if it is blank.
// - replaceLines(field, start, end, newLines, options): writes the lines in
// place of the lines [start, end]. With the option {keepCaret: true}, the
// caret stays where the user put it, and a field without focus does not
// get it.
// - replaceText(field, from, to, text): writes the text in place of the
// characters [from, to) and puts the caret after it.
// - placeFixed(element, rect): puts a fixed element under the rect, or
// above it if there is no room below, inside the viewport.
// The helpers that write text highlight the written text for a moment (see
// highlightWritten()), because a widget writes its result, not a draft. A
// widget that writes a draft, for example, the start of a tag that the
// user completes, passes the option {highlight: false} to insertInline()
// or insertBlock().
//
// A widget popup that must not be cut by the form goes into <body> with a
// fixed position (see placeFixed()). Inside the form, the overflow of
// sdoc-form-grid would cut it: sdoc-node is a CSS container, and a
// container is the containing block of its fixed descendants. In the table
// view, a click or a key outside the edited cell saves or cancels the
// cell, so such a popup stops the propagation of its clicks and keys. The
// insert menu and the widget popups are above the modals, such as the
// table editor (z-index in the CSS of each widget).
//
// Fields outside a form. A multiline contenteditable outside a form, such
// as a cell of the table editor, gets the widgets when it has these
// attributes:
// - data-field-widgets-markup: the markup of the text ("RST" or
// "Markdown"), which a form field takes from the "document_markup" input.
// - data-field-widgets-document-mid: the document of the text, which a form
// field takes from the "context_document_mid" input (see link_widget.js).
// - data-field-widgets-context: the context for supports(), for example
// "table-cell". Without the attribute, the context is "field".
// Only a field in the "field" context has the field button. In the other
// contexts, "/" opens the insert menu.

(() => {

  // A field of a form, or a field outside a form that gives its markup in
  // data-field-widgets-markup, such as a cell of the table editor (see
  // "Fields outside a form" in the file comment).
  const SEL_FIELD =
    'sdoc-contenteditable[data-js-editable-field]' +
    '[data-field-type="multiline"][contenteditable="true"], ' +
    '[data-field-widgets-markup][contenteditable="true"]';

  // Insert menu DOM contract:
  // - js-field_widgets-insert marks an item of the insert menu. Its value is
  // the widget id.
  const ATTR_INSERT = 'js-field_widgets-insert';
  // - js-field_widgets-close marks the last item, which closes the menu.
  const ATTR_CLOSE = 'js-field_widgets-close';
  // - the class "active" marks the item that Enter chooses. It is styled by
  // .dropdown_menu_item.active in element.css.
  const CLASS_ACTIVE = 'active';
  // - js-field_widgets-icon marks an icon in the
  // #template-field-widgets-icons template. Its value is the widget id for
  // an insert menu item, "edit" for the edit button, or the `icon` of an
  // extraAction().
  const ATTR_ICON = 'js-field_widgets-icon';
  const ICON_TEMPLATE_ID = 'template-field-widgets-icons';

  // Returns a copy of the icon from the icon template, or null.
  function icon(name) {
    return document.getElementById(ICON_TEMPLATE_ID)
      ?.content.querySelector(`[${ATTR_ICON}="${name}"] svg`)?.cloneNode(true) ?? null;
  }

  // The distance in pixels between a fixed popup and its rect or the
  // viewport edge.
  const POPUP_GAP = 4;
  // The distance in pixels between the edit button and the extra button.
  const EXTRA_BUTTON_GAP = 4;

  // The highlight of the text that a widget has just written, and the
  // class that fades it (see highlightWritten()).
  const HIGHLIGHT_WRITTEN = 'field-widgets-written';
  const CLASS_WRITTEN = 'field-widgets-written';
  const HAS_HIGHLIGHTS = typeof CSS !== 'undefined' && 'highlights' in CSS;

  const widgets = [];
  const editableField = window.StrictDoc.editableField;

  //
  // Field text and DOM positions.
  //
  // The field holds text nodes and can hold <br> elements: typing and the
  // writes add them. To find a text position in the DOM, each text
  // node is mapped to its characters and each <br> to a line break. If the
  // field holds other elements, this mapping no longer matches innerText
  // (the text that is saved). Then positions in the field cannot be computed
  // reliably: the field gets no button, and lineRange() and
  // textBeforeCaret() return null, so the widgets cannot highlight or
  // write anything there.
  //

  function textSegments(root) {
    const segments = [];
    const walker = document.createTreeWalker(
      root,
      NodeFilter.SHOW_TEXT | NodeFilter.SHOW_ELEMENT,
    );
    while (walker.nextNode()) {
      const node = walker.currentNode;
      if (node.nodeType === Node.TEXT_NODE) {
        segments.push({
          node,
          text: node.nodeValue
        });
      } else if (node.nodeName === 'BR') {
        segments.push({
          node,
          text: '\n'
        });
      }
    }
    return segments;
  }

  function segmentsText(segments) {
    return segments.map((segment) => segment.text).join('');
  }

  // Returns a DOM position {node, offset} for a character offset.
  function domPosition(field, segments, charOffset) {
    let start = 0;
    for (const segment of segments) {
      const end = start + segment.text.length;
      if (charOffset <= end) {
        if (segment.node.nodeType === Node.TEXT_NODE) {
          return {
            node: segment.node,
            offset: charOffset - start
          };
        }
        const parent = segment.node.parentNode;
        const index = Array.prototype.indexOf.call(parent.childNodes, segment.node);
        return {
          node: parent,
          offset: charOffset === start ? index : index + 1
        };
      }
      start = end;
    }
    return {
      node: field,
      offset: field.childNodes.length
    };
  }

  // Returns a DOM range for the characters [from, to) of the field text.
  function textRange(field, segments, from, to) {
    const start = domPosition(field, segments, from);
    const end = domPosition(field, segments, to);
    const range = document.createRange();
    range.setStart(start.node, start.offset);
    range.setEnd(end.node, end.offset);
    return range;
  }

  function lineOffsets(lines) {
    const offsets = [];
    let offset = 0;
    for (const line of lines) {
      offsets.push(offset);
      offset += line.length + 1;
    }
    return offsets;
  }

  function caretRange() {
    const selection = window.getSelection();
    return selection?.rangeCount ? selection.getRangeAt(0) : null;
  }

  //
  // Per-field state.
  //

  // field -> { markup, context, button, extraButton, extraAction,
  // typing, lines, offsets, segments, mapped }
  // context: the context for supports(), "field" or another context (see
  // "Fields outside a form" in the file comment).
  // extraAction: the extraAction() result of the extra button, or null.
  // typing: the caret position after the last input, or false.
  // lines, offsets, segments, and mapped describe the current field text;
  // scanField() sets them after every change.
  const fieldStates = new Map();
  let activeField = null;

  // The open insert menu: { field, element, placeholder, start, offset,
  // query }, or null.
  // start: the text offset of the "/" that opened the menu, or null if the
  // insert button opened it.
  // offset: the text offset of the caret when the menu opened.
  // query: the text typed after "/".
  let menu = null;

  // Returns the widgets that work in the field (see supports()).
  function widgetsFor(field) {
    const {
      markup,
      context
    } = fieldStates.get(field);
    return widgets.filter(
      (widget) => widget.supports(markup, context),
    );
  }

  function hasWidget(field, id) {
    return fieldStates.has(field) &&
      widgetsFor(field).some((widget) => widget.id === id);
  }

  function isBlankLine(state, line) {
    return state.lines[line].trim() === '';
  }

  // Drops the fields of closed forms. Nothing watches for their removal, so
  // every scan checks the known fields.
  function forgetRemovedFields() {
    for (const known of fieldStates.keys()) {
      if (known.isConnected) continue;
      if (menu?.field === known) closeInsertMenu();
      fieldStates.delete(known);
      widgets.forEach((widget) => widget.forget?.(known));
    }
  }

  function scanField(field) {
    const state = fieldStates.get(field);
    const text = field.innerText;
    state.lines = text.split('\n');
    state.offsets = lineOffsets(state.lines);
    state.segments = textSegments(field);
    state.mapped = segmentsText(state.segments) === text;
    forgetRemovedFields();
    widgetsFor(field).forEach(
      (widget) => widget.scan?.(field, state.lines, state.markup),
    );
  }

  // See the helpers in the file comment.
  function textBeforeCaret(field) {
    if (!fieldStates.get(field)?.mapped) return null;
    const range = caretRange();
    if (!range || !field.contains(range.startContainer)) return null;

    const before = document.createRange();
    before.selectNodeContents(field);
    before.setEnd(range.startContainer, range.startOffset);
    return segmentsText(textSegments(before.cloneContents()));
  }

  // Returns the line index of the caret, or null (see textBeforeCaret()).
  function caretLine(field) {
    const text = textBeforeCaret(field);
    return text === null ? null : text.split('\n').length - 1;
  }

  // Returns the text offset of the caret, or null (see textBeforeCaret()).
  function caretOffset(field) {
    return textBeforeCaret(field)?.length ?? null;
  }

  // Returns {widget, block} for the widget block that holds the line, or
  // null.
  function blockAtLine(field, line) {
    if (line === null) return null;
    for (const widget of widgetsFor(field)) {
      const block = widget.blockAt?.(field, line);
      if (block) return {
        widget,
        block
      };
    }
    return null;
  }

  function lineRange(field, start, end, startColumn = 0) {
    const state = fieldStates.get(field);
    if (!state?.mapped) return null;
    return textRange(
      field,
      state.segments,
      state.offsets[start] + startColumn,
      state.offsets[end] + state.lines[end].length,
    );
  }

  // Returns the viewport top of a text line.
  // Uses the caret position when available; otherwise calculates the position
  // from the closest non-empty line at or above it, or from the field's top,
  // using line-height to account for empty lines.
  function lineTop(field, state, line, caret) {
    const caretRect = caret?.getClientRects()[0];
    if (caretRect?.height) return caretRect.top;

    const style = getComputedStyle(field);
    const lineHeight = parseFloat(style.lineHeight);
    for (let above = line; above >= 0; above--) {
      const length = state.lines[above].length;
      if (length === 0) continue;
      const from = state.offsets[above] + (above === line ? 0 : length - 1);
      const rect = textRange(field, state.segments, from, from + 1)
        .getClientRects()[0];
      if (rect) return rect.top + (line - above) * (lineHeight || rect.height);
    }
    return field.getBoundingClientRect().top + parseFloat(style.paddingTop) +
      line * (lineHeight || parseFloat(style.fontSize) * 1.2);
  }

  function caretField() {
    const node = caretRange()?.startContainer;
    const element = node?.nodeType === Node.ELEMENT_NODE ? node : node?.parentElement;
    const field = element?.closest(SEL_FIELD) ?? null;
    return fieldStates.has(field) && field === document.activeElement ? field : null;
  }

  //
  // Field button.
  //

  function hideButton(field) {
    const state = fieldStates.get(field);
    if (!state) return;
    state.button.hidden = true;
    state.extraButton.hidden = true;
  }

  // Shows the button in the left margin of the field: next to the first line
  // of the block that holds the caret ("edit"), or next to a blank caret line
  // ("insert"). Returns {widget, block} for the block that holds the caret,
  // or null.
  function placeButton(field) {
    const state = fieldStates.get(field);
    const line = caretLine(field);
    const found = blockAtLine(field, line);
    const {
      button
    } = state;
    // The button hides while the user types, so it does not flicker next to
    // the text the user writes. It shows up again when the caret moves away
    // from the position where the last input left it.
    const caret = caretRange();
    if (state.typing && (caret?.startContainer !== state.typing.node ||
        caret?.startOffset !== state.typing.offset)) {
      state.typing = false;
    }
    const canInsert = line !== null && isBlankLine(state, line) &&
      widgetsFor(field).length > 0;
    // Only a form field has room for the button. In the other contexts, such
    // as a cell of the table editor, the insert menu opens with "/".
    if (line === null || state.typing || state.context !== 'field' ||
      (!found && !canInsert)) {
      hideButton(field);
      return found;
    }

    button.dataset.mode = found ? 'edit' : 'insert';
    // The edit button shows the pencil icon; without the icon template, a
    // pencil character.
    if (found) button.replaceChildren(icon('edit') ?? '✎');
    else button.textContent = '+';
    button.title = found ? found.widget.editTitle : 'Insert';
    button.setAttribute('aria-label', button.title);
    const top = found ?
      lineTop(field, state, found.block.start, null) :
      lineTop(field, state, line, caret);
    button.hidden = false;
    button.style.top = `${top - button.offsetParent.getBoundingClientRect().top}px`;
    placeExtraButton(field, found);
    return found;
  }

  // Shows the button of the widget's extraAction() under the edit button,
  // or hides it.
  function placeExtraButton(field, found) {
    const state = fieldStates.get(field);
    const {
      button,
      extraButton
    } = state;
    state.extraAction = found?.widget.extraAction?.(field, found.block) ?? null;
    extraButton.hidden = state.extraAction === null;
    if (extraButton.hidden) return;
    extraButton.replaceChildren(icon(state.extraAction.icon) ?? '');
    extraButton.title = state.extraAction.title;
    extraButton.setAttribute('aria-label', state.extraAction.title);
    extraButton.style.top = `${button.offsetTop + button.offsetHeight + EXTRA_BUTTON_GAP}px`;
  }

  // Updates the button for the field that holds the caret and tells every
  // widget which of its blocks holds the caret. The insert menu closes when
  // the caret leaves the position where the menu expects it.
  function updateActiveField() {
    if (menu && caretOffset(menu.field) !== menu.offset + menu.query.length) {
      closeInsertMenu();
    }
    const field = caretField();
    if (activeField && activeField !== field) hideButton(activeField);
    activeField = field;

    const found = activeField ? placeButton(activeField) : null;
    widgets.forEach((widget) => widget.activate?.(
      activeField,
      found?.widget === widget ? found.block : null,
    ));
  }

  //
  // Insert menu.
  //

  // The placeholder splits a text node of the field, and its removal leaves
  // the parts. Both change the DOM that scanField() has mapped, so the field
  // is scanned again, or lineRange() would use the old text nodes.
  function closeInsertMenu() {
    if (!menu) return;
    const {
      field
    } = menu;
    menu.element.remove();
    menu.placeholder.remove();
    menu = null;
    if (field.isConnected) scanField(field);
  }

  function menuItems() {
    return [...menu.element.querySelectorAll(`[${ATTR_INSERT}]`)];
  }

  function setActive(item) {
    menuItems().forEach((each) => each.classList.toggle(CLASS_ACTIVE, each === item));
  }

  function moveActive(step) {
    const items = menuItems().filter((item) => !item.hidden);
    const index = items.findIndex((item) => item.classList.contains(CLASS_ACTIVE));
    setActive(items[(index + step + items.length) % items.length]);
  }

  // Shows the items with a word of the label that starts with the query.
  // The menu closes when no item matches.
  function filterInsertMenu() {
    const query = menu.query.toLowerCase();
    const items = menuItems();
    for (const item of items) {
      const id = item.getAttribute(ATTR_INSERT);
      const words = widgets.find((widget) => widget.id === id)
        .label.toLowerCase().split(/\s+/);
      item.hidden = !words.some((word) => word.startsWith(query));
    }
    const first = items.find((item) => !item.hidden);
    if (first) setActive(first);
    else closeInsertMenu();
  }

  function placeInsertMenu() {
    placeFixed(menu.element, menu.placeholder.getBoundingClientRect());
  }

  // Removes the "/" and the query, and lets the widget insert its element
  // at the caret position.
  function chooseWidget(id) {
    const {
      field,
      placeholder,
      start
    } = menu;
    const rect = placeholder.getBoundingClientRect();
    let at = menu.offset + menu.query.length;
    closeInsertMenu();
    if (start !== null) {
      replaceText(field, start, at, '');
      at = start;
    }
    const widget = widgets.find((each) => each.id === id);
    if (widget.inline) {
      widget.insert(field, at, rect);
    } else {
      widget.insert(field, field.innerText.slice(0, at).split('\n').length - 1, rect);
    }
  }

  // Opens the insert menu under the caret, or above it if there is no room
  // below. The menu is a fixed popup in <body> (see placeFixed()). The menu
  // keeps the caret in the field, so the caret position is still known when
  // an item is chosen. `start` is the text offset of the "/" that opens the
  // menu, or null.
  //
  // The placeholder at the caret is an empty element: its text comes from
  // CSS, so the field text (innerText) does not include it.
  function openInsertMenu(field, start) {
    closeInsertMenu();
    const caret = caretRange();
    const placeholder = document.createElement('sdoc-field-widgets-placeholder');
    placeholder.contentEditable = 'false';
    placeholder.dataset.testid = 'field-widgets-placeholder';
    caret.insertNode(placeholder);
    window.getSelection().collapse(caret.startContainer, caret.startOffset);
    // See closeInsertMenu().
    scanField(field);

    const element = document.createElement('sdoc-field-widgets-insert-menu');
    element.className = 'dropdown_menu';
    element.dataset.testid = 'field-widgets-insert-menu';
    element.setAttribute('role', 'menu');
    for (const widget of widgetsFor(field)) {
      const item = document.createElement('button');
      item.type = 'button';
      item.className = 'dropdown_menu_item';
      item.textContent = widget.label;
      item.dataset.testid = `field-widgets-insert-${widget.id}`;
      item.setAttribute('role', 'menuitem');
      item.setAttribute(ATTR_INSERT, widget.id);
      const itemIcon = icon(widget.id);
      if (itemIcon) item.prepend(itemIcon);
      item.addEventListener('pointerenter', () => setActive(item));
      element.appendChild(item);
    }
    const close = document.createElement('button');
    close.type = 'button';
    close.className = 'dropdown_menu_item field-widgets-menu-close';
    close.textContent = 'Close menu';
    close.dataset.testid = 'field-widgets-menu-close';
    close.setAttribute(ATTR_CLOSE, '');
    const key = document.createElement('span');
    key.className = 'field-widgets-menu-key';
    key.textContent = 'Esc';
    close.appendChild(key);
    element.appendChild(close);

    element.addEventListener('mousedown', (event) => event.preventDefault());
    element.addEventListener('click', (event) => {
      // The table view must not see this click (see placeFixed()).
      event.stopPropagation();
      const item = event.target.closest(`[${ATTR_INSERT}]`);
      if (item) chooseWidget(item.getAttribute(ATTR_INSERT));
      else if (event.target.closest(`[${ATTR_CLOSE}]`)) closeInsertMenu();
    });
    document.body.appendChild(element);
    menu = {
      field,
      element,
      placeholder,
      start,
      offset: caretOffset(field),
      query: ''
    };
    filterInsertMenu();
    placeInsertMenu();
  }

  //
  // Writing back to the field.
  //

  // Changes the field text to `text`. editable_field.js writes only the
  // changed part, so that Ctrl+Z undoes the write (see setText() there).
  //
  // `written` is the range [from, to) of the text to highlight, or null. A
  // null `caret` leaves the focus, the caret and the scroll position as they
  // are. Otherwise, the field gets the focus, and the caret goes to the
  // offset.
  function writeText(field, text, caret, written = null) {
    editableField.setText(field, text);
    // The write fires the input event, and the input listener scans the
    // field and treats the write as typing, which would hide the button. The
    // widget wrote the text, not the user, so the button stays.
    const state = fieldStates.get(field);
    state.typing = false;
    if (caret !== null) placeCaret(field, state, caret);
    if (state.mapped && written && written[0] < written[1]) {
      highlightWritten(field, textRange(field, state.segments, ...written));
    }
    updateActiveField();
  }

  // Focuses the field, puts the caret at the offset, and scrolls to the
  // caret.
  function placeCaret(field, state, caret) {
    // focus() scrolls to the field and would stop the smooth scroll of the
    // page to the caret.
    field.focus({
      preventScroll: true
    });
    if (!state.mapped) return;
    const position = domPosition(field, state.segments, caret);
    window.getSelection().collapse(position.node, position.offset);
    scrollToCaret(field, state.segments, caret);
  }

  // The browser does not scroll to a caret that a script sets, and a caret
  // has no element to scroll to. So a marker element goes next to the field,
  // over the caret line, and scrollIntoView() scrolls to the marker. The
  // marker is not in the field: a DOM change in the field ends the undo
  // history there. 'nearest' scrolls as little as possible: a caret below the
  // viewport ends up at its bottom edge, a visible caret does not scroll.
  //
  // The caret line is the line of the character at the caret, or of the one
  // before it at the end of the text. A collapsed range is not used: in
  // Firefox, its rectangle at the start of a line is at the end of the
  // previous line. The rectangle of a character is lower than the line, so
  // the marker gets the line height around it. A marker of the character
  // height leaves the bottom of the line under the edge of the viewport.
  function scrollToCaret(field, segments, caret) {
    const length = segmentsText(segments).length;
    let rect = null;
    if (caret < length) {
      rect = textRange(field, segments, caret, caret + 1).getClientRects()[0];
    }
    if (!rect?.height && caret > 0) {
      const rects = textRange(field, segments, caret - 1, caret).getClientRects();
      rect = rects[rects.length - 1];
    }
    if (!rect?.height) {
      field.scrollIntoView({
        block: 'nearest'
      });
      return;
    }
    const lineHeight = Math.max(
      rect.height,
      parseFloat(getComputedStyle(field).lineHeight) || 0,
    );
    const top = rect.top - (lineHeight - rect.height) / 2;
    const marker = document.createElement('span');
    Object.assign(marker.style, {
      position: 'absolute',
      width: '1px',
      height: `${lineHeight}px`,
      visibility: 'hidden',
      pointerEvents: 'none',
    });
    field.parentElement.append(marker);
    const parent = marker.offsetParent;
    if (parent) {
      const parentRect = parent.getBoundingClientRect();
      marker.style.top =
        `${top - parentRect.top - parent.clientTop + parent.scrollTop}px`;
      marker.style.left =
        `${rect.left - parentRect.left - parent.clientLeft + parent.scrollLeft}px`;
      marker.scrollIntoView({
        block: 'nearest'
      });
    }
    marker.remove();
  }

  // `written` is the range [start, end] of the lines to highlight, or null.
  function writeLines(field, lines, caretAfterLine, written = null) {
    const offsets = lineOffsets(lines);
    writeText(
      field,
      lines.join('\n'),
      offsets[caretAfterLine] + lines[caretAfterLine].length,
      written && [offsets[written[0]], offsets[written[1]] + lines[written[1]].length],
    );
  }

  function replaceText(field, from, to, text) {
    const current = field.innerText;
    writeText(
      field,
      current.slice(0, from) + text + current.slice(to),
      from + text.length,
      [from, from + text.length],
    );
  }

  function replaceLines(field, start, end, newLines, {
    keepCaret = false
  } = {}) {
    const {
      lines,
      offsets
    } = fieldStates.get(field);
    const updated = [
      ...lines.slice(0, start),
      ...newLines,
      ...lines.slice(end + 1),
    ];
    const last = start + newLines.length - 1;
    if (!keepCaret) {
      writeLines(field, updated, last, [start, last]);
      return;
    }
    // The caret moves with the text after the replaced lines. A caret
    // inside them goes to their end.
    const from = offsets[start];
    const to = offsets[end] + lines[end].length;
    const length = newLines.join('\n').length;
    let caret = field === document.activeElement ? caretOffset(field) : null;
    if (caret !== null && caret >= to) caret += length - (to - from);
    else if (caret !== null && caret > from) caret = from + length;
    writeText(field, updated.join('\n'), caret, [from, from + length]);
  }

  // The rule for an inline element on a blank line. Alone on a blank line
  // between two paragraphs, the element would join them into one, so it
  // forms its own paragraph, as a block does. To insert the element into a
  // blank line as is, return false.
  function inlineFormsParagraph(lines, line) {
    return lines[line].trim() === '';
  }

  // See the helpers in the file comment.
  function insertInline(field, offset, text, {
    highlight = true
  } = {}) {
    const current = field.innerText;
    const lines = current.split('\n');
    const line = current.slice(0, offset).split('\n').length - 1;
    if (inlineFormsParagraph(lines, line)) {
      insertBlock(field, line, [text], {
        highlight
      });
      return;
    }
    const spaceBefore = offset > 0 && /\S/.test(current[offset - 1]) ? ' ' : '';
    const spaceAfter = offset < current.length && /\S/.test(current[offset]) ? ' ' : '';
    const from = offset + spaceBefore.length;
    writeText(
      field,
      current.slice(0, offset) + spaceBefore + text + spaceAfter + current.slice(offset),
      from + text.length,
      highlight ? [from, from + text.length] : null,
    );
  }

  // See the helpers in the file comment. Blank lines separate the block
  // from the surrounding text.
  function insertBlock(field, line, blockLines, {
    highlight = true
  } = {}) {
    scanField(field);
    const {
      lines
    } = fieldStates.get(field);

    if (lines.join('').trim() === '') {
      const end = blockLines.length - 1;
      writeLines(field, blockLines, end, highlight ? [0, end] : null);
      return;
    }

    // A blank line is replaced. Otherwise, the block goes after the last
    // non-blank line of the block that holds the line.
    let [before, after] = [lines.slice(0, line), lines.slice(line + 1)];
    if (lines[line].trim() !== '') {
      let end = line;
      while (end + 1 < lines.length && lines[end + 1].trim() !== '') end++;
      [before, after] = [lines.slice(0, end + 1), lines.slice(end + 1)];
    }
    const blankBefore = before.length === 0 ||
      before[before.length - 1].trim() === '' ? [] : [''];
    const blankAfter = after.length > 0 && after[0].trim() !== '' ? [''] : [];

    const updated = [...before, ...blankBefore, ...blockLines, ...blankAfter, ...after];
    const start = before.length + blankBefore.length;
    const end = start + blockLines.length - 1;
    writeLines(field, updated, end, highlight ? [start, end] : null);
  }

  // Highlights the range of the field for a moment. The
  // ::highlight() pseudo-element cannot be animated, so the class
  // CLASS_WRITTEN animates the custom property
  // --field-widgets-written-alpha of the field, and the highlight takes its
  // color from the property (see field_widgets.css). When the animation
  // ends, the highlight is removed.
  function highlightWritten(field, range) {
    if (!HAS_HIGHLIGHTS) return;
    const highlight = new Highlight(range);
    // Above the table highlights of table_editor.js.
    highlight.priority = 1;
    CSS.highlights.set(HIGHLIGHT_WRITTEN, highlight);
    // A new write restarts the animation.
    field.classList.remove(CLASS_WRITTEN);
    void field.offsetWidth;
    field.classList.add(CLASS_WRITTEN);
  }

  // See the helpers in the file comment.
  function placeFixed(element, rect) {
    const width = element.offsetWidth;
    const height = element.offsetHeight;

    const maxLeft = window.innerWidth - width - POPUP_GAP;
    const left = Math.max(POPUP_GAP, Math.min(rect.left, maxLeft));
    const below = rect.bottom + POPUP_GAP;
    const above = rect.top - POPUP_GAP - height;
    const fitsBelow = below + height <= window.innerHeight - POPUP_GAP;
    const top = fitsBelow || above < POPUP_GAP ? below : above;

    element.style.left = `${left}px`;
    element.style.top = `${top}px`;
  }

  //
  // Fields and listeners.
  //

  function initField(field) {
    if (fieldStates.has(field)) return;

    const markup = field.dataset.fieldWidgetsMarkup ?? field.closest('form')
      ?.querySelector('[name="document_markup"]')?.value;
    if (!markup) return;

    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'field-widgets-button';
    button.dataset.testid = 'field-widgets-button';
    button.hidden = true;

    // Keep the caret in the field: the click handler reads its position.
    button.addEventListener('mousedown', (event) => event.preventDefault());

    button.addEventListener('click', () => {
      scanField(field);
      const state = fieldStates.get(field);
      const line = caretLine(field);
      const found = blockAtLine(field, line);
      if (found) {
        found.widget.edit(field, found.block);
      } else if (menu?.field === field) {
        closeInsertMenu();
      } else if (line !== null && isBlankLine(state, line)) {
        openInsertMenu(field, null);
      }
    });

    // The button of the widget's extraAction() (see placeExtraButton()).
    const extraButton = document.createElement('button');
    extraButton.type = 'button';
    extraButton.className = 'field-widgets-button';
    extraButton.dataset.testid = 'field-widgets-extra-button';
    extraButton.hidden = true;
    extraButton.addEventListener('mousedown', (event) => event.preventDefault());
    extraButton.addEventListener('click', () => fieldStates.get(field).extraAction?.run());

    // The hidden input must stay the field's next sibling:
    // editable_field.js finds it with nextElementSibling.
    (field.nextElementSibling ?? field).after(button, extraButton);

    fieldStates.set(field, {
      markup,
      context: field.dataset.fieldWidgetsContext ?? 'field',
      button,
      extraButton,
      extraAction: null,
      typing: false
    });
    scanField(field);
  }

  // A widget script can load after the fields are initialized, so a new
  // widget scans the fields that already exist.
  function register(widget) {
    widgets.push(widget);
    for (const [field, state] of fieldStates) {
      if (field.isConnected && widget.supports(state.markup, state.context)) {
        widget.scan?.(field, state.lines, state.markup);
      }
    }
  }

  window.StrictDoc.fieldWidgets = {
    register,
    hasWidget,
    lineRange,
    textBeforeCaret,
    insertInline,
    insertBlock,
    replaceLines,
    replaceText,
    placeFixed,
  };

  window.StrictDoc.onInsert(SEL_FIELD, initField);

  document.addEventListener('input', (event) => {
    const field = event.target.closest?.(SEL_FIELD);
    if (!fieldStates.has(field)) return;
    const range = caretRange();
    fieldStates.get(field).typing = range && {
      node: range.startContainer,
      offset: range.startOffset
    };
    scanField(field);
    updateInsertMenu(field, event);
    updateActiveField();
  });

  // Typing closes the menu of the insert button. In the menu of "/", the
  // typed text is the query. A "/" typed into the field opens the menu,
  // unless a widget captures the input (see capturesInput() in the file
  // comment).
  function updateInsertMenu(field, event) {
    if (menu?.field === field) {
      const before = menu.start === null ? null : textBeforeCaret(field);
      const query = before !== null && before.length > menu.start &&
        before[menu.start] === '/' ? before.slice(menu.start + 1) : null;
      if (query === null || /\s/.test(query)) {
        closeInsertMenu();
      } else {
        menu.query = query;
        filterInsertMenu();
      }
    }
    const available = widgetsFor(field);
    if (!menu && event.inputType === 'insertText' && event.data === '/' &&
      available.length > 0 && !available.some((widget) => widget.capturesInput?.(field))) {
      const offset = caretOffset(field);
      if (offset !== null) openInsertMenu(field, offset - 1);
    }
  }

  // After typing, the button comes back when the caret moves (see
  // placeButton()). A click at the position where typing stopped does not
  // move the caret, so no selectionchange event fires. The click itself then
  // brings the button back.
  document.addEventListener('pointerup', (event) => {
    const state = fieldStates.get(event.target.closest?.(SEL_FIELD));
    if (!state?.typing) return;
    state.typing = false;
    updateActiveField();
  });

  document.addEventListener('pointerdown', (event) => {
    if (menu && !menu.element.contains(event.target) &&
      !fieldStates.get(menu.field).button.contains(event.target)) closeInsertMenu();
  });

  // The menu keys must not reach the field or the table view, which cancels
  // the edited cell on Escape. The arrow keys left and right close the menu,
  // so the caret does not move past the placeholder.
  document.addEventListener('keydown', (event) => {
    if (!menu || event.target !== menu.field) return;
    if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
      moveActive(event.key === 'ArrowDown' ? 1 : -1);
    } else if (event.key === 'Enter' || event.key === 'Tab') {
      const active = menu.element.querySelector(`.${CLASS_ACTIVE}`);
      chooseWidget(active.getAttribute(ATTR_INSERT));
    } else if (event.key === 'Escape') {
      closeInsertMenu();
    } else {
      if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') closeInsertMenu();
      return;
    }
    event.preventDefault();
    event.stopPropagation();
  }, true);

  // The widgets learn that the caret has left the field: during focusout,
  // the field is not the active element, so updateActiveField() passes null
  // to activate().
  document.addEventListener('focusout', (event) => {
    if (!fieldStates.has(event.target)) return;
    if (menu?.field === event.target) closeInsertMenu();
    hideButton(event.target);
    updateActiveField();
  });

  // The insert menu has a fixed position, so it follows the placeholder
  // when the page or a container scrolls, and when the window size changes.
  function replaceInsertMenu() {
    if (menu) placeInsertMenu();
  }
  document.addEventListener('scroll', replaceInsertMenu, true);
  window.addEventListener('resize', replaceInsertMenu);

  document.addEventListener('animationend', (event) => {
    if (event.animationName !== CLASS_WRITTEN) return;
    event.target.classList.remove(CLASS_WRITTEN);
    CSS.highlights.delete(HIGHLIGHT_WRITTEN);
  });

  document.addEventListener('selectionchange', updateActiveField);

})();
