// @relation(SDOC-SRS-61, scope=file)
//
// Table editor for the multiline fields of the node form.
//
// Supported markup: RST grid tables and Markdown (GFM) pipe tables. The
// format follows the field markup (the form's "document_markup" input);
// fields with other markup are left alone.
//
// A table is editable only when the parser understands its whole structure
// (see parseRstGridTable() and parseMarkdownPipeTable()). Anything else, for
// example an RST table with spans, is not highlighted and cannot be opened,
// so the editor never rewrites a table it has misread.
//
// While the caret is in a field, a button floats in the field's left margin:
// next to the table that holds the caret ("edit"), or next to the caret line
// ("insert"). It hides while the user types and inside table-like text that
// is not editable. Both modes open a modal that edits a copy of the table:
// cells, grips with a menu for rows and columns, insert buttons on the
// borders, and extend bars. Apply writes the serialized table back into the
// field and fires a bubbling "input" event, so editable_field.js syncs the
// hidden textarea the same way it does for typing.
//
// The CSS Custom Highlight API paints the tables in place, so there are no
// overlay elements to position or to keep away from the caret.

(() => {

  const SEL_FIELD =
    'sdoc-contenteditable[data-js-editable-field]' +
    '[data-field-type="multiline"][contenteditable="true"]';
  const HIGHLIGHT_TABLE = 'sdoc-table';
  const HIGHLIGHT_ACTIVE_TABLE = 'sdoc-table-active';
  const HAS_HIGHLIGHTS = typeof CSS !== 'undefined' && 'highlights' in CSS;

  // Editor DOM contract. The row and column indexes of cells and handles are
  // in data-row and data-column; row 0 is the header row.
  // - js-table_editor-cell marks the editable element of a cell.
  // - js-table_editor-insert marks a "+" button on a border. Its value is
  // "row" or "column"; its index is where the new row or column goes.
  // - js-table_editor-grip marks the grip of a body row or a column. Its
  // value is "row" or "column".
  // - js-table_editor-extend marks an extend bar. Its value is "row" or
  // "column".
  // - js-table_editor-menu-action marks a grip menu item. Its value is the
  // action.
  // - js-table_editor-tooltip marks a handle with a tooltip. Its value is a
  // key of TOOLTIPS.
  // - js-table_editor-icon marks an icon in the #template-table-editor-icons
  // template (components/table_editor/icons.jinja). Its value is the menu
  // action.
  const ATTR_CELL = 'js-table_editor-cell';
  const ATTR_INSERT = 'js-table_editor-insert';
  const ATTR_GRIP = 'js-table_editor-grip';
  const ATTR_EXTEND = 'js-table_editor-extend';
  const ATTR_MENU_ACTION = 'js-table_editor-menu-action';
  const ATTR_TOOLTIP = 'js-table_editor-tooltip';
  const ATTR_ICON = 'js-table_editor-icon';
  const ICON_TEMPLATE_ID = 'template-table-editor-icons';

  // A press on a grip or an extend bar that moves the pointer less than this
  // many pixels is a click.
  const DRAG_THRESHOLD = 4;
  // The distance in pixels between a tooltip and its handle or the viewport
  // edge.
  const TOOLTIP_GAP = 8;

  //
  // Shared parsing helpers.
  //

  // Parses each run of consecutive lines accepted by isCandidate(). Returns
  // the runs that parse() accepts as tables, with their line range, and the
  // rejected runs of two or more lines as blocks: table-like text that the
  // editor must neither rewrite nor insert into.
  function findTables(lines, isCandidate, parse) {
    const tables = [];
    const blocks = [];
    let start = -1;
    for (let index = 0; index <= lines.length; index++) {
      const candidate = index < lines.length && isCandidate(lines[index], index);
      if (candidate && start === -1) start = index;
      if (!candidate && start !== -1) {
        const table = parse(lines.slice(start, index));
        if (table) {
          tables.push(Object.assign(table, {
            start,
            end: index - 1
          }));
        } else if (index - start > 1) {
          blocks.push({
            start,
            end: index - 1
          });
        }
        start = -1;
      }
    }
    return {
      tables,
      blocks
    };
  }

  // Returns the indent shared by all lines, or null if they differ. A line
  // indented deeper than the others also gives null: the serializer writes
  // one indent for all lines, so such a block cannot be written back as it
  // was.
  function commonIndent(lines) {
    const indent = lines[0].match(/^ */)[0];
    return lines.every((line) => line.startsWith(indent) &&
      !/^ /.test(line.slice(indent.length))) ? indent : null;
  }

  // Splits cell text into lines without trailing spaces and without leading
  // or trailing blank lines. A cell may hold several lines and paragraphs.
  function cellLines(cell) {
    const lines = cell.split('\n').map((line) => line.trimEnd());
    while (lines.length > 1 && lines[0] === '') lines.shift();
    while (lines.length > 1 && lines[lines.length - 1] === '') lines.pop();
    return lines;
  }

  function columnWidths(rows, minWidth) {
    return rows[0].map((_, column) => Math.max(
      minWidth,
      ...rows.map((row) => Math.max(...row[column].map((line) => line.length))),
    ));
  }

  // Renders a row of cells, each given as lines, as text lines of the same
  // height.
  function renderRowLines(row, widths) {
    const height = Math.max(...row.map((lines) => lines.length));
    return Array(height).fill(null).map((_, index) => `| ${row.map(
      (lines, column) => (lines[index] ?? '').padEnd(widths[column]),
    ).join(' | ')} |`);
  }

  //
  // RST grid tables.
  //

  function rstBorder(widths, char) {
    return `+${widths.map((width) => char.repeat(width + 2)).join('+')}+`;
  }

  // Returns the number of columns of a full-width border line, or 0.
  function rstBorderColumns(line, char) {
    const pattern = char === '=' ? /^\+(=+\+)+$/ : /^\+(-+\+)+$/;
    return pattern.test(line) ? line.split('+').length - 2 : 0;
  }

  // Cuts one text line of a row into the parts of its cells. A line that is
  // still aligned with the top border is cut at the "+" positions of that
  // border, so a "|" inside a cell is plain text. A line misaligned by typing
  // is split on "|" instead, and accepted only if that gives exactly one part
  // per column: one more part means a "|" inside a cell, and then the cell
  // boundaries are ambiguous.
  function parseRstRowLine(line, edges) {
    const isAligned = line.length === edges[edges.length - 1] + 1 &&
      edges.every((edge) => line[edge] === '|');
    if (isAligned) {
      return edges.slice(1).map(
        (edge, column) => line.slice(edges[column] + 1, edge),
      );
    }
    if (!/^\|.*\|$/.test(line)) return null;
    const parts = line.slice(1, -1).split('|');
    return parts.length === edges.length - 1 ? parts : null;
  }

  // Joins the parts of a cell from the text lines of its row. The indent
  // shared by the non-blank parts is removed, so nested indents (lists,
  // directives) are kept relative to the cell.
  function rstCellText(parts) {
    const filled = parts.filter((part) => part.trim() !== '');
    const indent = Math.min(...filled.map((part) => part.match(/^ */)[0].length));
    return cellLines(parts.map((part) => part.slice(indent)).join('\n')).join('\n');
  }

  // Accepts grid tables without spans and with at most one header row. A row
  // may span several text lines, so a cell may hold several lines and
  // paragraphs. Every border must have as many columns as the top border.
  // Borders and rows do not have to be aligned (see parseRstRowLine());
  // serializing realigns them.
  function parseRstGridTable(blockLines) {
    if (blockLines.length < 3) return null;

    const indent = commonIndent(blockLines);
    if (indent === null) return null;
    const lines = blockLines.map((line) => line.slice(indent.length).trimEnd());

    const columns = rstBorderColumns(lines[0], '-');
    if (columns === 0) return null;
    const edges = [];
    for (let index = 0; index < lines[0].length; index++) {
      if (lines[0][index] === '+') edges.push(index);
    }

    let hasHeader = false;
    const rows = [];
    let rowParts = [];
    for (let index = 1; index < lines.length; index++) {
      const line = lines[index];
      const isBorder = rstBorderColumns(line, '-') === columns;
      const isHeaderBorder = rstBorderColumns(line, '=') === columns;
      if (!isBorder && !isHeaderBorder) {
        const parts = parseRstRowLine(line, edges);
        if (!parts) return null;
        rowParts.push(parts);
        continue;
      }
      if (rowParts.length === 0) return null;
      if (isHeaderBorder) {
        if (rows.length > 0 || index === lines.length - 1) return null;
        hasHeader = true;
      }
      rows.push(rowParts[0].map(
        (_, column) => rstCellText(rowParts.map((parts) => parts[column])),
      ));
      rowParts = [];
    }
    if (rowParts.length > 0) return null;

    return {
      indent,
      hasHeader,
      rows,
      align: null
    };
  }

  // An empty header row is left out: a grid table without a header is
  // valid RST.
  function serializeRstGridTable(table) {
    const hasHeader = table.hasHeader &&
      table.rows[0].some((cell) => cell.trim() !== '');
    const sourceRows = table.hasHeader && !hasHeader ? table.rows.slice(1) : table.rows;
    const rows = sourceRows.map((row) => row.map(cellLines));
    const widths = columnWidths(rows, 1);

    const lines = [rstBorder(widths, '-')];
    rows.forEach((row, index) => {
      lines.push(...renderRowLines(row, widths));
      const isHeader = hasHeader && index === 0;
      lines.push(rstBorder(widths, isHeader ? '=' : '-'));
    });
    return lines.map((line) => table.indent + line);
  }

  const RST = {
    findTables(lines) {
      return findTables(lines, (line) => /^\s*[+|]/.test(line), parseRstGridTable);
    },
    serialize: serializeRstGridTable,
  };

  //
  // Markdown (GFM) pipe tables.
  //

  const MD_DELIMITER_CELL = /^:?-+:?$/;
  // A pipe table row is one text line: line breaks inside a cell are <br>.
  const MD_LINE_BREAK = /<br\s*\/?>/gi;
  const MD_FENCE = /^ {0,3}(`{3,}|~{3,})/;

  // Splits a row on unescaped "|" and unescapes "\|" inside cells. The
  // leading and trailing pipes are optional in GFM.
  function splitPipeRow(line) {
    let text = line.trim();
    if (text.startsWith('|')) text = text.slice(1);
    if (text.endsWith('|') && !text.endsWith('\\|')) text = text.slice(0, -1);

    const cells = [];
    let cell = '';
    for (let index = 0; index < text.length; index++) {
      if (text[index] === '\\' && text[index + 1] === '|') {
        cell += '|';
        index++;
      } else if (text[index] === '|') {
        cells.push(cell.trim());
        cell = '';
      } else {
        cell += text[index];
      }
    }
    cells.push(cell.trim());
    return cells;
  }

  function parseAlign(cell) {
    const left = cell.startsWith(':');
    const right = cell.endsWith(':');
    if (left && right) return 'center';
    if (left) return 'left';
    if (right) return 'right';
    return '';
  }

  // Accepts a header row, a delimiter row, and body rows, all with the same
  // number of cells. GFM itself tolerates rows with fewer or more cells;
  // such tables are left alone instead of being "fixed" silently.
  function parseMarkdownPipeTable(blockLines) {
    if (blockLines.length < 2) return null;

    // An indent of four spaces makes an indented code block, not a table.
    const indent = commonIndent(blockLines);
    if (indent === null || indent.length > 3) return null;

    const [header, delimiter, ...body] = blockLines.map(splitPipeRow);
    if (!delimiter.every((cell) => MD_DELIMITER_CELL.test(cell))) return null;
    if (![header, ...body].every((row) => row.length === delimiter.length)) {
      return null;
    }

    return {
      indent,
      hasHeader: true,
      rows: [header, ...body].map((row) => row.map(
        (cell) => cell.replace(MD_LINE_BREAK, '\n'),
      )),
      align: delimiter.map(parseAlign),
    };
  }

  function markdownDelimiter(align, width) {
    switch (align) {
      case 'left':
        return `:${'-'.repeat(width - 1)}`;
      case 'right':
        return `${'-'.repeat(width - 1)}:`;
      case 'center':
        return `:${'-'.repeat(width - 2)}:`;
      default:
        return '-'.repeat(width);
    }
  }

  // A pipe table always has a header row; its cells may be empty.
  function serializeMarkdownPipeTable(table) {
    const rows = table.rows.map((row) => row.map(
      (cell) => [cellLines(cell).join('<br>').replaceAll('|', '\\|')],
    ));
    // Three characters fit the widest delimiter cell, ":-:".
    const widths = columnWidths(rows, 3);
    const renderRow = (row) => renderRowLines(row, widths)[0];

    const lines = [
      renderRow(rows[0]),
      renderRow(table.align.map(
        (align, column) => [markdownDelimiter(align, widths[column])],
      )),
      ...rows.slice(1).map(renderRow),
    ];
    return lines.map((line) => table.indent + line);
  }

  const MARKDOWN = {
    findTables(lines) {
      const inFence = [];
      let fence = null;
      lines.forEach((line, index) => {
        const match = line.match(MD_FENCE);
        if (fence === null && match) {
          fence = match[1][0];
          inFence[index] = true;
        } else if (fence !== null) {
          inFence[index] = true;
          if (match && match[1][0] === fence) fence = null;
        }
      });

      const isCandidate = (line, index) => !inFence[index] && line.includes('|');
      return findTables(lines, isCandidate, parseMarkdownPipeTable);
    },
    serialize: serializeMarkdownPipeTable,
  };

  const FORMATS = new Map([
    ['RST', RST],
    ['Markdown', MARKDOWN],
  ]);

  //
  // Table structure. Row 0 is the header row: it cannot be moved or
  // deleted. A table keeps at least one body row and one column. `kind` is
  // "row" or "column".
  //

  function createEmptyTable(columns, bodyRows) {
    return {
      indent: '',
      hasHeader: true,
      rows: Array(bodyRows + 1).fill(null).map(() => Array(columns).fill('')),
      align: Array(columns).fill(''),
    };
  }

  function copyTable(table) {
    return {
      ...table,
      rows: table.rows.map((row) => [...row]),
      align: table.align && [...table.align],
    };
  }

  // Returns the number of body rows or columns.
  function itemCount(table, kind) {
    return kind === 'row' ? table.rows.length - 1 : table.rows[0].length;
  }

  function lastIndex(table, kind) {
    return kind === 'row' ? table.rows.length - 1 : table.rows[0].length - 1;
  }

  function isEmptyItem(table, kind, index) {
    const cells = kind === 'row' ? table.rows[index] : table.rows.map((row) => row[index]);
    return cells.every((cell) => cell.trim() === '');
  }

  function insertItem(table, kind, index) {
    if (kind === 'row') {
      table.rows.splice(index, 0, Array(table.rows[0].length).fill(''));
    } else {
      table.rows.forEach((cells) => cells.splice(index, 0, ''));
      table.align?.splice(index, 0, '');
    }
  }

  // Returns false if the row or column cannot be deleted.
  function deleteItem(table, kind, index) {
    if (itemCount(table, kind) <= 1 || (kind === 'row' && index === 0)) {
      return false;
    }
    if (kind === 'row') {
      table.rows.splice(index, 1);
    } else {
      table.rows.forEach((cells) => cells.splice(index, 1));
      table.align?.splice(index, 1);
    }
    return true;
  }

  // Moves a row or column in front of the one at index `to`, or to the end
  // if `to` is past the last one. Returns its new index. The alignment moves
  // with its column.
  function moveItem(table, kind, from, to) {
    const at = to > from ? to - 1 : to;
    const move = (list) => list.splice(at, 0, ...list.splice(from, 1));
    if (kind === 'row') {
      move(table.rows);
    } else {
      table.rows.forEach(move);
      if (table.align) move(table.align);
    }
    return at;
  }

  //
  // Field text and DOM positions.
  //
  // The field usually holds a single text node, but typing can add more text
  // nodes and <br> elements. Text nodes and <br> are mapped to characters of
  // the field text; if the field holds anything else, its innerText (what is
  // saved) and this mapping disagree, and highlighting is skipped.
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
  // Per-field state and highlighting.
  //

  // field -> { format, button, typing, lines, offsets, segments, mapped,
  // tables, blocks }
  // typing: the caret position after the last input, or false.
  // The text fields are filled by scanField().
  const fieldStates = new Map();
  let activeField = null;

  function scanField(field) {
    const state = fieldStates.get(field);
    const text = field.innerText;
    state.lines = text.split('\n');
    state.offsets = lineOffsets(state.lines);
    state.segments = textSegments(field);
    state.mapped = segmentsText(state.segments) === text;
    ({
      tables: state.tables,
      blocks: state.blocks
    } = state.format.findTables(state.lines));
  }

  // Returns the line index of the caret, or null if the caret is not in the
  // field or the field's DOM cannot be mapped to its text.
  function caretLine(field) {
    if (!fieldStates.get(field).mapped) return null;
    const range = caretRange();
    if (!range || !field.contains(range.startContainer)) return null;

    const before = document.createRange();
    before.selectNodeContents(field);
    before.setEnd(range.startContainer, range.startOffset);
    const text = segmentsText(textSegments(before.cloneContents()));
    return text.split('\n').length - 1;
  }

  function tableAtLine(state, line, list = state.tables) {
    if (line === null) return null;
    return list.find(
      (table) => line >= table.start && line <= table.end,
    ) || null;
  }

  function tableRange(field, state, table) {
    return textRange(
      field,
      state.segments,
      state.offsets[table.start],
      state.offsets[table.end] + state.lines[table.end].length,
    );
  }

  // Returns the viewport top of a text line. A collapsed range on an empty
  // line has no rect, so the top is then derived from the closest non-empty
  // line above.
  function lineTop(field, state, line, caret) {
    const caretRect = caret?.getClientRects()[0];
    if (caretRect?.height) return caretRect.top;

    for (let above = line; above >= 0; above--) {
      const length = state.lines[above].length;
      if (length === 0) continue;
      const from = state.offsets[above] + (above === line ? 0 : length - 1);
      const rect = textRange(field, state.segments, from, from + 1)
        .getClientRects()[0];
      if (rect) return rect.top + (line - above) * rect.height;
    }
    const style = getComputedStyle(field);
    const lineHeight = parseFloat(style.lineHeight) ||
      parseFloat(style.fontSize) * 1.2;
    return field.getBoundingClientRect().top + parseFloat(style.paddingTop) +
      line * lineHeight;
  }

  function updateHighlights() {
    // Drops the fields of closed forms; nothing watches for their removal.
    for (const field of fieldStates.keys()) {
      if (!field.isConnected) fieldStates.delete(field);
    }
    if (!HAS_HIGHLIGHTS) return;

    const ranges = [];
    for (const [field, state] of fieldStates) {
      if (!state.mapped) continue;
      state.tables.forEach((table) => {
        ranges.push(tableRange(field, state, table));
      });
    }
    CSS.highlights.set(HIGHLIGHT_TABLE, new Highlight(...ranges));
  }

  function caretField() {
    const node = caretRange()?.startContainer;
    const element = node?.nodeType === Node.ELEMENT_NODE ? node : node?.parentElement;
    const field = element?.closest(SEL_FIELD) ?? null;
    return fieldStates.has(field) && field === document.activeElement ? field : null;
  }

  function hideButton(field) {
    const state = fieldStates.get(field);
    if (!state) return;
    state.button.hidden = true;
  }

  // Shows the button in the left margin of the field: next to the first line
  // of the table that holds the caret ("edit"), or next to the caret line
  // ("insert"). Returns the table that holds the caret.
  function placeButton(field) {
    const state = fieldStates.get(field);
    const line = caretLine(field);
    const table = tableAtLine(state, line);
    const {
      button
    } = state;
    // The button hides while the user types and shows up again once the
    // caret is somewhere else than where the last input left it.
    const caret = caretRange();
    if (state.typing && (caret.startContainer !== state.typing.node ||
        caret.startOffset !== state.typing.offset)) {
      state.typing = false;
    }
    if (line === null || state.typing || (!table && tableAtLine(state, line, state.blocks))) {
      button.hidden = true;
      return table;
    }

    button.dataset.mode = table ? 'edit' : 'insert';
    button.textContent = table ? '✎' : '⊞';
    button.title = table ? 'Edit table' : 'Insert table';
    button.setAttribute('aria-label', button.title);
    const top = table ?
      lineTop(field, state, table.start, null) :
      lineTop(field, state, line, caret);
    button.hidden = false;
    button.style.top = `${top - button.offsetParent.getBoundingClientRect().top}px`;
    return table;
  }

  // Updates the button and the active-table highlight for the field that
  // holds the caret.
  function updateActiveTable() {
    const field = caretField();
    if (activeField && activeField !== field) hideButton(activeField);
    activeField = field;

    let activeRange = null;
    if (activeField) {
      const table = placeButton(activeField);
      if (table) {
        activeRange = tableRange(activeField, fieldStates.get(activeField), table);
      }
    }

    if (HAS_HIGHLIGHTS) {
      CSS.highlights.set(
        HIGHLIGHT_ACTIVE_TABLE,
        activeRange ? new Highlight(activeRange) : new Highlight(),
      );
    }
  }

  //
  // Writing back to the field.
  //

  // Replaces the field content with one text node, so the caret can be set
  // by a text offset.
  function writeLines(field, lines, caretAfterLine) {
    const text = lines.join('\n');
    field.replaceChildren(document.createTextNode(text));

    field.focus();
    const caretOffset = lineOffsets(lines)[caretAfterLine] +
      lines[caretAfterLine].length;
    window.getSelection().collapse(field.firstChild, caretOffset);

    field.dispatchEvent(new Event('input', {
      bubbles: true
    }));
    // A rewrite by the editor is not typing: keep the button.
    fieldStates.get(field).typing = false;
    updateActiveTable();
  }

  function replaceTable(field, table, tableLines) {
    const {
      lines
    } = fieldStates.get(field);
    const updated = [
      ...lines.slice(0, table.start),
      ...tableLines,
      ...lines.slice(table.end + 1),
    ];
    writeLines(field, updated, table.start + tableLines.length - 1);
  }

  // Inserts the table after the caret line, or in place of it if the line is
  // blank. Blank lines separate the table from the surrounding text.
  function insertTable(field, line, tableLines) {
    const {
      lines
    } = fieldStates.get(field);

    if (lines.join('').trim() === '') {
      writeLines(field, tableLines, tableLines.length - 1);
      return;
    }

    const lineIndex = Math.min(line ?? lines.length - 1, lines.length - 1);
    const isBlank = lines[lineIndex].trim() === '';
    const before = lines.slice(0, isBlank ? lineIndex : lineIndex + 1);
    const after = lines.slice(lineIndex + 1);
    const blankBefore = before.length === 0 ||
      before[before.length - 1].trim() === '' ? [] : [''];
    const blankAfter = after.length > 0 && after[0].trim() !== '' ? [''] : [];

    const updated = [...before, ...blankBefore, ...tableLines, ...blankAfter, ...after];
    writeLines(
      field,
      updated,
      before.length + blankBefore.length + tableLines.length - 1,
    );
  }

  //
  // Editor modal.
  //

  function createButton(className, text, title, testId) {
    const button = document.createElement('button');
    button.type = 'button';
    if (className) button.className = className;
    button.textContent = text;
    if (title) {
      button.title = title;
      button.setAttribute('aria-label', title);
    }
    button.dataset.testid = testId;
    return button;
  }

  // Handles are the controls around the grid. They stay out of the Tab
  // order, so Tab moves from cell to cell.
  function createHandle(className, text, title, testId) {
    const handle = createButton(className, text, title, testId);
    handle.tabIndex = -1;
    return handle;
  }

  // A "+" button on the border between two rows or columns.
  function createInsertButton(kind, index, edge) {
    const button = createHandle(
      'table-editor-insert-button',
      '+',
      `Insert ${kind}`,
      `table-editor-insert-${kind}`,
    );
    button.setAttribute(ATTR_INSERT, kind);
    button.dataset[kind] = String(index);
    button.dataset.edge = edge;
    return button;
  }

  // The grip of a body row or a column, on the table border: dragging it
  // moves the row or column, clicking it opens its menu.
  function createGrip(kind, index) {
    const grip = createHandle(
      'table-editor-grip',
      '⠿',
      `Move or edit the ${kind}`,
      `table-editor-${kind}-grip`,
    );
    grip.setAttribute(ATTR_GRIP, kind);
    grip.dataset[kind] = String(index);
    return grip;
  }

  // Tooltip lines: [action, text]. The action is shown in bold.
  const TOOLTIPS = {
    'extend-row': [
      ['Click', 'to add a new row'],
      ['Drag', 'to add or remove rows'],
    ],
    'extend-column': [
      ['Click', 'to add a new column'],
      ['Drag', 'to add or remove columns'],
    ],
  };

  // Bars below and right of the table: a click adds a row or column at the
  // end, a drag adds or removes them (see the extend handlers). They have a
  // tooltip instead of a title, so the native title does not show up too.
  function createExtendBar(kind) {
    const tooltip = `extend-${kind}`;
    const bar = createHandle(
      'table-editor-extend-bar',
      '+',
      null,
      `table-editor-extend-${kind}s`,
    );
    bar.setAttribute(ATTR_EXTEND, kind);
    bar.setAttribute(ATTR_TOOLTIP, tooltip);
    bar.setAttribute(
      'aria-label',
      TOOLTIPS[tooltip].map((line) => `${line.join(' ')}.`).join(' '),
    );
    return bar;
  }

  // Returns a copy of the icon of a menu action, or null if the page has no
  // icon template.
  function menuIcon(action) {
    const template = document.getElementById(ICON_TEMPLATE_ID);
    const icon = template?.content.querySelector(`[${ATTR_ICON}="${action}"] svg`);
    return icon?.cloneNode(true) ?? null;
  }

  // Returns the row or column of a handle as {kind, index}.
  function handleItem(handle, attr) {
    const kind = handle.getAttribute(attr);
    return {
      kind,
      index: Number(handle.dataset[kind])
    };
  }

  // [action, label, offset]: an insert item adds a row or column at the
  // grip's index plus offset.
  const MENU_ITEMS = {
    row: [
      ['insert-above', 'Insert above', 0],
      ['insert-below', 'Insert below', 1],
      ['delete', 'Delete'],
    ],
    column: [
      ['insert-left', 'Insert left', 0],
      ['insert-right', 'Insert right', 1],
      ['delete', 'Delete'],
    ],
  };

  // Builds the modal around an empty grid. modal.js removes the
  // data-js-modal element on Escape and on a click on the
  // data-js-modal-cancel-button element.
  //
  // Why the backdrop is focusable (tabIndex -1, so it is not in the Tab
  // order):
  // A click on a part of the modal that cannot take focus, for example the
  // header, normally moves the focus to the page body. A key pressed after
  // that comes from the body, not from the modal. In the table view, this
  // breaks Escape: one press would do two things. modal.js would close the
  // modal, and table_view_edit.js would cancel the edited cell, because it
  // ignores only the keys that come from a modal. With a focusable backdrop,
  // such a click focuses the backdrop, the key comes from the modal, and
  // Escape only closes the modal.
  function createModal(title) {
    const backdrop = document.createElement('sdoc-backdrop');
    backdrop.setAttribute('data-js-modal', '');
    backdrop.className = 'table-editor-backdrop';
    backdrop.tabIndex = -1;
    backdrop.dataset.testid = 'table-editor-modal';

    const modal = document.createElement('sdoc-modal');
    modal.setAttribute('context', 'table-editor');

    const header = document.createElement('sdoc-modal-header');
    header.textContent = title;

    const content = document.createElement('sdoc-modal-content');
    const canvas = document.createElement('sdoc-table-editor-canvas');
    const grid = document.createElement('table');
    grid.className = 'table-editor-grid';
    canvas.append(grid, createExtendBar('column'), createExtendBar('row'));
    content.append(canvas);

    const footer = document.createElement('sdoc-modal-footer');
    const cancelButton = createButton(
      'action_button',
      'Cancel',
      null,
      'table-editor-cancel-action',
    );
    cancelButton.setAttribute('data-js-modal-cancel-button', '');
    cancelButton.dataset.actionType = 'cancel';
    const applyButton = createButton(
      'action_button',
      'Apply',
      null,
      'table-editor-apply-action',
    );
    applyButton.dataset.actionType = 'submit';
    footer.append(cancelButton, applyButton);

    // The tooltip is fixed to the viewport, outside the modal content, so
    // the scrolling content does not clip it.
    const tooltip = document.createElement('sdoc-table-editor-tooltip');
    tooltip.setAttribute('role', 'tooltip');
    tooltip.hidden = true;

    modal.append(header, content, footer);
    backdrop.append(modal, tooltip);
    return {
      backdrop,
      tooltip,
      canvas,
      grid,
      applyButton
    };
  }

  // Opens the modal for a copy of `table`; onApply(table) receives the
  // edited copy. The editor always shows a header row: serializing decides
  // what an empty header becomes in the format. The header row has no grip:
  // it cannot be moved or deleted, and it stays first.
  function openEditor(title, table, onApply) {
    const edited = copyTable(table);
    if (!edited.hasHeader) {
      edited.rows.unshift(Array(edited.rows[0].length).fill(''));
      edited.hasHeader = true;
    }
    const {
      backdrop,
      tooltip,
      canvas,
      grid,
      applyButton
    } = createModal(title);

    // The cell to focus after the grid is rendered again.
    let focused = {
      row: 0,
      column: 0
    };

    // The header cells and the body rows, without the handles.
    const headerCells = () => [...grid.querySelectorAll('thead th')];
    const bodyRows = () => [...grid.querySelectorAll('tbody tr')];

    // Column handles above the header; row handles left of the rows. An
    // insert button sits on the leading border of its handle; the last
    // handle also has one on its trailing border.
    function renderGrid() {
      closeMenu();
      const columns = itemCount(edited, 'column');

      const handles = document.createElement('tr');
      handles.appendChild(document.createElement('td'));
      for (let column = 0; column < columns; column++) {
        const handle = document.createElement('td');
        handle.className = 'table-editor-handle';
        handle.appendChild(createInsertButton('column', column, 'start'));
        handle.appendChild(createGrip('column', column));
        if (column === columns - 1) {
          handle.appendChild(createInsertButton('column', columns, 'end'));
        }
        handles.appendChild(handle);
      }

      const thead = document.createElement('thead');
      const tbody = document.createElement('tbody');
      thead.appendChild(handles);
      edited.rows.forEach((row, rowIndex) => {
        const isHeader = rowIndex === 0;
        const tr = document.createElement('tr');
        const handle = document.createElement('td');
        handle.className = 'table-editor-handle';
        if (!isHeader) {
          handle.appendChild(createInsertButton('row', rowIndex, 'start'));
          handle.appendChild(createGrip('row', rowIndex));
          if (rowIndex === edited.rows.length - 1) {
            handle.appendChild(createInsertButton('row', edited.rows.length, 'end'));
          }
        }
        tr.appendChild(handle);

        row.forEach((cell, columnIndex) => {
          const td = document.createElement(isHeader ? 'th' : 'td');
          td.dataset.row = String(rowIndex);
          td.dataset.column = String(columnIndex);
          // The look and the Enter behavior of the node form fields, but not
          // their data-js-editable-field handlers: a cell has no hidden
          // input to sync and no form to upload images for.
          const input = document.createElement('sdoc-contenteditable');
          input.setAttribute(ATTR_CELL, '');
          input.setAttribute('contenteditable', 'true');
          input.setAttribute('role', 'textbox');
          input.setAttribute('aria-multiline', 'true');
          input.dataset.fieldType = 'multiline';
          input.textContent = cell;
          input.dataset.testid = 'table-editor-cell';
          input.dataset.row = String(rowIndex);
          input.dataset.column = String(columnIndex);
          input.setAttribute(
            'aria-label',
            `${isHeader ? 'Header' : `Row ${rowIndex}`}, column ${columnIndex + 1}`,
          );
          td.appendChild(input);
          tr.appendChild(td);
        });
        (isHeader ? thead : tbody).appendChild(tr);
      });
      grid.replaceChildren(thead, tbody);
    }

    function focusCell() {
      grid.querySelector(
        `[${ATTR_CELL}][data-row="${focused.row}"][data-column="${focused.column}"]`,
      )?.focus();
    }

    function rerender() {
      renderGrid();
      focusCell();
    }

    // Focuses the first cell of a row, or the header cell of a column.
    function focusItem(kind, index) {
      focused = {
        row: 0,
        column: 0,
        [kind]: index
      };
    }

    function insertAt(kind, index) {
      insertItem(edited, kind, index);
      focusItem(kind, index);
      rerender();
    }

    function deleteAt(kind, index) {
      if (!deleteItem(edited, kind, index)) return;
      focusItem(kind, Math.min(index, lastIndex(edited, kind)));
      rerender();
    }

    //
    // Cells.
    //

    grid.addEventListener('input', (event) => {
      const cell = event.target.closest(`[${ATTR_CELL}]`);
      if (!cell) return;
      const {
        row,
        column
      } = cell.dataset;
      edited.rows[Number(row)][Number(column)] = cell.innerText;
    });

    // Cells take plain text only.
    grid.addEventListener('paste', (event) => {
      event.preventDefault();
      const text = event.clipboardData.getData('text/plain');
      const selection = window.getSelection();
      if (!selection.rangeCount) return;
      selection.deleteFromDocument();
      const node = document.createTextNode(text);
      selection.getRangeAt(0).insertNode(node);
      selection.collapse(node, text.length);
      event.target.dispatchEvent(new Event('input', {
        bubbles: true
      }));
    });

    grid.addEventListener('focusin', (event) => {
      const cell = event.target.closest(`[${ATTR_CELL}]`);
      if (!cell) return;
      focused = {
        row: Number(cell.dataset.row),
        column: Number(cell.dataset.column),
      };
    });

    //
    // Insert buttons.
    //

    grid.addEventListener('click', (event) => {
      const button = event.target.closest(`[${ATTR_INSERT}]`);
      if (!button) return;
      const {
        kind,
        index
      } = handleItem(button, ATTR_INSERT);
      insertAt(kind, index);
    });

    //
    // Grip menu.
    //

    let menu = null;

    function markCells(kind, index, className, isOn) {
      grid.querySelectorAll(`:is(td, th)[data-${kind}="${index}"]`).forEach(
        (cell) => cell.classList.toggle(className, isOn),
      );
    }

    function closeMenu() {
      if (!menu) return;
      markCells(menu.kind, menu.index, 'table-editor-deleting', false);
      menu.element.remove();
      menu = null;
    }

    function openMenu(grip) {
      const {
        kind,
        index
      } = handleItem(grip, ATTR_GRIP);
      const canDelete = itemCount(edited, kind) > 1;

      const element = document.createElement('sdoc-table-editor-menu');
      element.className = 'dropdown_menu';
      element.dataset.testid = 'table-editor-menu';
      element.setAttribute('role', 'menu');
      for (const [action, label] of MENU_ITEMS[kind]) {
        if (action === 'delete' && !canDelete) continue;
        const item = createButton(
          'dropdown_menu_item',
          label,
          null,
          `table-editor-menu-${action}`,
        );
        item.setAttribute('role', 'menuitem');
        item.setAttribute(ATTR_MENU_ACTION, action);
        const icon = menuIcon(action);
        if (icon) item.prepend(icon);
        element.appendChild(item);
      }
      grip.after(element);
      menu = {
        element,
        kind,
        index
      };
    }

    canvas.addEventListener('click', (event) => {
      const item = event.target.closest(`[${ATTR_MENU_ACTION}]`);
      if (!item || !menu) return;
      const {
        kind,
        index
      } = menu;
      const action = item.getAttribute(ATTR_MENU_ACTION);
      const [, , offset] = MENU_ITEMS[kind].find(([entry]) => entry === action);
      if (action === 'delete') deleteAt(kind, index);
      else insertAt(kind, index + offset);
    });

    // Marks the row or column that "Delete" would remove.
    canvas.addEventListener('pointerover', (event) => {
      if (!menu) return;
      const isDelete = event.target.closest(`[${ATTR_MENU_ACTION}="delete"]`) !== null;
      markCells(menu.kind, menu.index, 'table-editor-deleting', isDelete);
    });

    canvas.addEventListener('pointerdown', (event) => {
      if (menu && !menu.element.contains(event.target)) closeMenu();
    });

    // Escape closes the menu, not the whole editor (modal.js listens on
    // the document).
    backdrop.addEventListener('keydown', (event) => {
      if (event.key !== 'Escape' || !menu) return;
      event.stopPropagation();
      closeMenu();
    });

    //
    // Dragging a grip moves its row or column; a click without moving opens
    // the menu. The drop position is the border closest to the pointer; the
    // header row stays first. Pointer events, not HTML drag and drop, so the
    // cells keep their own text dragging.
    //

    let drag = null;

    // Returns the index the dragged row or column would be inserted at.
    function dropIndex(kind, event) {
      const targets = kind === 'row' ? bodyRows() : headerCells();
      const first = kind === 'row' ? 1 : 0;
      const index = targets.findIndex((target) => {
        const rect = target.getBoundingClientRect();
        return kind === 'row' ?
          event.clientY < rect.top + rect.height / 2 :
          event.clientX < rect.left + rect.width / 2;
      });
      return index === -1 ? first + targets.length : first + index;
    }

    function markDrop(kind, index) {
      grid.querySelectorAll('[data-drop]').forEach(
        (element) => element.removeAttribute('data-drop'),
      );
      if (index === null) return;
      const isAfter = index === lastIndex(edited, kind) + 1;
      const at = isAfter ? index - 1 : index;
      const elements = kind === 'row' ?
        grid.querySelectorAll(`tbody tr:has(> [data-row="${at}"])`) :
        grid.querySelectorAll(`:is(td, th)[data-column="${at}"]`);
      elements.forEach(
        (element) => element.setAttribute('data-drop', isAfter ? 'after' : 'before'),
      );
    }

    function endDrag() {
      if (!drag) return;
      markDrop(drag.kind, null);
      markCells(drag.kind, drag.from, 'table-editor-dragged', false);
      grid.classList.remove('table-editor-dragging');
      drag = null;
    }

    grid.addEventListener('pointerdown', (event) => {
      const grip = event.target.closest(`[${ATTR_GRIP}]`);
      if (!grip || event.button !== 0) return;
      event.preventDefault();
      const {
        kind,
        index
      } = handleItem(grip, ATTR_GRIP);
      drag = {
        grip,
        kind,
        from: index,
        x: event.clientX,
        y: event.clientY,
        isMoving: false,
        to: null,
        // A click on the grip of the open menu closes it.
        hadMenu: menu?.element.previousElementSibling === grip,
      };
      grip.setPointerCapture(event.pointerId);
    });

    grid.addEventListener('pointermove', (event) => {
      if (!drag) return;
      if (!drag.isMoving) {
        if (Math.hypot(event.clientX - drag.x, event.clientY - drag.y) < DRAG_THRESHOLD) {
          return;
        }
        drag.isMoving = true;
        grid.classList.add('table-editor-dragging');
        markCells(drag.kind, drag.from, 'table-editor-dragged', true);
      }
      drag.to = dropIndex(drag.kind, event);
      markDrop(drag.kind, drag.to);
    });

    grid.addEventListener('pointerup', () => {
      if (!drag) return;
      const {
        grip,
        kind,
        from,
        to,
        isMoving,
        hadMenu
      } = drag;
      endDrag();
      if (!isMoving) {
        if (!hadMenu) openMenu(grip);
        return;
      }
      if (to === null) return;
      const at = moveItem(edited, kind, from, to);
      if (at === from) return;
      focused[kind] = at;
      rerender();
    });

    grid.addEventListener('pointercancel', endDrag);

    //
    // Extend bars: a click adds a row or column at the end. A drag moves the
    // far edge of the table with the pointer: a row or column is added as
    // soon as the pointer passes the edge, and the last one is removed once
    // the pointer is before its start. Only empty rows and columns are
    // removed: the drag stops at the first one with content, and at the last
    // body row or column.
    //

    let extend = null;

    // Returns where the last row or column starts and ends, in viewport
    // coordinates along the extend direction.
    function lastItemSpan(kind) {
      const rect = (kind === 'row' ? bodyRows() : headerCells())
        .at(-1).getBoundingClientRect();
      return kind === 'row' ? {
        start: rect.top,
        end: rect.bottom
      } : {
        start: rect.left,
        end: rect.right
      };
    }

    function extendTo(kind, position) {
      for (;;) {
        const {
          start,
          end
        } = lastItemSpan(kind);
        const last = lastIndex(edited, kind);
        if (position > end) {
          insertItem(edited, kind, last + 1);
        } else if (position >= start || !isEmptyItem(edited, kind, last) ||
          !deleteItem(edited, kind, last)) {
          break;
        }
        renderGrid();
      }
    }

    canvas.addEventListener('pointerdown', (event) => {
      const bar = event.target.closest(`[${ATTR_EXTEND}]`);
      if (!bar || event.button !== 0) return;
      event.preventDefault();
      hideTooltip();
      const kind = bar.getAttribute(ATTR_EXTEND);
      const pointer = kind === 'row' ? event.clientY : event.clientX;
      extend = {
        kind,
        pointer,
        // The bar stands for the table edge: the drag moves the edge by
        // the pointer travel, wherever on the bar the press was.
        offset: pointer - lastItemSpan(kind).end,
        isMoving: false,
      };
      bar.setPointerCapture(event.pointerId);
    });

    canvas.addEventListener('pointermove', (event) => {
      if (!extend) return;
      const pointer = extend.kind === 'row' ? event.clientY : event.clientX;
      if (!extend.isMoving && Math.abs(pointer - extend.pointer) < DRAG_THRESHOLD) return;
      extend.isMoving = true;
      extendTo(extend.kind, pointer - extend.offset);
    });

    canvas.addEventListener('pointerup', () => {
      if (!extend) return;
      const {
        kind,
        isMoving
      } = extend;
      extend = null;
      if (!isMoving) {
        insertItem(edited, kind, lastIndex(edited, kind) + 1);
        renderGrid();
      }
      focusItem(kind, lastIndex(edited, kind));
      focusCell();
    });

    canvas.addEventListener('pointercancel', () => {
      extend = null;
    });

    //
    // Tooltips: below the handle, kept inside the viewport. No tooltip shows
    // up while a drag is in progress.
    //

    function showTooltip(target) {
      tooltip.replaceChildren(...TOOLTIPS[target.getAttribute(ATTR_TOOLTIP)].map(
        ([action, text]) => {
          const line = document.createElement('div');
          const strong = document.createElement('strong');
          strong.textContent = action;
          line.append(strong, ` ${text}`);
          return line;
        },
      ));
      tooltip.hidden = false;
      const rect = target.getBoundingClientRect();
      const left = Math.min(
        Math.max(rect.left + rect.width / 2 - tooltip.offsetWidth / 2, TOOLTIP_GAP),
        window.innerWidth - tooltip.offsetWidth - TOOLTIP_GAP,
      );
      tooltip.style.left = `${left}px`;
      tooltip.style.top = `${rect.bottom + TOOLTIP_GAP}px`;
    }

    function hideTooltip() {
      tooltip.hidden = true;
    }

    canvas.addEventListener('pointerover', (event) => {
      const target = event.target.closest(`[${ATTR_TOOLTIP}]`);
      if (target && !drag && !extend) showTooltip(target);
    });

    canvas.addEventListener('pointerout', (event) => {
      const target = event.target.closest(`[${ATTR_TOOLTIP}]`);
      if (target && !target.contains(event.relatedTarget)) hideTooltip();
    });

    applyButton.addEventListener('click', () => {
      backdrop.remove();
      onApply(edited);
    });

    renderGrid();
    document.getElementById('modal').appendChild(backdrop);
    focusCell();
  }

  //
  // Field button.
  //

  function initField(field) {
    if (fieldStates.has(field)) return;

    const markup = field.closest('form')
      ?.querySelector('[name="document_markup"]')?.value;
    const format = FORMATS.get(markup);
    if (!format) return;

    const button = createButton('table-editor-button', '', null, 'table-editor-action');
    button.hidden = true;

    // Keep the caret in the field: the click handler reads its position.
    button.addEventListener('mousedown', (event) => event.preventDefault());

    button.addEventListener('click', () => {
      scanField(field);
      const state = fieldStates.get(field);
      const line = caretLine(field);
      const table = tableAtLine(state, line);
      if (table) {
        openEditor('Edit table', table, (edited) => {
          if (!field.isConnected) return;
          replaceTable(field, table, format.serialize(edited));
        });
      } else if (!tableAtLine(state, line, state.blocks)) {
        openEditor('Insert table', createEmptyTable(3, 2), (created) => {
          if (!field.isConnected) return;
          scanField(field);
          insertTable(field, line, format.serialize(created));
        });
      }
    });

    // The hidden textarea must stay the field's next sibling:
    // editable_field.js finds it with nextElementSibling.
    (field.nextElementSibling ?? field).after(button);

    fieldStates.set(field, {
      format,
      button,
      typing: false
    });
    scanField(field);
    updateHighlights();
  }

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
    updateHighlights();
    updateActiveTable();
  });

  // Clicking the caret back to where typing stopped moves nothing.
  document.addEventListener('pointerup', (event) => {
    const state = fieldStates.get(event.target.closest?.(SEL_FIELD));
    if (!state?.typing) return;
    state.typing = false;
    updateActiveTable();
  });

  document.addEventListener('focusout', (event) => {
    if (fieldStates.has(event.target)) hideButton(event.target);
  });

  document.addEventListener('selectionchange', updateActiveTable);

})();
