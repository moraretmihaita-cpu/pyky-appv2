import { useCallback } from 'react';
import { fetchMetaAdSets } from '../../lib/api/meta';
import GenericMetricsTablePage from '../../components/shared/GenericMetricsTablePage';

export default function MetaAdSetsPage({ filters }) {
  const loader = useCallback(() => fetchMetaAdSets(filters), [filters]);

  return (
    <GenericMetricsTablePage
      title="Meta Ad Sets"
      subtitle="Ad set-uri Meta conectate la API-ul Python."
      chips={[
        `Meta: ${filters.metaDateRange}`,
        filters.campaignFilter ? `Campanie: ${filters.campaignFilter}` : null,
      ]}
      loader={loader}
      buttonLabel="Reload ad sets"
      metricDefs={[
        { key: 'spend', label: 'Spend' },
        { key: 'purchases', label: 'Purchases' },
        { key: 'value', label: 'Value' },
        { key: 'roas', label: 'ROAS' },
      ]}
      columns={[
        { key: 'campaign_name', label: 'Campanie' },
        { key: 'adset_name', label: 'Ad Set' },
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
