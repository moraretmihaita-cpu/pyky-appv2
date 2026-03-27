import { getJson } from './client';

export async function fetchJoinAdsGa4(params) {
  return getJson('/api/join-ads-ga4', {
    ga4_start: params.ga4Start,
    ga4_end: params.ga4End,
    ads_date_range: params.adsDateRange,
    campaign_filter: params.campaignFilter || '',
    product_filter: params.productFilter || '',
    selected_item_id: params.selectedItemId || '',
    compare_previous: params.comparePrevious ? 'true' : 'false',
  });
}
