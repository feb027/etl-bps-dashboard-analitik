export async function loadDashboardData(path = 'data/dashboard-data.json') {
  const response = await fetch(path, { cache: 'no-store' });
  if (!response.ok) {
    throw new Error(`Gagal memuat ${path}: HTTP ${response.status}`);
  }
  const data = await response.json();
  validateDashboardData(data);
  return data;
}

export function validateDashboardData(data) {
  const requiredArrays = ['indicators', 'years', 'regions', 'table_rows'];
  for (const key of requiredArrays) {
    if (!Array.isArray(data[key])) {
      throw new Error(`dashboard-data.json tidak valid: ${key} harus berupa array`);
    }
  }
  if (!data.series?.trend?.length) {
    throw new Error('dashboard-data.json tidak memiliki series.trend dari SQLite');
  }
  if (!data.quality?.no_dummy_data) {
    throw new Error('dashboard-data.json tidak menyatakan no_dummy_data=true');
  }
}
