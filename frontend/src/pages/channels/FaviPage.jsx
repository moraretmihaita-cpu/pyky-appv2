import { useCallback, useMemo } from 'react';
import { fetchFaviReport } from '../../lib/api/ga4';
import DataTable from '../../components/DataTable';
import MetricCard from '../../components/ui/MetricCard';
import ErrorBox from '../../components/ui/ErrorBox';
import SectionHeader from '../../components/ui/SectionHeader';
import useRemoteResource from '../../hooks/useRemoteResource';

export default function FaviPage({ filters }) {
  const loader = useCallback(() => fetchFaviReport(filters), [filters]);
  const { loading, error, data, load } = useRemoteResource(loader);

  const chips = useMemo(
    () => [
      `GA4: ${filters.ga4Start} → ${filters.ga4End}`,
      data?.source_medium ? `Source: ${data.source_medium}` : 'Source: favi.ro / cpc',
      filters.productFilter ? `Produs: ${filters.productFilter}` : null,
      `Tip pagină: ${filters.pageType}`,
    ],
    [data?.source_medium, filters]
  );

  return (
    <>
      <SectionHeader
        title="FAVI"
        subtitle="Raport GA4 dedicat sursei favi.ro / cpc."
        chips={chips}
      />

      <button className="button" onClick={load} disabled={loading}>
        {loading ? 'Loading…' : 'Reload FAVI'}
      </button>

      <ErrorBox error={error} />

      {data ? (
        <>
          <div className="metrics-grid">
            <MetricCard
              label="Sessions"
              value={data.overview.sessions}
              delta={data.comparison?.metric_deltas?.sessions}
            />
            <MetricCard
              label="Purchases"
              value={data.overview.purchases}
              delta={data.comparison?.metric_deltas?.purchases}
            />
            <MetricCard
              label="Revenue"
              value={data.overview.revenue}
              delta={data.comparison?.metric_deltas?.revenue}
            />
            <MetricCard
              label="Purchase rate %"
              value={data.overview.purchase_rate}
              delta={data.comparison?.metric_deltas?.purchase_rate}
            />
          </div>

          <div className="metrics-grid metrics-grid-3">
            <MetricCard
              label="Engaged sessions"
              value={data.overview.engaged_sessions}
              delta={data.comparison?.metric_deltas?.engaged_sessions}
            />
            <MetricCard
              label="Engagement rate %"
              value={data.overview.engagement_rate}
              delta={data.comparison?.metric_deltas?.engagement_rate}
            />
            <MetricCard
              label="Revenue / session"
              value={data.overview.revenue_per_session}
              delta={data.comparison?.metric_deltas?.revenue_per_session}
            />
          </div>

          <div className="two-col" style={{ gridTemplateColumns: '1fr 1fr' }}>
            <DataTable
              title="FAVI products"
              rows={data.products}
              columns={[
                { key: 'item_name', label: 'Produs' },
                { key: 'item_id', label: 'Item ID' },
                { key: 'items_viewed', label: 'Views' },
                { key: 'items_added_to_cart', label: 'Add To Cart' },
                { key: 'items_purchased', label: 'Purchases' },
                { key: 'item_revenue', label: 'Revenue' },
                { key: 'purchase_rate', label: 'Purchase Rate %' },
              ]}
            />

            <DataTable
              title="FAVI landing pages"
              rows={data.landing_pages}
              columns={[
                { key: 'landing_page', label: 'Landing Page' },
                { key: 'sessions', label: 'Sessions' },
                { key: 'engaged_sessions', label: 'Engaged' },
                { key: 'purchases', label: 'Purchases' },
                { key: 'purchase_revenue', label: 'Revenue' },
              ]}
            />
          </div>
        </>
      ) : null}
    </>
  );
}
