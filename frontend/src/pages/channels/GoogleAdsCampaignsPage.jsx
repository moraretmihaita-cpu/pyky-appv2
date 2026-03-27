import { useCallback } from 'react';
import { fetchGoogleAdsCampaigns } from '../../lib/api/googleAds';
import GenericMetricsTablePage from '../../components/shared/GenericMetricsTablePage';

export default function GoogleAdsCampaignsPage({ filters }) {
  const loader = useCallback(() => fetchGoogleAdsCampaigns(filters), [filters]);

  return (
    <GenericMetricsTablePage
      title="Google Ads Campaigns"
      subtitle="Campanii conectate la API-ul Python."
      chips={[
        `Ads: ${filters.adsDateRange}`,
        filters.campaignFilter ? `Campanie: ${filters.campaignFilter}` : null,
      ]}
      loader={loader}
      buttonLabel="Reload campaigns"
      metricDefs={[
        { key: 'cost', label: 'Cost' },
        { key: 'conversions', label: 'Conversions' },
        { key: 'value', label: 'Value' },
        { key: 'roas', label: 'ROAS' },
      ]}
      columns={[
        { key: 'campaign_name', label: 'Campanie' },
        { key: 'impressions', label: 'Impresii' },
        { key: 'clicks', label: 'Clickuri' },
        { key: 'cost', label: 'Cost' },
        { key: 'conversions', label: 'Conversii' },
        { key: 'conversion_value', label: 'Valoare' },
        { key: 'ctr', label: 'CTR %' },
        { key: 'cpa', label: 'CPA' },
        { key: 'roas', label: 'ROAS' },
      ]}
    />
  );
}
