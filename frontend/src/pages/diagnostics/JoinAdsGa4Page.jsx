import { useCallback, useMemo } from 'react';
import { fetchJoinAdsGa4 } from '../../lib/api/diagnostics';
import DataTable from '../../components/DataTable';
import MetricCard from '../../components/ui/MetricCard';
import ErrorBox from '../../components/ui/ErrorBox';
import SectionHeader from '../../components/ui/SectionHeader';
import useRemoteResource from '../../hooks/useRemoteResource';

export default function JoinAdsGa4Page({ filters }) {
  const chips = useMemo(
    () => [
      `GA4: ${filters.ga4Start} → ${filters.ga4End}`,
      `Ads: ${filters.adsDateRange}`,
      filters.campaignFilter ? `Campanie: ${filters.campaignFilter}` : null,
      filters.productFilter ? `Produs: ${filters.productFilter}` : null,
    ].filter(Boolean),
    [filters]
  );

  const loader = useCallback(() => fetchJoinAdsGa4(filters), [filters]);
  const { loading, error, data, load } = useRemoteResource(loader);

  return (
    <>
      <SectionHeader
        title="Join Ads + GA4"
        subtitle="Raport principal de produse combinând Ads și GA4."
        chips={chips}
      />

      <button className="button" onClick={load} disabled={loading}>
        {loading ? 'Loading…' : 'Reload joined report'}
      </button>

      <ErrorBox error={error} />

      {data ? (
        <>
          <div className="metrics-grid">
            <MetricCard
              label="Products"
              value={data.metrics.products}
              delta={data.comparison?.metric_deltas?.products}
            />
            <MetricCard
              label="Problematic"
              value={data.metrics.problematic}
              delta={data.comparison?.metric_deltas?.problematic}
            />
            <MetricCard
              label="Atenție"
              value={data.metrics.attention}
              delta={data.comparison?.metric_deltas?.attention}
            />
            <MetricCard
              label="Bun"
              value={data.metrics.good}
              delta={data.comparison?.metric_deltas?.good}
            />
          </div>

          <div className="two-col" style={{ gridTemplateColumns: '1.4fr 1fr' }}>
            <DataTable
              title="Joined rows"
              rows={data.rows}
              columns={[
                { key: 'join_item_id', label: 'Item ID' },
                { key: 'product_name', label: 'Produs' },
                { key: 'status', label: 'Status' },
                { key: 'clicks', label: 'Clickuri' },
                { key: 'cost', label: 'Cost' },
                { key: 'ads_roas', label: 'ROAS' },
                { key: 'ga4_views_google_cpc', label: 'Views G/CPC' },
                { key: 'ga4_purchases_google_cpc', label: 'Purchases G/CPC' },
              ]}
            />

            <DataTable
              title="AI-style insights"
              rows={data.insights}
              columns={Object.keys(data.insights?.[0] || {})
                .slice(0, 6)
                .map((key) => ({ key, label: key }))}
            />
          </div>
        </>
      ) : null}
    </>
  );
}
