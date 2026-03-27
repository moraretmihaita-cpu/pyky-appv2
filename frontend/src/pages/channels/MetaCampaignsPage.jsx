import { useCallback } from 'react';
import { fetchMetaCampaigns } from '../../lib/api/meta';
import GenericMetricsTablePage from '../../components/shared/GenericMetricsTablePage';

export default function MetaCampaignsPage({ filters }) {
  const loader = useCallback(() => fetchMetaCampaigns(filters), [filters]);

  return (
    <GenericMetricsTablePage
      title="Meta Campaigns"
      subtitle="Campanii Meta conectate la API-ul Python."
      chips={[
        `Meta: ${filters.metaDateRange}`,
        filters.campaignFilter ? `Campanie: ${filters.campaignFilter}` : null,
      ]}
      loader={loader}
      buttonLabel="Reload campaigns"
      metricDefs={[
        { key: 'spend', label: 'Spend' },
        { key: 'purchases', label: 'Purchases' },
        { key: 'value', label: 'Value' },
        { key: 'roas', label: 'ROAS' },
      ]}
      columns={[
        { key: 'campaign_name', label: 'Campanie' },
        { key: 'impressions', label: 'Impresii' },
        { key: 'clicks', label: 'Clickuri' },
        { key: 'spend', label: 'Spend' },
        { key: 'purchases', label: 'Purchases' },
        { key: 'purchase_value', label: 'Value' },
        { key: 'ctr', label: 'CTR %' },
        { key: 'cpc', label: 'CPC' },
        { key: 'cpa', label: 'CPA' },
        { key: 'roas', label: 'ROAS' },
      ]}
    />
  );
}
