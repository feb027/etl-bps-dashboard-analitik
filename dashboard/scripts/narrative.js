import { formatDelta, formatValue } from './formatters.js';

function sentence(parts) {
  return parts.filter(Boolean).join(' ');
}

export function renderNarrative(data, state) {
  const panel = document.getElementById('narrative-panel');
  if (!panel) return;
  const seed = data.narrative_seed?.by_indicator?.[state.indicatorKey];
  if (!seed) {
    panel.textContent = 'Insight belum tersedia untuk pilihan ini.';
    return;
  }
  const unit = seed.unit ?? '';
  const top = seed.latest_top;
  const bottom = seed.latest_bottom;
  const change = seed.largest_absolute_change;
  const fragments = [
    seed.latest_year && seed.latest_average !== null
      ? `Pada ${seed.latest_year}, rata-rata ${seed.indicator_name} dari baris fakta tersedia adalah ${formatValue(seed.latest_average, unit)}.`
      : null,
    top && bottom
      ? `Wilayah tertinggi dalam agregasi yang sama adalah ${top.region_name} (${formatValue(top.value, unit)}), sedangkan terendah adalah ${bottom.region_name} (${formatValue(bottom.value, unit)}).`
      : null,
    change
      ? `Perubahan absolut terbesar antara ${change.from_year} dan ${change.to_year} tercatat di ${change.region_name}, sebesar ${formatDelta(change.delta, unit)}.`
      : null,
    `Catatan: angka ini berasal dari ${seed.aggregation.replaceAll('_', ' ')} dan tidak menggunakan data buatan.`,
  ];
  panel.textContent = sentence(fragments);
}
