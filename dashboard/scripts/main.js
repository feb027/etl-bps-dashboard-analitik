import { loadDashboardData } from './data-loader.js';
import { filteredRankingRows, filteredTableRows, populateFilters, rankingForSelection, selectedIndicator, sortedRows, trendForSelection } from './filters.js';
import { formatNumber, setText } from './formatters.js';
import { createInitialState, updateState } from './state.js';
import { registerChartResize, renderRankingChart, renderTrendChart } from './charts.js';
import { bindTableSorting, renderTable } from './table.js';
import { renderNarrative } from './narrative.js';

let dashboardData;
let state;

function renderSummary(data) {
  setText('project-status', data.project?.status ?? 'Status dashboard tidak tersedia.');
  setText('summary-indicators', formatNumber(data.summary?.indicator_count));
  setText('summary-regions', formatNumber(data.summary?.region_count));
  setText('summary-years', formatNumber(data.summary?.year_count));
  setText('summary-records', formatNumber(data.summary?.record_count));
  setText('source-line', `Sumber: ${data.evidence?.source_paths?.dashboard_json ?? 'dashboard/data/dashboard-data.json'} dari ${data.evidence?.database_path ?? 'SQLite lokal'}`);
  setText('evidence-run', data.summary?.last_etl_run ?? '-');
  setText('evidence-db', data.evidence?.database_path ?? '-');
  const review = data.project?.review;
  const reviewText = review?.score === null ? `Fase ${review.phase}: ${review.verdict}` : `Fase ${review?.phase}: ${review?.score}/100 ${review?.verdict}`;
  setText('evidence-review', reviewText);
  setText('evidence-quality', data.quality?.no_dummy_data ? 'true' : 'false');

  const artifactList = document.getElementById('artifact-list');
  if (artifactList) {
    artifactList.textContent = '';
    (data.evidence?.artifacts ?? data.artifacts ?? []).slice(0, 10).forEach((artifact) => {
      const item = document.createElement('li');
      const code = document.createElement('code');
      code.textContent = artifact;
      item.append(code);
      artifactList.append(item);
    });
  }
}

function renderDynamicSections() {
  const indicator = selectedIndicator(dashboardData, state);
  const trend = trendForSelection(dashboardData, state);
  const ranking = rankingForSelection(dashboardData, state);
  const rankingRows = filteredRankingRows(ranking, state);
  const tableRows = sortedRows(filteredTableRows(dashboardData, state), state);

  setText('trend-summary', `${trend.indicator_name}: rata-rata ${trend.points.length} tahun dari baris fakta BPS yang tersedia.`);
  setText('selected-indicator-label', indicator?.name ?? state.indicatorKey);
  if (state.rankingMode === 'change') {
    setText('ranking-summary', `${ranking.indicator_name}: perubahan wilayah ${ranking.from_year}-${ranking.to_year}, difilter menurut pencarian wilayah.`);
  } else {
    setText('ranking-summary', `${ranking.indicator_name}: ${state.rankingMode === 'top' ? 'wilayah tertinggi' : 'wilayah terendah'} pada ${state.year}.`);
  }

  renderTrendChart(trend);
  renderRankingChart(ranking, rankingRows, state.rankingMode);
  renderNarrative(dashboardData, state);
  renderTable(tableRows, state, indicator);
}

function bindControls() {
  const indicatorSelect = document.getElementById('indicator-select');
  const yearSelect = document.getElementById('year-select');
  const regionSearch = document.getElementById('region-search');
  indicatorSelect?.addEventListener('change', (event) => {
    state = updateState(state, { indicatorKey: event.target.value });
    renderDynamicSections();
  });
  yearSelect?.addEventListener('change', (event) => {
    state = updateState(state, { year: event.target.value });
    renderDynamicSections();
  });
  regionSearch?.addEventListener('input', (event) => {
    state = updateState(state, { regionSearch: event.target.value });
    renderDynamicSections();
  });
  document.querySelectorAll('input[name="ranking-mode"]').forEach((control) => {
    control.addEventListener('change', (event) => {
      state = updateState(state, { rankingMode: event.target.value });
      renderDynamicSections();
      const rankingSection = document.querySelector('.atlas-section--ranking');
      rankingSection?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });
  bindTableSorting((sortKey) => {
    const sortDirection = state.sortKey === sortKey && state.sortDirection === 'asc' ? 'desc' : 'asc';
    state = updateState(state, { sortKey, sortDirection });
    renderDynamicSections();
  });
}

function showLoadError(error) {
  const element = document.getElementById('load-error');
  if (element) {
    element.hidden = false;
    element.textContent = error.message;
  }
  setText('project-status', `Dashboard gagal memuat data: ${error.message}`);
}

async function boot() {
  try {
    dashboardData = await loadDashboardData();
    state = createInitialState(dashboardData);
    renderSummary(dashboardData);
    populateFilters(dashboardData, state);
    bindControls();
    registerChartResize();
    renderDynamicSections();
  } catch (error) {
    showLoadError(error);
  }
}

boot();
