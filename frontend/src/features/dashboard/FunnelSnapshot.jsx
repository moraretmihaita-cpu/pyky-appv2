function toNumber(value) {
  const num = Number(value || 0);
  return Number.isFinite(num) ? num : 0;
}

export default function FunnelSnapshot({ funnel, rates }) {
  const views = toNumber(funnel?.find((step) => step.label === 'Views')?.value);
  const addToCart = toNumber(funnel?.find((step) => step.label === 'Add To Cart')?.value);
  const purchases = toNumber(funnel?.find((step) => step.label === 'Purchases')?.value);
  const total = Math.max(views + addToCart + purchases, 1);

  const viewsAngle = (views / total) * 360;
  const cartAngle = ((views + addToCart) / total) * 360;

  const pieStyle = {
    background: `conic-gradient(
      rgba(96, 165, 250, 0.95) 0deg ${viewsAngle}deg,
      rgba(52, 211, 153, 0.95) ${viewsAngle}deg ${cartAngle}deg,
      rgba(251, 191, 36, 0.95) ${cartAngle}deg 360deg
    )`,
  };

  const steps = [
    { label: 'Views', value: views, tone: 'views' },
    { label: 'Add To Cart', value: addToCart, tone: 'cart' },
    { label: 'Purchases', value: purchases, tone: 'purchase' },
  ];

  return (
    <div className="card panel dashboard-panel">
      <div className="dashboard-panel-header">
        <div>
          <h3 className="section-title">Funnel Snapshot</h3>
          <p className="section-subtitle">Unde se transformă interesul în acțiune.</p>
        </div>
      </div>

      <div className="funnel-chart-layout">
        <div className="funnel-pie-card">
          <div className="funnel-pie" style={pieStyle}>
            <div className="funnel-pie-hole">
              <div className="funnel-pie-hole-label">Purchase rate</div>
              <div className="funnel-pie-hole-value">{rates.viewToPurchaseRate}%</div>
            </div>
          </div>

          <div className="funnel-legend">
            {steps.map((step) => (
              <div className="funnel-legend-item" key={step.label}>
                <span className={`funnel-legend-dot ${step.tone}`} />
                <span className="funnel-legend-label">{step.label}</span>
                <strong className="funnel-legend-value">{step.value}</strong>
              </div>
            ))}
          </div>
        </div>

        <div>
          <div className="funnel-grid compact">
            {steps.map((step) => (
              <div className="funnel-step" key={step.label}>
                <div className="funnel-step-label">{step.label}</div>
                <div className="funnel-step-value">{step.value}</div>
              </div>
            ))}
          </div>

          <div className="funnel-rates">
            <div className="funnel-rate-card">
              <div className="funnel-rate-label">View → Add To Cart</div>
              <div className="funnel-rate-value">{rates.viewToCartRate}%</div>
            </div>
            <div className="funnel-rate-card">
              <div className="funnel-rate-label">Add To Cart → Purchase</div>
              <div className="funnel-rate-value">{rates.cartToPurchaseRate}%</div>
            </div>
            <div className="funnel-rate-card">
              <div className="funnel-rate-label">View → Purchase</div>
              <div className="funnel-rate-value">{rates.viewToPurchaseRate}%</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
