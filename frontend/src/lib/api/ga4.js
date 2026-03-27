import { getJson } from './client';

export async function fetchGa4Products(params) {
  return getJson('/api/ga4/products', {
    ga4_start: params.ga4Start,
    ga4_end: params.ga4End,
    product_filter: params.productFilter || '',
    selected_item_id: params.selectedItemId || '',
    compare_previous: params.comparePrevious ? 'true' : 'false',
  });
}

export async function fetchGa4Traffic(params) {
  return getJson('/api/ga4/traffic', {
    ga4_start: params.ga4Start,
    ga4_end: params.ga4End,
    traffic_type: params.trafficType || 'toate',
    campaign_filter: params.campaignFilter || '',
    compare_previous: params.comparePrevious ? 'true' : 'false',
  });
}

export async function fetchGa4LandingPages(params) {
  return getJson('/api/ga4/landing-pages', {
    ga4_start: params.ga4Start,
    ga4_end: params.ga4End,
    page_type: params.pageType || 'toate',
    compare_previous: params.comparePrevious ? 'true' : 'false',
  });
}

export async function fetchGa4Devices(params) {
  return getJson('/api/ga4/devices', {
    ga4_start: params.ga4Start,
    ga4_end: params.ga4End,
    compare_previous: params.comparePrevious ? 'true' : 'false',
  });
}

export async function fetchGa4ProductChannels(params) {
  return getJson('/api/ga4/product-channels', {
    ga4_start: params.ga4Start,
    ga4_end: params.ga4End,
    source_filter: params.sourceFilter || '',
    product_filter: params.productFilter || '',
    selected_item_id: params.selectedItemId || '',
    compare_previous: params.comparePrevious ? 'true' : 'false',
  });
}

export async function fetchFaviReport(params) {
  return getJson('/api/favi', {
    ga4_start: params.ga4Start,
    ga4_end: params.ga4End,
    product_filter: params.productFilter || '',
    selected_item_id: params.selectedItemId || '',
    page_type: params.pageType || 'toate',
    compare_previous: params.comparePrevious ? 'true' : 'false',
  });
}
