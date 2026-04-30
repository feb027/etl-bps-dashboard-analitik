const numberFormatter = new Intl.NumberFormat('id-ID');
const valueFormatter = new Intl.NumberFormat('id-ID', {
  maximumFractionDigits: 2,
  minimumFractionDigits: 0,
});

export function formatNumber(value) {
  return numberFormatter.format(Number(value ?? 0));
}

export function formatValue(value, unit = '') {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return '-';
  }
  const suffix = unit ? ` ${unit}` : '';
  return `${valueFormatter.format(Number(value))}${suffix}`;
}

export function formatDelta(value, unit = '') {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return '-';
  }
  const numeric = Number(value);
  const prefix = numeric > 0 ? '+' : '';
  const suffix = unit ? ` ${unit}` : '';
  return `${prefix}${valueFormatter.format(numeric)}${suffix}`;
}

export function normalizeText(value) {
  return String(value ?? '').toLocaleLowerCase('id-ID');
}

export function setText(id, value) {
  const element = document.getElementById(id);
  if (element) {
    element.textContent = value ?? '-';
  }
}

export function createElement(tagName, options = {}) {
  const element = document.createElement(tagName);
  if (options.className) {
    element.className = options.className;
  }
  if (options.text !== undefined) {
    element.textContent = options.text;
  }
  return element;
}
