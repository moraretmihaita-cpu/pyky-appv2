import { useCallback } from 'react';
import { fetchGa4Traffic } from '../../lib/api/ga4';
import GenericMetricsTablePage from '../../components/shared/GenericMetricsTablePage';

export default function Ga4TrafficPage({ filters }) {
  const loader = useCallback(() => fetchGa4Traffic(filters), [filters]);

  return (
    <GenericMetricsTablePage
      title="GA4 Traffic"
      subtitle="Surse și campanii GA4 conectate la API-ul Python."
      chips={[
        `GA4: ${filters.ga4Start} → ${filters.ga4End}`,
        `Tip trafic: ${filters.trafficType}`,
        filters.campaignFilter ? `Campanie: ${filters.campaignFilter}` : null,
      ]}
      loader={loader}
      buttonLabel="Reload traffic"
      metricDefs={[
        { key: 'sessions', label: 'Sessions' },
        { key: 'engaged_sessions', label: 'Engaged' },
        { key: 'purchases', label: 'Purchases' },
        { key: 'revenue', label: 'Revenue' },
      ]}
      columns={[
        { key: 'source_medium', label: 'Source / Medium' },
        { key: 'campaign_name', label: 'Campanie' },
        { key: 'sessions', label: 'Sessions' },
        { key: 'engaged_sessions', label: 'Engaged' },
        { key: 'engagement_rate', label: 'Engagement %' },
        { key: 'purchases', label: 'Purchases' },
        { key: 'purchase_revenue', label: 'Revenue' },
        { key: 'revenue_per_session', label: 'Revenue / Session' },
      ]}
    />
  );
}
