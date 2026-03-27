
function MetricDelta({ value, inverse = false }) {
  if (!value || (value.pct === null || value.pct === undefined)) return null;
  const normalized = Number(value.pct);
  const sign = normalized > 0 ? '+' : '';
  const good = inverse ? normalized < 0 : normalized > 0;
  const tone = normalized === 0 ? 'neutral' : good ? 'positive' : 'negative';
  return <div className={`metric-delta ${tone}`}>{sign}{normalized}% vs anterior</div>;
}

function MetricCard({ label, value, helper, delta, inverse = false }) {
  return (
    <div className="card metric-card dashboard-metric-card">
      <div className="metric-label">{label}</div>
      <div className="metric-value">{value}</div>
      {helper ? <div className="metric-helper">{helper}</div> : null}
      <MetricDelta value={delta} inverse={inverse} />
    </div>
  );
}

export default function ExecutiveMetrics({ metrics, rates, metricDeltas = {} }) {
  const cards = [
    { label: 'Ads Cost', value: metrics.ads_cost, helper: 'Buget consumat', delta: metricDeltas.ads_cost, inverse: true },
    { label: 'Ads Value', value: metrics.ads_value, helper: 'Valoare conversii', delta: metricDeltas.ads_value },
    { label: 'ROAS', value: metrics.ads_roas, helper: 'Randament media', delta: metricDeltas.ads_roas },
    { label: 'GA4 Views', value: metrics.ga4_views, helper: 'Interes pe produse', delta: metricDeltas.ga4_views },
    { label: 'Add To Cart', value: metrics.ga4_add_to_cart, helper: 'Semnal de intenție', delta: metricDeltas.ga4_add_to_cart },
    { label: 'Purchases', value: metrics.ga4_purchases, helper: 'Conversii finale', delta: metricDeltas.ga4_purchases },
    { label: 'View → ATC', value: `${rates.viewToCartRate}%`, helper: 'Conversie produs' },
    { label: 'View → Purchase', value: `${rates.viewToPurchaseRate}%`, helper: 'Eficiență finală' },
  ];

  return (
    <div className="metrics-grid dashboard-metrics-grid">
      {cards.map((card) => (
        <MetricCard key={card.label} {...card} />
      ))}
    </div>
  );
}
