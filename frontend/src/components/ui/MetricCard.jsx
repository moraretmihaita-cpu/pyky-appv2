function fmt(value) {
  if (value === null || value === undefined || value === '') return '0';
  const n = Number(value);
  if (Number.isFinite(n)) {
    return new Intl.NumberFormat('ro-RO', { maximumFractionDigits: 2 }).format(n);
  }
  return String(value);
}

function DeltaLine({ delta, inverse = false }) {
  if (!delta || delta.pct === null || delta.pct === undefined) return null;
  const pct = Number(delta.pct || 0);
  const abs = Number(delta.abs || 0);
  const isPositive = inverse ? pct < 0 : pct > 0;
  const tone = pct === 0 ? 'neutral' : isPositive ? 'positive' : 'negative';
  const sign = pct > 0 ? '+' : '';
  return (
    <div className={`metric-delta metric-delta-${tone}`}>
      {sign}{fmt(pct)}% ({abs >= 0 ? '+' : ''}{fmt(abs)})
    </div>
  );
}

export default function MetricCard({ label, value, delta, inverse = false }) {
  return (
    <div className="card metric-card">
      <div className="metric-label">{label}</div>
      <div className="metric-value">{fmt(value)}</div>
      <DeltaLine delta={delta} inverse={inverse} />
    </div>
  );
}
