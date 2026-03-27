import { useCallback } from 'react';
import { fetchGa4Devices } from '../../lib/api/ga4';
import GenericMetricsTablePage from '../../components/shared/GenericMetricsTablePage';

export default function DevicesPage({ filters }) {
  const loader = useCallback(() => fetchGa4Devices(filters), [filters]);

  return (
    <GenericMetricsTablePage
      title="GA4 Devices"
      subtitle="Performanță pe device din GA4."
      chips={[`GA4: ${filters.ga4Start} → ${filters.ga4End}`]}
      loader={loader}
      buttonLabel="Reload devices"
      metricDefs={[
        { key: 'sessions', label: 'Sessions' },
        { key: 'engaged_sessions', label: 'Engaged' },
        { key: 'purchases', label: 'Purchases' },
        { key: 'revenue', label: 'Revenue' },
      ]}
      columns={[
        { key: 'device', label: 'Device' },
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
