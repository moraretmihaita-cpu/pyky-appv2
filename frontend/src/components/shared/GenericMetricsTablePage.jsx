import DataTable from '../DataTable';
import MetricCard from '../ui/MetricCard';
import ErrorBox from '../ui/ErrorBox';
import SectionHeader from '../ui/SectionHeader';
import useRemoteResource from '../../hooks/useRemoteResource';

function formatCompareValue(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return value ?? '-';
  const num = Number(value);
  return Number.isInteger(num) ? String(num) : num.toFixed(2);
}

function ComparePanel({ comparison, metricDefs }) {
  if (!comparison) return null;
  if (!comparison.available) {
    return (
      <div className="card panel">
        <h3 className="section-title">Comparație cu perioada anterioară</h3>
        <p className="section-subtitle">{comparison.reason || 'Comparația nu este disponibilă pentru intervalele selectate.'}</p>
      </div>
    );
  }

  const currentLabel = comparison.current_ga4_range || comparison.current_ads_range || comparison.current_meta_range || comparison.current_label || 'Curent';
  const previousLabel = comparison.previous_ga4_range || comparison.previous_ads_range || comparison.previous_meta_range || comparison.previous_label || 'Anterior';

  const deltas = metricDefs
    .map((metric) => ({
      metric,
      delta: comparison.metric_deltas?.[metric.key],
    }))
    .filter((x) => x.delta);

  return (
    <div className="card panel">
      <h3 className="section-title">Comparativ cu perioada anterioară</h3>
      <p className="section-subtitle">
        {currentLabel} vs {previousLabel}
      </p>
      <div className="comparison-metrics-grid">
        {deltas.map(({ metric, delta }) => {
          const current = delta.current;
          const previous = delta.previous;
          const abs = Number(delta.abs || 0);
          const pct = Number(delta.pct || 0);
          const positive = pct === 0 ? true : abs >= 0;
          return (
            <div className="comparison-metric-card" key={metric.key}>
              <div className="comparison-metric-label">{metric.label}</div>
              <div className="comparison-metric-values">
                <div><span className="comparison-kicker">Curent</span> {formatCompareValue(current)}</div>
                <div><span className="comparison-kicker">Anterior</span> {formatCompareValue(previous)}</div>
              </div>
              <div className={`comparison-delta ${positive ? 'is-positive' : 'is-negative'}`}>
                {abs >= 0 ? '+' : ''}{formatCompareValue(abs)} ({formatCompareValue(pct)}%)
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default function GenericMetricsTablePage({
  title,
  subtitle,
  chips,
  loader,
  buttonLabel,
  metricDefs,
  columns,
}) {
  const { loading, error, data, load } = useRemoteResource(loader);

  return (
    <>
      <SectionHeader title={title} subtitle={subtitle} chips={chips} />

      <button className="button" onClick={load} disabled={loading}>
        {loading ? 'Loading…' : buttonLabel}
      </button>

      <ErrorBox error={error} />

      {data ? (
        <>
          <div className="metrics-grid">
            {metricDefs.map((metric) => (
              <MetricCard
                key={metric.key}
                label={metric.label}
                value={data.metrics?.[metric.key]}
                delta={data.comparison?.metric_deltas?.[metric.key]}
                inverse={!!metric.inverse}
              />
            ))}
          </div>

          {data.comparison ? <ComparePanel comparison={data.comparison} metricDefs={metricDefs} /> : null}

          <DataTable
            title={`${title} rows`}
            rows={data.rows || []}
            columns={columns}
          />
        </>
      ) : null}
    </>
  );
}
