import { normalizeText } from './formatters.js';

export function populateFilters(data, state) {
  const indicatorSelect = document.getElementById('indicator-select');
  const yearSelect = document.getElementById('year-select');
  if (indicatorSelect) {
    indicatorSelect.textContent = '';
    data.indicators.forEach((indicator) => {
      const option = document.createElement('option');
      option.value = indicator.key;
      option.textContent = indicator.name;
      option.title = indicator.name;
      option.selected = indicator.key === state.indicatorKey;
      indicatorSelect.append(option);
    });
  }
  if (yearSelect) {
    yearSelect.textContent = '';
    data.years.forEach((year) => {
      const option = document.createElement('option');
      option.value = String(year.year);
      option.textContent = String(year.year);
      option.selected = String(year.year) === String(state.year);
      yearSelect.append(option);
    });
  }
}

export function selectedIndicator(data, state) {
  return data.indicators.find((indicator) => indicator.key === state.indicatorKey) ?? data.indicators[0];
}

export function trendForSelection(data, state) {
  return data.series.trend.find((series) => series.indicator_key === state.indicatorKey) ?? data.series.trend[0];
}

export function rankingForSelection(data, state) {
  const mode = state.rankingMode;
  if (mode === 'change') {
    return data.rankings.change.find((item) => item.indicator_key === state.indicatorKey) ?? data.rankings.change[0];
  }
  return data.rankings[mode].find(
    (item) => item.indicator_key === state.indicatorKey && String(item.year) === String(state.year),
  ) ?? data.rankings[mode][0];
}

export function filteredRankingRows(ranking, state) {
  const query = normalizeText(state.regionSearch);
  const rows = ranking?.rows ?? [];
  if (!query) {
    return rows;
  }
  return rows.filter((row) => normalizeText(`${row.region_name} ${row.region_code} ${row.region_level}`).includes(query));
}

export function filteredTableRows(data, state) {
  const query = normalizeText(state.regionSearch);
  return data.table_rows.filter((row) => {
    const indicatorMatches = row.indicator_key === state.indicatorKey;
    const yearMatches = String(row.year) === String(state.year);
    const regionMatches = !query || normalizeText(`${row.region_name} ${row.region_code} ${row.region_level}`).includes(query);
    return indicatorMatches && yearMatches && regionMatches;
  });
}

export function sortedRows(rows, state) {
  const direction = state.sortDirection === 'desc' ? -1 : 1;
  return [...rows].sort((a, b) => {
    const left = a[state.sortKey];
    const right = b[state.sortKey];
    if (typeof left === 'number' && typeof right === 'number') {
      return (left - right) * direction;
    }
    return String(left ?? '').localeCompare(String(right ?? ''), 'id-ID', { numeric: true }) * direction;
  });
}
