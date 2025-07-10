// @relation(SDOC-SRS-35, scope=file)

document.addEventListener("DOMContentLoaded", () => {
  const table = document.querySelector(".project_coverage");
  const tbody = table.querySelector("tbody");
  const originalRows = Array.from(tbody.rows);
  let sortState = null;

  const handlers = table.querySelectorAll(".project_coverage-sort_handler");
  const colgroupCols = table.querySelectorAll("colgroup col");

  handlers.forEach((handler) => {
    handler.addEventListener("click", () => {

      const dataId = handler.getAttribute("data-id");
      // We expect:
      // - Each .project_coverage-sort_handler has a unique data-id
      // - Each <td> in sortable rows has matching data-id and data-value
      // - <colgroup> contains <col data-id="..."> matching the same data-id

      console.assert(dataId, "Missing data-id on sort handler.");
      if (!dataId) return;

      const isSameColumn = sortState && sortState.id === dataId;
      const asc = isSameColumn ? !sortState.asc : false;

      const rows = Array.from(tbody.rows);
      const validRows = rows.filter(row =>
        row.classList.contains("project_coverage-file") &&
        row.querySelector(`td[data-id="${dataId}"]`)
      );
      if (validRows.length === 0) return;

      validRows.sort((a, b) => {
        const aCell = a.querySelector(`td[data-id="${dataId}"]`);
        const bCell = b.querySelector(`td[data-id="${dataId}"]`);
        const aVal = parseFloat(aCell?.dataset.value || '0');
        const bVal = parseFloat(bCell?.dataset.value || '0');
        return asc ? aVal - bVal : bVal - aVal;
      });

      tbody.innerHTML = "";
      validRows.forEach(row => tbody.appendChild(row));
      table.classList.add("sorted");

      handlers.forEach(h => h.removeAttribute("sorted"));
      handler.setAttribute("sorted", asc ? "asc" : "dsc");

      sortState = { id: dataId, asc };

      // Highlight active <col>
      colgroupCols.forEach(col => col.classList.remove("sorted_col"));
      const activeCol = table.querySelector(`colgroup col[data-id="${dataId}"]`);
      if (activeCol) {
        activeCol.classList.add("sorted_col");
      } else {
        console.warn(`No <col> found for data-id="${dataId}"`);
      }
    });
  });

  const resetter = table.querySelector(".project_coverage-sort_reset");
  if (resetter) {
    resetter.addEventListener("click", () => {
      tbody.innerHTML = "";
      originalRows.forEach(row => tbody.appendChild(row));
      table.classList.remove("sorted");
      handlers.forEach(h => h.removeAttribute("sorted"));
      colgroupCols.forEach(col => col.classList.remove("sorted_col"));
      sortState = null;
    });
  }
});
