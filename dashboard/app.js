async function loadDashboardData() {
  const response = await fetch('data/dashboard-data.json', { cache: 'no-store' });
  if (!response.ok) throw new Error(`Failed to load dashboard data: ${response.status}`);
  return response.json();
}

function setText(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value ?? '0';
}

function formatNumber(value) {
  return new Intl.NumberFormat('id-ID').format(value ?? 0);
}

function renderPhaseProgress(phases = []) {
  const list = document.getElementById('phase-list');
  if (!list) return;

  list.innerHTML = phases.map((item) => `
    <article class="phase-item phase-${item.status}">
      <span class="phase-badge">Fase ${item.phase}</span>
      <div>
        <h3>${item.title}</h3>
        <p>${item.description}</p>
      </div>
    </article>
  `).join('');
}

function renderArtifacts(artifacts = []) {
  const list = document.getElementById('artifact-list');
  if (!list) return;

  list.innerHTML = artifacts.map((artifact) => `<li><code>${artifact}</code></li>`).join('');
}

function render(data) {
  const metrics = data.design_metrics || {};
  const review = data.project?.review || {};

  setText('current-phase', data.project?.current_phase || 'Fase tidak tersedia');
  setText('project-status', data.project?.status || 'Status tidak tersedia');
  setText('review-pill', review.verdict ? `Review Fase ${review.phase}: ${review.score}/100 ${review.verdict}` : 'Review: -');

  setText('valid-indicators', formatNumber(metrics.valid_indicators));
  setText('api-probe-rows', formatNumber(metrics.api_probe_rows));
  setText('normalized-sample-records', formatNumber(metrics.normalized_sample_records));
  setText('schema-validation-tests', formatNumber(metrics.schema_validation_tests));
  setText('dimension-tables', formatNumber(metrics.dimension_tables));
  setText('fact-tables', formatNumber(metrics.fact_tables));
  setText('audit-tables', formatNumber(metrics.audit_tables));
  setText('unmatched-keys', formatNumber(metrics.unmatched_datacontent_keys));
  setText('extract-targets', formatNumber(metrics.extract_targets));
  setText('metadata-snapshots', formatNumber(metrics.metadata_snapshots));
  setText('dynamic-snapshots', formatNumber(metrics.dynamic_snapshots));
  setText('total-raw-rows', formatNumber(metrics.total_raw_rows));
  setText('transform-fact-rows', formatNumber(metrics.transform_fact_preview_rows));
  setText('transform-quality-gate', metrics.transform_quality_gate || '-');
  setText('transform-unmatched', formatNumber(metrics.transform_unmatched_count));
  setText('transform-duplicates', formatNumber(metrics.transform_duplicate_fact_key_count));
  setText('fact-grain', data.schema?.fact_grain || '-');

  renderPhaseProgress(data.phase_progress || []);
  renderArtifacts(data.artifacts || []);

  const empty = document.getElementById('empty-state');
  if (empty && (data.summary?.record_count ?? 0) === 0) {
    empty.hidden = false;
  }
}

loadDashboardData()
  .then(render)
  .catch((error) => {
    setText('project-status', `Gagal memuat dashboard data: ${error.message}`);
    const empty = document.getElementById('empty-state');
    if (empty) empty.hidden = false;
  });
