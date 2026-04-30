import { createElement, formatNumber, formatValue } from './formatters.js';

const VISIBLE_LIMIT = 80;

function appendCell(rowElement, content, options = {}) {
  const cell = document.createElement('td');
  if (options.kind) {
    cell.dataset.kind = options.kind;
  }
  if (Array.isArray(content)) {
    content.forEach((item) => cell.append(item));
  } else {
    cell.textContent = content;
  }
  rowElement.append(cell);
}

export function renderTable(rows, state, selectedIndicator) {
  const body = document.getElementById('table-body');
  const count = document.getElementById('table-count');
  if (!body) return;
  body.textContent = '';
  const visibleRows = rows.slice(0, VISIBLE_LIMIT);
  visibleRows.forEach((row) => {
    const tr = document.createElement('tr');
    appendCell(tr, [
      document.createTextNode(row.indicator_name),
      createElement('span', { className: 'muted-cell', text: row.indicator_key }),
    ]);
    appendCell(tr, String(row.year));
    appendCell(tr, [
      document.createTextNode(row.region_name),
      createElement('span', { className: 'muted-cell', text: `${row.region_code} · ${row.region_level}` }),
    ]);
    appendCell(tr, `${row.turvar_label} · ${row.turth_label}`);
    appendCell(tr, formatValue(row.value, row.unit), { kind: 'number' });
    appendCell(tr, [
      document.createTextNode(row.source_domain),
      createElement('span', { className: 'muted-cell', text: row.data_key }),
    ]);
    body.append(tr);
  });
  if (count) {
    const suffix = rows.length > VISIBLE_LIMIT ? `, ${formatNumber(VISIBLE_LIMIT)} ditampilkan` : '';
    count.textContent = `${formatNumber(rows.length)} baris${suffix} · ${selectedIndicator?.name ?? state.indicatorKey}`;
  }
}

function updateSortAccessibility(activeButton) {
  document.querySelectorAll('[data-sort]').forEach((button) => {
    const header = button.closest('th');
    if (!header) return;
    if (button === activeButton) {
      const direction = button.dataset.direction === 'asc' ? 'ascending' : 'descending';
      header.setAttribute('aria-sort', direction);
      button.setAttribute('aria-label', `Urutkan berdasarkan ${button.textContent.trim()}, arah aktif ${direction}`);
    } else {
      header.setAttribute('aria-sort', 'none');
      button.removeAttribute('aria-label');
    }
  });
}

export function bindTableSorting(onSort) {
  document.querySelectorAll('[data-sort]').forEach((button) => {
    const header = button.closest('th');
    if (header) header.setAttribute('aria-sort', 'none');
    button.addEventListener('click', () => {
      const nextDirection = button.dataset.direction === 'asc' ? 'desc' : 'asc';
      button.dataset.direction = nextDirection;
      updateSortAccessibility(button);
      onSort(button.dataset.sort);
    });
  });
}
