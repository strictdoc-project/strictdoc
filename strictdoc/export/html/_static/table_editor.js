// @relation(SDOC-SRS-61, scope=file)
//
// Table editor: the "table" widget of field_widgets.js.
//
// Supported markup: RST grid tables and Markdown (GFM) pipe tables. The
// format follows the field markup; fields with other markup have no table
// editor.
//
// A table is editable only when the parser understands its whole structure
// (see parseRstGridTable() and parseMarkdownPipeTable()). Anything else, for
// example an RST table with spans, is not highlighted and cannot be opened,
// so the editor never rewrites a table it has misread.
//
// The field button edits the table that holds the caret. The insert menu
// inserts a new table. Both open a modal that edits a copy of the table:
// cells, grips with a menu for rows and columns, insert buttons on the
// borders, and extend bars. Apply writes the serialized table back into the
// field through field_widgets.js. The cells take the field widgets that
// work in a table cell, such as Link (see cellWidgetContext()).
//
// The CSS Custom Highlight API paints the tables in place, so there are no
// overlay elements to position or to keep away from the caret.
//
// Alignment. A table is aligned when its cell separators stand at the same
// positions in all lines: "|" in the rows, and also "+" in the borders of
// an RST table (the `aligned` flag of the parsers). A table with columns
// wider than their text is aligned too. A misaligned table is still
// editable, but RST rejects it ("Malformed table"), and in Markdown it is
// only harder to read. So:
// - Under the edit button of a misaligned table, the Format table button
// aligns it: it writes the table the same way as Apply of the editor.
// - An RST table that the user or a widget has changed is aligned
// automatically when the caret leaves the table or the field loses focus.
// Only a changed table is aligned, so a table that the user only passes
// through stays as it is. It is not aligned while the caret is in it: a
// widget may still be writing there, for example, the "[LINK: " draft and
// its popup. Markdown tables are not aligned automatically.

(() => {

  const HIGHLIGHT_TABLE = 'sdoc-table';
  const HIGHLIGHT_ACTIVE_TABLE = 'sdoc-table-active';
  // A Markdown table with more cells in a row than in the header (see
  // parseMarkdownPipeTable()), and, on top of it, the extra cells of such
  // rows. These highlights are above the other two.
  const HIGHLIGHT_OVERFLOW_TABLE = 'sdoc-table-overflow';
  const HIGHLIGHT_OVERFLOW_CELLS = 'sdoc-table-overflow-cells';
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
  // template (components/table_editor/icons.jinja). Its value is a grip
  // menu action.
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
  // the runs that parse() accepts as tables, with their line range.
  function findTables(lines, isCandidate, parse) {
    const tables = [];
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
        }
        start = -1;
      }
    }
    return tables;
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

  // The width of text. A wide or full-width East Asian character, for
  // example, a CJK character or an emoji, takes the width of two characters.
  // Every other character takes the width of one character, also a character
  // outside the BMP. Docutils measures a grid table in this way
  // (docutils.statemachine.StringList.pad_double_width()). The Markdown
  // tables use the same measure, so a table looks aligned in a monospace
  // font. The format command measures text in the same way
  // (strictdoc/helpers/text_width.py).
  //
  // Docutils takes the width of a character from the unicodedata module of
  // the Python on the server. The server writes the code point ranges of the
  // double-width characters from the same module into the page
  // (components/table_editor/double_width_ranges.jinja), as [first, last]
  // pairs in ascending order. The page has the element only when the server
  // renders it, and the table editor works only there.
  const DOUBLE_WIDTH_RANGES_ID = 'table-editor-double-width-ranges';
  let doubleWidthRanges = null;

  // Reads the ranges at the first use: the script runs before the page body
  // with the element is parsed.
  function getDoubleWidthRanges() {
    if (doubleWidthRanges === null) {
      const element = document.getElementById(DOUBLE_WIDTH_RANGES_ID);
      if (!element) throw new Error(`table_editor.js: no #${DOUBLE_WIDTH_RANGES_ID}`);
      doubleWidthRanges = JSON.parse(element.textContent);
    }
    return doubleWidthRanges;
  }

  function isWideCodePoint(codePoint) {
    const ranges = getDoubleWidthRanges();
    let low = 0;
    let high = ranges.length - 1;
    while (low <= high) {
      const middle = (low + high) >> 1;
      const [first, last] = ranges[middle];
      if (codePoint < first) high = middle - 1;
      else if (codePoint > last) low = middle + 1;
      else return true;
    }
    return false;
  }

  // A pad item after a wide character in textPositions().
  const DOUBLE_WIDTH_PAD = '\0';

  // Splits a line into its positions: one item per character, and a pad item
  // after each wide character. The index of an item is its position in the
  // line, measured in text width.
  function textPositions(line) {
    const positions = [];
    for (const char of line) {
      positions.push(char);
      if (isWideCodePoint(char.codePointAt(0))) positions.push(DOUBLE_WIDTH_PAD);
    }
    return positions;
  }

  function textWidth(line) {
    return textPositions(line).length;
  }

  function columnWidths(rows, minWidth) {
    return rows[0].map((_, column) => Math.max(
      minWidth,
      ...rows.map((row) => Math.max(...row[column].map(textWidth))),
    ));
  }

  // Renders a row of cells, each given as lines, as text lines of the same
  // height.
  function renderRowLines(row, widths) {
    const height = Math.max(...row.map((lines) => lines.length));
    return Array(height).fill(null).map((_, index) => `| ${row.map((lines, column) => {
      const line = lines[index] ?? '';
      return line + ' '.repeat(widths[column] - textWidth(line));
    }).join(' | ')} |`);
  }

  //
  // RST grid tables.
  //
  // Docutils finds the cell borders of a grid table by the positions of "|"
  // and "+" in the lines, so the parser works on the lines split by
  // textPositions().
  //

  function rstBorder(widths, char) {
    return `+${widths.map((width) => char.repeat(width + 2)).join('+')}+`;
  }

  // Returns true if the line, given as positions (see textPositions()), has
  // `char` at every column edge and ends at the last edge.
  function isAlignedRstLine(positions, edges, char) {
    return positions.length === edges[edges.length - 1] + 1 &&
      edges.every((edge) => positions[edge] === char);
  }

  // Returns the number of columns of a full-width border line, or 0.
  function rstBorderColumns(line, char) {
    const pattern = char === '=' ? /^\+(=+\+)+$/ : /^\+(-+\+)+$/;
    return pattern.test(line) ? line.split('+').length - 2 : 0;
  }

  // Cuts one text line of a row into the parts of its cells. A line that is
  // still aligned with the top border is cut at the "+" positions of that
  // border, so a "|" inside a cell is plain text. A line misaligned by typing
  // cannot be cut by positions, so it is split on "|" instead. That split is
  // accepted only if it gives exactly one part per column. More parts mean
  // that some cell contains a "|", and then it is unclear where the cells
  // end.
  function parseRstRowLine(positions, edges) {
    if (isAlignedRstLine(positions, edges, '|')) {
      return edges.slice(1).map(
        (edge, column) => positions.slice(edges[column] + 1, edge).join(''),
      );
    }
    const line = positions.join('');
    if (!/^\|.*\|$/.test(line)) return null;
    const parts = line.slice(1, -1).split('|');
    return parts.length === edges.length - 1 ? parts : null;
  }

  // Joins the parts of a cell from the text lines of its row. The indent
  // shared by the non-blank parts is removed, so nested indents (lists,
  // directives) are kept relative to the cell. The pad items after the wide
  // characters (see textPositions()) are removed too.
  function rstCellText(parts) {
    const filled = parts.filter((part) => part.trim() !== '');
    const indent = Math.min(...filled.map((part) => part.match(/^ */)[0].length));
    const text = parts.map((part) => part.slice(indent)).join('\n');
    return cellLines(text.replaceAll(DOUBLE_WIDTH_PAD, '')).join('\n');
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
    // Each line as positions (see textPositions()).
    const lines = blockLines.map((line) => textPositions(line.slice(indent.length).trimEnd()));

    const columns = rstBorderColumns(lines[0].join(''), '-');
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
      const isBorder = rstBorderColumns(line.join(''), '-') === columns;
      const isHeaderBorder = rstBorderColumns(line.join(''), '=') === columns;
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
      align: null,
      // See "Alignment" in the file comment.
      aligned: lines.every((line) => isAlignedRstLine(line, edges, '+') ||
        isAlignedRstLine(line, edges, '|')),
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

  // The table rules follow the table rule of markdown-it, which renders
  // Markdown in StrictDoc (markdown_it/rules_block/table.py, after GFM):
  // - A table starts with a header row that contains "|" and a delimiter
  // row with the same number of cells. The table can interrupt a
  // paragraph: the paragraph lines above the header are not part of it.
  // - Every following line is a row, even without "|", up to a blank line,
  // a line indented by four or more spaces (code), or the start of another
  // block (MD_BLOCK_STARTS).
  // - A row can have fewer cells than the header: the missing cells are
  // empty. A row can have more cells: markdown-it does not show the extra
  // cells. The editor keeps them in added columns, so it never deletes
  // text, and such a table gets the overflow highlight.
  const MD_DELIMITER_CELL = /^:?-+:?$/;
  // A delimiter row has only "|", "-", ":", and spaces. A row that starts
  // with "-" and a space is a list item.
  const MD_DELIMITER_ROW = /^[|:-][|:\- \t]*$/;
  // A pipe table row is one text line: line breaks inside a cell are <br>.
  const MD_LINE_BREAK = /<br\s*\/?>/gi;
  const MD_FENCE = /^ {0,3}(`{3,}|~{3,})/;
  // The HTML block names of markdown-it (common/html_blocks.py).
  const MD_HTML_BLOCK_NAMES = 'address|article|aside|base|basefont|blockquote|body|caption|' +
    'center|col|colgroup|dd|details|dialog|dir|div|dl|dt|fieldset|figcaption|figure|' +
    'footer|form|frame|frameset|h1|h2|h3|h4|h5|h6|head|header|hr|html|iframe|legend|li|' +
    'link|main|menu|menuitem|nav|noframes|ol|optgroup|option|p|param|search|section|' +
    'summary|table|tbody|td|tfoot|th|thead|title|tr|track|ul';
  // The starts of the blocks that end a table, tested on a line without
  // its indent: fence, blockquote, thematic break, list item, heading, and
  // the HTML blocks that can end a paragraph.
  const MD_BLOCK_STARTS = [
    /^(`{3,}|~{3,})/,
    /^>/,
    /^([-*_])([ \t]*\1){2,}[ \t]*$/,
    /^([-*+]|\d{1,9}[.)])([ \t]|$)/,
    /^#{1,6}([ \t]|$)/,
    /^<(script|pre|style|textarea)(?=(\s|>|$))/i,
    /^<!--/,
    /^<\?/,
    /^<![A-Z]/,
    /^<!\[CDATA\[/,
    new RegExp(`^</?(${MD_HTML_BLOCK_NAMES})(?=(\\s|/?>|$))`, 'i'),
  ];

  function indentOf(line) {
    return line.match(/^ */)[0].length;
  }

  function isDelimiterRow(line) {
    const text = line.trim();
    return indentOf(line) < 4 && MD_DELIMITER_ROW.test(text) && !/^-[ \t]/.test(text);
  }

  // Returns true if the line continues a table (see the rules above).
  function isTableRow(line) {
    const text = line.trimStart();
    return text !== '' && indentOf(line) < 4 &&
      !MD_BLOCK_STARTS.some((start) => start.test(text));
  }

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

  // Returns the positions of the unescaped "|" in a line, as string
  // indexes.
  function pipePositions(line) {
    const positions = [];
    for (let index = 0; index < line.length; index++) {
      if (line[index] === '\\' && line[index + 1] === '|') index++;
      else if (line[index] === '|') positions.push(index);
    }
    return positions;
  }

  // Returns the positions of the unescaped "|" in a line, measured in text
  // width (see textWidth()).
  function pipeTextPositions(line) {
    return pipePositions(line).map((index) => textWidth(line.slice(0, index)));
  }

  function parseAlign(cell) {
    const left = cell.startsWith(':');
    const right = cell.endsWith(':');
    if (left && right) return 'center';
    if (left) return 'left';
    if (right) return 'right';
    return '';
  }

  // Parses the lines of one table: a header row, a delimiter row, and body
  // rows (see the rules above). Returns null if the header and the
  // delimiter row do not make a table. The rows are padded with empty cells
  // to the widest row, so the table model has the same number of cells in
  // every row. The added columns are not aligned.
  function parseMarkdownPipeTable(blockLines) {
    const [header, delimiter, ...body] = blockLines.map(splitPipeRow);
    if (!delimiter.every((cell) => MD_DELIMITER_CELL.test(cell))) return null;
    if (header.length !== delimiter.length) return null;

    const columns = Math.max(header.length, ...body.map((row) => row.length));
    // The extra cells of a row start after the "|" that ends its last
    // header-wide cell. The leading "|" of a row is optional.
    const overflowCells = [];
    body.forEach((row, index) => {
      if (row.length <= header.length) return;
      const line = blockLines[index + 2];
      const leading = line.trimStart().startsWith('|') ? 1 : 0;
      overflowCells.push({
        line: index + 2,
        column: pipePositions(line)[header.length - 1 + leading] + 1,
      });
    });
    const pad = (cells, value) => [...cells, ...Array(columns - cells.length).fill(value)];
    return {
      // The serializer writes all lines with the indent of the header.
      indent: ' '.repeat(indentOf(blockLines[0])),
      hasHeader: true,
      rows: [header, ...body].map((row) => pad(row, '').map(
        (cell) => cell.replace(MD_LINE_BREAK, '\n'),
      )),
      align: pad(delimiter.map(parseAlign), ''),
      // A row with more cells than the header: markdown-it does not show
      // the extra cells. overflowCells: {line, column} where the extra cells
      // of a row start; `line` counts from the header row.
      overflow: columns > header.length,
      overflowCells,
      // See "Alignment" in the file comment.
      aligned: blockLines.every(
        (line) => pipeTextPositions(line).join() === pipeTextPositions(blockLines[0]).join(),
      ),
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

      const tables = [];
      let start = 0;
      while (start < lines.length - 1) {
        const isStart = !inFence[start] && !inFence[start + 1] &&
          indentOf(lines[start]) < 4 && lines[start].includes('|') &&
          isDelimiterRow(lines[start + 1]);
        let end = start + 2;
        while (isStart && end < lines.length && !inFence[end] && isTableRow(lines[end])) end++;
        const table = isStart && parseMarkdownPipeTable(lines.slice(start, end));
        if (!table) {
          start++;
          continue;
        }
        tables.push(Object.assign(table, {
          start,
          end: end - 1
        }));
        start = end;
      }
      return tables;
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

  // Returns a copy of the icon of a menu item, or null if the page has no
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

  // The cells of the editor are fields of field_widgets.js in the
  // "table-cell" context. Each widget decides in supports() if it works in a
  // cell. The widgets also need the markup and the document of the field
  // (see "Fields outside a form" in field_widgets.js).
  function cellWidgetContext(field) {
    return {
      markup: fieldTables.get(field).markup,
      documentMid: field.closest('form')
        ?.querySelector('[name="context_document_mid"]')?.value ?? '',
    };
  }

  // Opens the modal for a copy of `table`; onApply(table) receives the
  // edited copy. The editor always shows a header row: serializing decides
  // what an empty header becomes in the format. The header row has no grip:
  // it cannot be moved or deleted, and it stays first. `widgetContext` comes
  // from cellWidgetContext().
  function openEditor(title, table, onApply, widgetContext) {
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
          input.dataset.fieldWidgetsMarkup = widgetContext.markup;
          input.dataset.fieldWidgetsDocumentMid = widgetContext.documentMid;
          input.dataset.fieldWidgetsContext = 'table-cell';
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

    // Cells take plain text only, so that pasted formatting does not end up
    // as HTML elements in a cell. The write can be undone with Ctrl+Z and
    // fires the 'input' event (see editable_field.js).
    grid.addEventListener('paste', (event) => {
      const cell = event.target.closest(`[${ATTR_CELL}]`);
      if (!cell) return;
      event.preventDefault();
      const text = event.clipboardData.getData('text/plain');
      const selected = editableField.textSelection(cell);
      if (selected) editableField.writeText(cell, selected.from, selected.to, text);
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

    // When the menu is open, Escape closes only the menu. modal.js closes the
    // whole editor on Escape from its listener on the document, so the event
    // must not get there.
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
      const last = (kind === 'row' ? bodyRows() : headerCells()).at(-1) ??
        headerCells().at(-1);
      const rect = last.getBoundingClientRect();
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
  // Widget.
  //

  const fieldWidgets = window.StrictDoc.fieldWidgets;
  const editableField = window.StrictDoc.editableField;

  // field -> { markup, format, tables } for the fields with a table format.
  const fieldTables = new Map();

  function updateHighlights() {
    if (!HAS_HIGHLIGHTS) return;

    const ranges = [];
    const overflowRanges = [];
    const overflowCellRanges = [];
    for (const [field, entry] of fieldTables) {
      entry.tables.forEach((table) => {
        const range = fieldWidgets.lineRange(field, table.start, table.end);
        if (!range) return;
        if (!table.overflow) {
          ranges.push(range);
          return;
        }
        overflowRanges.push(range);
        for (const cells of table.overflowCells) {
          const line = table.start + cells.line;
          overflowCellRanges.push(fieldWidgets.lineRange(field, line, line, cells.column));
        }
      });
    }
    CSS.highlights.set(HIGHLIGHT_TABLE, new Highlight(...ranges));
    // The two overflow highlights are translucent, so the extra cells, which
    // have both, look denser than the rest of the table.
    const overflow = new Highlight(...overflowRanges);
    overflow.priority = 1;
    CSS.highlights.set(HIGHLIGHT_OVERFLOW_TABLE, overflow);
    const overflowCells = new Highlight(...overflowCellRanges);
    overflowCells.priority = 2;
    CSS.highlights.set(HIGHLIGHT_OVERFLOW_CELLS, overflowCells);
  }

  //
  // Alignment (see the file comment).
  //

  // The table that holds the caret: { field, start, changed }, or null.
  // changed: the field text changed while the caret was in the table.
  let editing = null;
  // True while the widget writes an aligned table, so that this write does
  // not count as a change of the table.
  let aligning = false;
  // The field of the 'input' event that field_widgets.js handles now, or
  // null.
  let inputField = null;

  function writeAligned(field, table, options) {
    const {
      format
    } = fieldTables.get(field);
    aligning = true;
    try {
      fieldWidgets.replaceLines(
        field, table.start, table.end, format.serialize(table), options,
      );
    } finally {
      aligning = false;
    }
  }

  // Aligns the changed RST table that starts at the line `start`, if it is
  // still a misaligned table. The caret stays where the user put it.
  function alignChangedTable(field, start) {
    const state = fieldTables.get(field);
    if (!field.isConnected || state?.format !== RST) return;
    const table = state.tables.find((each) => each.start === start);
    if (table && !table.aligned) {
      writeAligned(field, table, {
        keepCaret: true
      });
    }
  }

  // Follows the table that holds the caret. When the caret leaves a changed
  // table, the table is aligned after the current event: the caret move
  // comes from field_widgets.js, which must finish its own update first.
  function followCaret(field, table) {
    if (editing && (editing.field !== field || editing.start !== table?.start)) {
      const left = editing;
      editing = null;
      if (left.changed) queueMicrotask(() => alignChangedTable(left.field, left.start));
    }
    if (table && !editing) {
      editing = {
        field,
        start: table.start,
        // A write puts the caret after the written text, so a table that
        // gets the caret with a write is changed by it, for example, by an
        // undo with the caret outside the table.
        changed: inputField === field
      };
    }
  }

  // Any write into the field while the caret is in a table changes the
  // table: typing, paste, undo, and the writes of the widgets. The listener
  // runs in the capture phase, before field_widgets.js moves the caret
  // state on the same input.
  document.addEventListener('input', (event) => {
    if (aligning) return;
    if (editing?.field === event.target) editing.changed = true;
    inputField = event.target;
  }, true);

  // This script runs after field_widgets.js, so its listener comes after the
  // one of field_widgets.js.
  document.addEventListener('input', () => {
    inputField = null;
  });

  fieldWidgets.register({
    id: 'table',
    label: 'Table',
    editTitle: 'Edit table',
    // The editor does not support nested tables, so the widget works only in
    // a form field, not in a cell of its own editor.
    supports: (markup, context) => context === 'field' && FORMATS.has(markup),

    scan(field, lines, markup) {
      const format = FORMATS.get(markup);
      fieldTables.set(field, {
        markup,
        format,
        tables: format.findTables(lines)
      });
      updateHighlights();
    },

    forget(field) {
      fieldTables.delete(field);
      if (editing?.field === field) editing = null;
      updateHighlights();
    },

    blockAt(field, line) {
      return fieldTables.get(field)?.tables.find(
        (table) => line >= table.start && line <= table.end,
      ) ?? null;
    },

    activate(field, table) {
      followCaret(field, table);
      if (!HAS_HIGHLIGHTS) return;
      const range = table && fieldWidgets.lineRange(field, table.start, table.end);
      CSS.highlights.set(
        HIGHLIGHT_ACTIVE_TABLE,
        range ? new Highlight(range) : new Highlight(),
      );
    },

    extraAction(field, table) {
      if (table.aligned) return null;
      return {
        icon: 'format',
        title: 'Format table',
        run: () => writeAligned(field, table),
      };
    },

    edit(field, table) {
      const {
        format
      } = fieldTables.get(field);
      // The editor writes the whole table on Apply, so the table is not
      // aligned automatically when the editor takes the focus.
      editing = null;
      openEditor('Edit table', table, (edited) => {
        if (!field.isConnected) return;
        const tableLines = format.serialize(edited);
        fieldWidgets.replaceLines(field, table.start, table.end, tableLines);
      }, cellWidgetContext(field));
    },

    insert(field, line) {
      const {
        format
      } = fieldTables.get(field);
      openEditor('Insert table', createEmptyTable(3, 2), (created) => {
        if (!field.isConnected) return;
        fieldWidgets.insertBlock(field, line, format.serialize(created));
      }, cellWidgetContext(field));
    },
  });

})();
