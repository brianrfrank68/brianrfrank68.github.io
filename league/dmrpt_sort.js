/* Click-to-sort for Diamond Mind report tables (table.dmrpt).
   Maintained here; league/style_flb_reports.py copies this file into each
   league directory and links it from every report page that has a table. */
(function () {
  "use strict";

  function parseCellValue(raw) {
    var text = raw.replace(/ /g, " ").trim();
    if (text === "") return null;
    if (text === "-") return 0; // e.g. "0 games behind" for the division leader in GB columns

    // mixed fraction, e.g. games-behind values like "8 1/2"
    var frac = text.match(/^(-?\d+)\s+(\d+)\/(\d+)$/);
    if (frac) {
      var whole = parseInt(frac[1], 10);
      var part = parseInt(frac[2], 10) / parseInt(frac[3], 10);
      return whole < 0 ? whole - part : whole + part;
    }

    if (/^-?\.?\d+(\.\d+)?$/.test(text)) return parseFloat(text);
    return NaN; // not a number; comparator falls back to string compare
  }

  function cellText(row, index) {
    var cell = row.children[index];
    return cell ? cell.textContent : "";
  }

  function isPinnedRow(row) {
    var limit = Math.min(3, row.children.length);
    for (var i = 0; i < limit; i++) {
      var text = row.children[i].textContent.replace(/ /g, " ").trim().toLowerCase();
      if (text === "total" || text === "totals") return true;
    }
    return false;
  }

  function compareRows(a, b, index, dir) {
    var rawA = cellText(a, index);
    var rawB = cellText(b, index);
    var av = parseCellValue(rawA);
    var bv = parseCellValue(rawB);

    if (av === null && bv === null) return 0;
    if (av === null) return 1; // blanks always sort last
    if (bv === null) return -1;

    var aNum = !isNaN(av);
    var bNum = !isNaN(bv);
    if (aNum && bNum) return dir * (av - bv);
    if (aNum !== bNum) return aNum ? -1 : 1;
    return dir * rawA.trim().localeCompare(rawB.trim());
  }

  function makeSortable(table) {
    var headerRows = table.querySelectorAll("tr.dmrptsecthdr");
    if (!headerRows.length) return;

    var headerRow = headerRows[headerRows.length - 1];
    var headerCells = Array.prototype.slice.call(headerRow.children);

    // Skip decorative spanning header rows (real column headers are single-cell).
    var hasSpan = headerCells.some(function (cell) {
      var span = cell.getAttribute("colspan");
      return span && span !== "1";
    });
    if (hasSpan) return;

    var tbody = headerRow.parentNode;
    var dataRows = Array.prototype.slice.call(table.querySelectorAll("tr.dmrptbody, tr.dmrptbody2"));
    if (dataRows.length < 2) return;

    headerCells.forEach(function (cell, index) {
      cell.classList.add("sortable");
      cell.addEventListener("click", function () {
        var nextDir = cell.getAttribute("data-dir") === "asc" ? "desc" : "asc";
        headerCells.forEach(function (c) { c.removeAttribute("data-dir"); });
        cell.setAttribute("data-dir", nextDir);
        var dir = nextDir === "asc" ? 1 : -1;

        var pinned = dataRows.filter(isPinnedRow);
        var sortable = dataRows.filter(function (row) { return pinned.indexOf(row) === -1; });
        sortable.sort(function (a, b) { return compareRows(a, b, index, dir); });

        var frag = document.createDocumentFragment();
        sortable.concat(pinned).forEach(function (row) { frag.appendChild(row); });
        tbody.appendChild(frag);
      });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    var tables = document.querySelectorAll("table.dmrpt");
    for (var i = 0; i < tables.length; i++) makeSortable(tables[i]);
  });
})();
