import { createElement, formatDelta, formatValue } from './formatters.js';

let trendChart;
let rankingChart;

function chartTheme() {
  return {
    ink: '#24313f',
    muted: '#667789',
    blue: '#1d63ad',
    green: '#238a63',
    amber: '#b47a1e',
    red: '#b64c35',
    line: '#d2cbb8',
  };
}

function showFallback(containerId, chartElement, rows, columns, summary) {
  const fallback = document.getElementById(containerId);
  if (!fallback) return;
  chartElement?.classList.add('chart--fallback-active');
  fallback.hidden = false;
  fallback.textContent = '';
  fallback.append(createElement('p', { text: summary }));
  const table = document.createElement('table');
  const thead = document.createElement('thead');
  const tbody = document.createElement('tbody');
  const headerRow = document.createElement('tr');
  columns.forEach((column) => {
    const th = document.createElement('th');
    th.scope = 'col';
    th.textContent = column.label;
    headerRow.append(th);
  });
  thead.append(headerRow);
  rows.forEach((row) => {
    const tr = document.createElement('tr');
    columns.forEach((column) => {
      const td = document.createElement('td');
      td.textContent = column.render(row);
      tr.append(td);
    });
    tbody.append(tr);
  });
  table.append(thead, tbody);
  fallback.append(table);
}

function hideFallback(containerId, chartElement) {
  const fallback = document.getElementById(containerId);
  chartElement?.classList.remove('chart--fallback-active');
  if (fallback) {
    fallback.hidden = true;
    fallback.textContent = '';
  }
}

function hasEcharts() {
  return Boolean(window.echarts);
}

export function renderTrendChart(series) {
  const element = document.getElementById('trend-chart');
  if (!element || !series) return;
  const unit = series.unit ?? '';
  const points = series.points ?? [];
  const summary = `Fallback tren ${series.indicator_name}. Data berasal dari rata-rata ${points.length} titik tahun.`;
  element.setAttribute('aria-label', `Tren ${series.indicator_name}, ${points.length} titik tahun`);
  if (!hasEcharts()) {
    showFallback(
      'trend-fallback',
      element,
      points,
      [
        { label: 'Tahun', render: (row) => String(row.year) },
        { label: 'Nilai rata-rata', render: (row) => formatValue(row.value, unit) },
        { label: 'Baris', render: (row) => String(row.record_count) },
      ],
      summary,
    );
    return;
  }
  hideFallback('trend-fallback', element);
  const colors = chartTheme();
  trendChart = trendChart || window.echarts.init(element, null, { renderer: 'canvas' });
  trendChart.setOption({
    color: [colors.blue],
    grid: { left: 58, right: 24, top: 32, bottom: 52 },
    tooltip: {
      trigger: 'axis',
      valueFormatter: (value) => formatValue(value, unit),
      extraCssText: 'font-variant-numeric: tabular-nums;',
    },
    xAxis: {
      type: 'category',
      data: points.map((point) => point.year),
      axisLine: { lineStyle: { color: colors.line } },
      axisLabel: { color: colors.muted },
      axisTick: { show: false },
    },
    yAxis: {
      type: 'value',
      name: unit,
      nameTextStyle: { color: colors.muted },
      splitLine: { lineStyle: { color: colors.line } },
      axisLabel: { color: colors.muted },
    },
    series: [
      {
        name: series.indicator_name,
        type: 'line',
        smooth: true,
        symbolSize: 9,
        lineStyle: { width: 3 },
        emphasis: { focus: 'series' },
        data: points.map((point) => ({
          value: point.value,
          record_count: point.record_count,
        })),
      },
    ],
  }, true);
}

export function renderRankingChart(ranking, rows, mode) {
  const element = document.getElementById('ranking-chart');
  if (!element || !ranking) return;
  const unit = ranking.unit ?? '';
  const visibleRows = rows.slice(0, 14).reverse();
  const isChange = mode === 'change';
  const summary = `Fallback ranking ${ranking.indicator_name}. Menampilkan ${visibleRows.length} wilayah.`;
  element.setAttribute('aria-label', `Ranking ${ranking.indicator_name}, ${visibleRows.length} wilayah`);
  if (!hasEcharts()) {
    showFallback(
      'ranking-fallback',
      element,
      visibleRows.slice().reverse(),
      [
        { label: 'Wilayah', render: (row) => row.region_name },
        { label: isChange ? 'Perubahan' : 'Nilai', render: (row) => (isChange ? formatDelta(row.delta, unit) : formatValue(row.value, unit)) },
      ],
      summary,
    );
    return;
  }
  hideFallback('ranking-fallback', element);
  const colors = chartTheme();
  rankingChart = rankingChart || window.echarts.init(element, null, { renderer: 'canvas' });
  rankingChart.setOption({
    color: [isChange ? colors.amber : colors.green],
    grid: { left: 132, right: 34, top: 18, bottom: 28 },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params) => {
        const param = params[0];
        const row = visibleRows[param.dataIndex];
        if (isChange) {
          return `${row.region_name}<br>${row.from_year}-${row.to_year}: ${formatDelta(row.delta, unit)}`;
        }
        return `${row.region_name}<br>${ranking.year}: ${formatValue(row.value, unit)}<br>${row.record_count} baris fakta`;
      },
      extraCssText: 'font-variant-numeric: tabular-nums;',
    },
    xAxis: {
      type: 'value',
      axisLabel: { color: colors.muted },
      splitLine: { lineStyle: { color: colors.line } },
    },
    yAxis: {
      type: 'category',
      data: visibleRows.map((row) => row.region_name),
      axisLabel: { color: colors.ink, width: 118, overflow: 'truncate' },
      axisLine: { show: false },
      axisTick: { show: false },
    },
    series: [
      {
        type: 'bar',
        barWidth: 14,
        itemStyle: { borderRadius: [0, 4, 4, 0] },
        data: visibleRows.map((row) => (isChange ? row.delta : row.value)),
      },
    ],
  }, true);
}

export function registerChartResize() {
  window.addEventListener('resize', () => {
    trendChart?.resize();
    rankingChart?.resize();
  });
}
