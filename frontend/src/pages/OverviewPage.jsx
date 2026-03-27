
import { useCallback, useMemo } from 'react';
import { fetchOverview } from '../lib/api/overview';
import DataTable from '../components/DataTable';
import ErrorBox from '../components/ui/ErrorBox';
import SectionHeader from '../components/ui/SectionHeader';
import useRemoteResource from '../hooks/useRemoteResource';

function fmt(value) {
  if (value === null || value === undefined || value === '') return '0';
  const n = Number(value);
  if (Number.isFinite(n)) {
    return new Intl.NumberFormat('ro-RO', { maximumFractionDigits: 2 }).format(n);
  }
  return String(value);
}

function DeltaBadge({ delta, inverse = false }) {
  if (!delta || (delta.pct === null || delta.pct === undefined)) {
    return <div className="compare-delta neutral">Fără comparație disponibilă</div>;
  }
  const pct = Number(delta.pct || 0);
  const isPositive = inverse ? pct < 0 : pct > 0;
  const tone = pct === 0 ? 'neutral' : isPositive ? 'positive' : 'negative';
  const sign = pct > 0 ? '+' : '';
  return <div className={`compare-delta ${tone}`}>{sign}{pct}% vs perioada anterioară</div>;
}

function CompareMetricCard({ label, value, delta, inverse = false }) {
  return (
    <div className="card metric-card compare-metric-card">
      <div className="metric-label">{label}</div>
      <div className="metric-value">{fmt(value)}</div>
      <DeltaBadge delta={delta} inverse={inverse} />
    </div>
  );
}

function humanizePeriodPreset(periodPreset) {
  const map = {
    LAST_7_DAYS: 'Last 7 days',
    LAST_30_DAYS: 'Last 30 days',
    THIS_MONTH: 'This month',
    LAST_MONTH: 'Last month',
    CUSTOM_RANGE: 'Custom range',
  };
  return map[periodPreset] || periodPreset || 'Last period';
}

export default function OverviewPage({ filters }) {
  const chips = useMemo(
    () =>
      [
        `Period: ${humanizePeriodPreset(filters.periodPreset)}${filters.periodPreset === 'CUSTOM_RANGE' ? ` (${filters.ga4Start} → ${filters.ga4End})` : ''}`,
        filters.comparePrevious ? 'Compare: activ' : null,
        filters.campaignFilter ? `Campanie: ${filters.campaignFilter}` : null,
        filters.productFilter ? `Produs: ${filters.productFilter}` : null,
      ].filter(Boolean),
    [filters]
  );

  const loader = useCallback(() => fetchOverview(filters), [filters]);
  const { loading, error, data, load } = useRemoteResource(loader);
  const comparison = data?.comparison || { available: false, metric_deltas: {} };

  return (
    <>
      <SectionHeader
        title="Executive Summary"
        subtitle="Overview conectat la backend Python prin API real."
        chips={chips}
      />

      <button className="button" onClick={load} disabled={loading}>
        {loading ? 'Loading…' : 'Run overview'}
      </button>

      <ErrorBox error={error} />

      {data ? (
        <>
          <div className="metrics-grid">
            <CompareMetricCard label="Ads Cost" value={data.metrics.ads_cost} delta={comparison.metric_deltas?.ads_cost} inverse />
            <CompareMetricCard label="Ads Conversions" value={data.metrics.ads_conversions} delta={comparison.metric_deltas?.ads_conversions} />
            <CompareMetricCard label="Ads Value" value={data.metrics.ads_value} delta={comparison.metric_deltas?.ads_value} />
            <CompareMetricCard label="Ads ROAS" value={data.metrics.ads_roas} delta={comparison.metric_deltas?.ads_roas} />
          </div>

          <div className="metrics-grid metrics-grid-3">
            <CompareMetricCard label="GA4 Views" value={data.metrics.ga4_views} delta={comparison.metric_deltas?.ga4_views} />
            <CompareMetricCard label="GA4 Add To Cart" value={data.metrics.ga4_add_to_cart} delta={comparison.metric_deltas?.ga4_add_to_cart} />
            <CompareMetricCard label="GA4 Purchases" value={data.metrics.ga4_purchases} delta={comparison.metric_deltas?.ga4_purchases} />
          </div>

          {comparison.available ? (
            <div className="card panel compare-panel">
              <h3 className="section-title">Compare snapshot</h3>
              <p className="section-subtitle">
                Ads: {comparison.current_ads_range} vs {comparison.previous_ads_range} · GA4: {comparison.current_ga4_start} → {comparison.current_ga4_end} vs {comparison.previous_ga4_start} → {comparison.previous_ga4_end}
              </p>
            </div>
          ) : null}

          <div className="two-col">
            <div className="card panel">
              <h3 className="section-title">Funnel snapshot</h3>
              <ul>
                {data.funnel.map((step) => (
                  <li key={step.label}>
                    {step.label}: {fmt(step.value)}
                  </li>
                ))}
              </ul>
            </div>

            <div className="card panel">
              <h3 className="section-title">API status</h3>
              <p className="section-subtitle">
                Frontend consolidat pe un singur client API.
              </p>
            </div>
          </div>

          <div className="two-col" style={{ gridTemplateColumns: '1fr 1fr' }}>
            <DataTable
              title="Top produse după ROAS"
              rows={data.top_roas}
              columns={[
                { key: 'product_name', label: 'Produs' },
                { key: 'ads_roas', label: 'ROAS' },
                { key: 'cost', label: 'Cost' },
                { key: 'conversions', label: 'Conversii' },
                { key: 'status', label: 'Status' },
              ]}
            />

            <DataTable
              title="Produse problematice"
              rows={data.problem_products}
              columns={[
                { key: 'product_name', label: 'Produs' },
                { key: 'item_id', label: 'Item ID' },
                { key: 'campaign_name', label: 'Campanie' },
                { key: 'cost', label: 'Cost' },
                { key: 'conversions', label: 'Conversii' },
                { key: 'status', label: 'Status' },
              ]}
            />
          </div>
        </>
      ) : null}
    </>
  );
}
