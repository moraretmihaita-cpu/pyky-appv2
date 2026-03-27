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

function ComparePanel({ comparison }) {
  if (!comparison) return null;
  if (!comparison.available) {
    return (
      <div className="card panel">
        <h3 className="section-title">Comparație cu perioada anterioară</h3>
        <p className="section-subtitle">{comparison.reason || 'Comparația nu este disponibilă pentru intervalele selectate.'}</p>
      </div>
    );
  }

  return (
    <div className="card panel">
      <h3 className="section-title">Comparativ cu perioada anterioară</h3>
      <p className="section-subtitle">
        {comparison.current_label || 'Curent'} vs {comparison.previous_label || 'Anterior'}
      </p>
      {comparison.metrics ? (
        <div className="comparison-metrics-grid">
          {comparison.metrics.map((item) => (
            <div className="comparison-metric-card" key={item.label}>
              <div className="comparison-metric-label">{item.label}</div>
              <div className="comparison-metric-values">
                <div><span className="comparison-kicker">Curent</span> {formatCompareValue(item.current)}</div>
                <div><span className="comparison-kicker">Anterior</span> {formatCompareValue(item.previous)}</div>
              </div>
              <div className={`comparison-delta ${Number(item.delta || 0) >= 0 ? 'is-positive' : 'is-negative'}`}>
                {Number(item.delta || 0) >= 0 ? '+' : ''}{formatCompareValue(item.delta)} ({formatCompareValue(item.delta_pct || 0)}%)
              </div>
            </div>
          ))}
        </div>
      ) : null}
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

          {data.comparison ? <ComparePanel comparison={data.comparison} /> : null}

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
