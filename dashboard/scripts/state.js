export function createInitialState(data) {
  const firstIndicator = data.indicators[0]?.key ?? '';
  const lastYear = data.years[data.years.length - 1]?.year ?? '';
  return {
    indicatorKey: firstIndicator,
    year: String(lastYear),
    regionSearch: '',
    rankingMode: 'top',
    sortKey: 'region_name',
    sortDirection: 'asc',
  };
}

export function updateState(state, patch) {
  return { ...state, ...patch };
}
