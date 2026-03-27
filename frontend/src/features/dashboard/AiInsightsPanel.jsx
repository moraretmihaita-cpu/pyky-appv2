export default function AiInsightsPanel({ insights, onOpenCopilot, onActionPlan }) {
  return (
    <div className="card panel dashboard-panel">
      <div className="dashboard-panel-header">
        <div>
          <h3 className="section-title">AI Insights Center</h3>
          <p className="section-subtitle">Rezumat orientat pe decizie și acțiune.</p>
        </div>
        <button className="dashboard-inline-button" onClick={onOpenCopilot}>Open Copilot</button>
      </div>

      <div className="dashboard-insights-list">
        {insights?.map((insight, index) => (
          <div className="dashboard-insight" key={`${insight.title}-${index}`}>
            <div className="dashboard-insight-title">{insight.title}</div>
            <div className="dashboard-insight-body">{insight.body}</div>
          </div>
        ))}
      </div>

      <div className="dashboard-panel-actions">
        <button className="button" onClick={onActionPlan}>Generate action plan</button>
      </div>
    </div>
  );
}
