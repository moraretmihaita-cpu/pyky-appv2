const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

function qs(params) {
  return new URLSearchParams(params).toString();
}

async function getJson(path, params) {
  const url = params ? `${API_BASE}${path}?${qs(params)}` : `${API_BASE}${path}`;
  const response = await fetch(url);
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed with status ${response.status}`);
  }
  return response.json();
}

async function postJson(path, body) {
  const response = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed with status ${response.status}`);
  }
  return response.json();
}

export async function fetchHealth() {
  return getJson('/health');
}

export async function fetchOverview(params) {
  return getJson('/api/overview', {
    ga4_start: params.ga4Start,
    ga4_end: params.ga4End,
    ads_date_range: params.adsDateRange,
    campaign_filter: params.campaignFilter || '',
    product_filter: params.productFilter || '',
    selected_item_id: params.selectedItemId || '',
  });
}

export async function fetchGoogleAdsCampaigns(params) {
  return getJson('/api/google-ads/campaigns', {
    ads_date_range: params.adsDateRange,
    campaign_filter: params.campaignFilter || '',
  });
}

export async function fetchGoogleAdsProducts(params) {
  return getJson('/api/google-ads/products', {
    ads_date_range: params.adsDateRange,
    campaign_filter: params.campaignFilter || '',
    product_filter: params.productFilter || '',
    selected_item_id: params.selectedItemId || '',
  });
}

export async function fetchMetaCampaigns(params) {
  return getJson('/api/meta/campaigns', {
    meta_date_preset: params.metaDateRange,
    campaign_filter: params.campaignFilter || '',
  });
}

export async function fetchMetaAdSets(params) {
  return getJson('/api/meta/adsets', {
    meta_date_preset: params.metaDateRange,
    campaign_filter: params.campaignFilter || '',
  });
}

export async function fetchMetaProducts(params) {
  return getJson('/api/meta/products', {
    meta_date_preset: params.metaDateRange,
    campaign_filter: params.campaignFilter || '',
    product_filter: params.productFilter || '',
    selected_item_id: params.selectedItemId || '',
  });
}

export async function fetchGa4Products(params) {
  return getJson('/api/ga4/products', {
    ga4_start: params.ga4Start,
    ga4_end: params.ga4End,
    product_filter: params.productFilter || '',
    selected_item_id: params.selectedItemId || '',
  });
}

export async function fetchGa4Traffic(params) {
  return getJson('/api/ga4/traffic', {
    ga4_start: params.ga4Start,
    ga4_end: params.ga4End,
    traffic_type: params.trafficType || 'toate',
    campaign_filter: params.campaignFilter || '',
  });
}

export async function fetchGa4LandingPages(params) {
  return getJson('/api/ga4/landing-pages', {
    ga4_start: params.ga4Start,
    ga4_end: params.ga4End,
    page_type: params.pageType || 'toate',
  });
}

export async function fetchGa4Devices(params) {
  return getJson('/api/ga4/devices', {
    ga4_start: params.ga4Start,
    ga4_end: params.ga4End,
  });
}

export async function fetchGa4ProductChannels(params) {
  return getJson('/api/ga4/product-channels', {
    ga4_start: params.ga4Start,
    ga4_end: params.ga4End,
    source_filter: params.sourceFilter || '',
    product_filter: params.productFilter || '',
    selected_item_id: params.selectedItemId || '',
  });
}

export async function fetchJoinAdsGa4(params) {
  return getJson('/api/join-ads-ga4', {
    ga4_start: params.ga4Start,
    ga4_end: params.ga4End,
    ads_date_range: params.adsDateRange,
    campaign_filter: params.campaignFilter || '',
    product_filter: params.productFilter || '',
    selected_item_id: params.selectedItemId || '',
  });
}

export async function fetchPmaxFeedVsOther(params) {
  return getJson('/api/pmax-feed-vs-other', {
    ads_date_range: params.adsDateRange,
    campaign_filter: params.campaignFilter || '',
  });
}

export async function fetchFaviReport(params) {
  return getJson('/api/favi', {
    ga4_start: params.ga4Start,
    ga4_end: params.ga4End,
    product_filter: params.productFilter || '',
    selected_item_id: params.selectedItemId || '',
    page_type: params.pageType || 'toate',
  });
}

export async function fetchAiProviders() {
  return getJson('/api/ai/providers');
}

export async function sendCopilotMessage(payload) {
  return postJson('/api/copilot/chat', payload);
}


export async function fetchFunnelCoverage(params) {
  return getJson('/api/funnel/coverage', {
    ads_date_range: params.adsDateRange,
    meta_date_preset: params.metaDateRange,
    campaign_filter: params.campaignFilter || '',
    compare_previous: params.comparePrevious ? 'true' : 'false',
  });
}
