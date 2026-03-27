const severityLabel = {
  high: 'Critic',
  medium: 'Watch',
  low: 'Info',
};

export default function AlertsPanel({ alerts, onExplain, onViewReport }) {
  return (
    <div className="card panel dashboard-panel">
      <div className="dashboard-panel-header">
        <div>
          <h3 className="section-title">Alerts & Opportunities</h3>
          <p className="section-subtitle">Lucrurile care merită atenție imediat.</p>
        </div>
      </div>

      <div className="dashboard-alert-list">
        {alerts?.length ? alerts.map((alert, index) => (
          <div className={`dashboard-alert severity-${alert.severity || 'low'}`} key={`${alert.title}-${index}`}>
            <div className="dashboard-alert-top">
              <div className="dashboard-alert-title">{alert.title}</div>
              <div className={`dashboard-alert-badge severity-${alert.severity || 'low'}`}>
                {severityLabel[alert.severity || 'low'] || 'Info'}
              </div>
            </div>
            <div className="dashboard-alert-detail">{alert.detail}</div>
            <div className="dashboard-inline-actions">
              <button className="dashboard-inline-button" onClick={() => onExplain?.(alert)}>
                Explain this anomaly
              </button>
              {alert.reportAction ? (
                <button className="dashboard-inline-button secondary" onClick={() => onViewReport?.(alert.reportAction)}>
                  Vezi raport complet
                </button>
              ) : null}
            </div>
          </div>
        )) : <div className="dashboard-empty">Nu există alerte în contextul curent.</div>}
      </div>
    </div>
  );
}
