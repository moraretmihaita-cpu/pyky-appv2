import { getJson } from './client';

export async function fetchMetaCampaigns(params) {
  return getJson('/api/meta/campaigns', {
    meta_date_preset: params.metaDateRange,
    campaign_filter: params.campaignFilter || '',
    compare_previous: params.comparePrevious ? 'true' : 'false',
  });
}

export async function fetchMetaAdSets(params) {
  return getJson('/api/meta/adsets', {
    meta_date_preset: params.metaDateRange,
    campaign_filter: params.campaignFilter || '',
    compare_previous: params.comparePrevious ? 'true' : 'false',
  });
}

export async function fetchMetaProducts(params) {
  return getJson('/api/meta/products', {
    meta_date_preset: params.metaDateRange,
    campaign_filter: params.campaignFilter || '',
    product_filter: params.productFilter || '',
    selected_item_id: params.selectedItemId || '',
    compare_previous: params.comparePrevious ? 'true' : 'false',
  });
}
