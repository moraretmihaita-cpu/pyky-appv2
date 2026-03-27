import { useCallback, useEffect, useMemo, useState } from 'react';
import { fetchPmaxFeedVsOther } from '../../lib/api/googleAds';
import DataTable from '../../components/DataTable';
import MetricCard from '../../components/ui/MetricCard';
import ErrorBox from '../../components/ui/ErrorBox';
import SectionHeader from '../../components/ui/SectionHeader';
import useRemoteResource from '../../hooks/useRemoteResource';

function useRemote(loader) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [data, setData] = useState(null);

  const load = useCallback(async () => {
    try {
      setLoading(true);
      setError('');
      setData(await loader());
    } catch (err) {
      setError(err.message || 'A apărut o eroare la încărcarea datelor.');
    } finally {
      setLoading(false);
    }
  }, [loader]);

  useEffect(() => {
    load();
  }, [load]);

  return { loading, error, data, load };
}

export default function PmaxPage({ filters }) {
  const chips = useMemo(
    () => [
      `Ads: ${filters.adsDateRange}`,
      filters.campaignFilter ? `Campanie: ${filters.campaignFilter}` : null,
    ].filter(Boolean),
    [filters]
  );

  const loader = useCallback(() => fetchPmaxFeedVsOther(filters), [filters]);
  const { loading, error, data, load } = useRemoteResource(loader);

  return (
    <>
      <SectionHeader
        title="PMAX Feed vs Other"
        subtitle="Estimare feed traffic vs other traffic pentru campaniile PMAX."
        chips={chips}
      />

      <button className="button" onClick={load} disabled={loading}>
        {loading ? 'Loading…' : 'Reload PMAX'}
      </button>

      <ErrorBox error={error} />

      {data ? (
        <>
          <div className="metrics-grid">
            <MetricCard label="Total Clicks" value={data.metrics.total_clicks} />
            <MetricCard label="Product Clicks" value={data.metrics.product_clicks} />
            <MetricCard label="Other Clicks" value={data.metrics.other_clicks} />
            <MetricCard label="Feed Share %" value={data.metrics.feed_share} />
          </div>

          <div className="two-col" style={{ gridTemplateColumns: '1fr 1fr' }}>
            <DataTable
              title="PMAX rows"
              rows={data.rows}
              columns={[
                { key: 'campaign_name', label: 'Campanie' },
                { key: 'total_clicks', label: 'Total Clicks' },
                { key: 'product_clicks_estimate', label: 'Product Clicks' },
                { key: 'other_clicks_estimate', label: 'Other Clicks' },
                { key: 'feed_share_pct', label: 'Feed Share %' },
                { key: 'traffic_profile', label: 'Profile' },
              ]}
            />

            <DataTable
              title="Totals"
              rows={data.totals}
              columns={Object.keys(data.totals?.[0] || {})
                .slice(0, 8)
                .map((key) => ({ key, label: key }))}
            />
          </div>
        </>
      ) : null}
    </>
  );
}
