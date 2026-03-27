import { getJson } from './client';

export async function fetchGoogleAdsCampaigns(params) {
  return getJson('/api/google-ads/campaigns', {
    ads_date_range: params.adsDateRange,
    campaign_filter: params.campaignFilter || '',
    compare_previous: params.comparePrevious ? 'true' : 'false',
  });
}

export async function fetchGoogleAdsProducts(params) {
  return getJson('/api/google-ads/products', {
    ads_date_range: params.adsDateRange,
    campaign_filter: params.campaignFilter || '',
    product_filter: params.productFilter || '',
    selected_item_id: params.selectedItemId || '',
    compare_previous: params.comparePrevious ? 'true' : 'false',
  });
}

export async function fetchPmaxFeedVsOther(params) {
  return getJson('/api/pmax-feed-vs-other', {
    ads_date_range: params.adsDateRange,
    campaign_filter: params.campaignFilter || '',
    compare_previous: params.comparePrevious ? 'true' : 'false',
  });
}

export async function fetchPmaxCampaignProducts(params) {
  return getJson('/api/google-ads/pmax-campaign-products', {
    ads_date_range: params.adsDateRange,
    campaign_filter: params.campaignFilter || '',
    product_filter: params.productFilter || '',
    selected_item_id: params.selectedItemId || '',
    pmax_campaign: params.pmaxCampaignName || '',
    asset_group: params.assetGroupName || '',
    compare_previous: params.comparePrevious ? 'true' : 'false',
  });
}
