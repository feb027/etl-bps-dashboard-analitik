async function loadDashboardData() {
  const response = await fetch('data/dashboard-data.json', { cache: 'no-store' });
  if (!response.ok) throw new Error(`Failed to load dashboard data: ${response.status}`);
  return response.json();
}

function setText(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value ?? '0';
}

function render(data) {
  setText('project-status', data.project?.status || 'Status tidak tersedia');
  setText('indicator-count', data.summary?.indicator_count ?? 0);
  setText('region-count', data.summary?.region_count ?? 0);
  setText('year-count', data.summary?.year_count ?? 0);
  setText('record-count', data.summary?.record_count ?? 0);

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
