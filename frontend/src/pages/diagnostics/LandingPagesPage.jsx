import { useCallback } from 'react';
import { fetchGa4LandingPages } from '../../lib/api/ga4';
import GenericMetricsTablePage from '../../components/shared/GenericMetricsTablePage';

export default function LandingPagesPage({ filters }) {
  const loader = useCallback(() => fetchGa4LandingPages(filters), [filters]);

  return (
    <GenericMetricsTablePage
      title="Landing Pages"
      subtitle="Landing pages GA4 conectate la API-ul Python."
      chips={[
        `GA4: ${filters.ga4Start} → ${filters.ga4End}`,
        `Tip pagină: ${filters.pageType}`,
      ]}
      loader={loader}
      buttonLabel="Reload landing pages"
      metricDefs={[
        { key: 'sessions', label: 'Sessions' },
        { key: 'engaged_sessions', label: 'Engaged' },
        { key: 'purchases', label: 'Purchases' },
        { key: 'revenue', label: 'Revenue' },
      ]}
      columns={[
        { key: 'landing_page', label: 'Landing Page' },
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
