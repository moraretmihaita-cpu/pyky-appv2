
const API_BASE = 'http://127.0.0.1:8000';

async function fetchJson(path) {
  const response = await fetch(`${API_BASE}${path}`);
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `HTTP ${response.status}`);
  }
  return response.json();
}

export async function fetchOverview(filters) {
  const params = new URLSearchParams({
    ga4_start: filters.ga4Start,
    ga4_end: filters.ga4End,
    ads_date_range: filters.adsDateRange,
    meta_date_preset: filters.metaDateRange,
    campaign_filter: filters.campaignFilter || '',
    product_filter: filters.productFilter || '',
    selected_item_id: filters.selectedItemId || '',
    compare_previous: filters.comparePrevious ? 'true' : 'false',
  });

  return fetchJson(`/api/overview?${params.toString()}`);
}
