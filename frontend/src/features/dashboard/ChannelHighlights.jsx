function HighlightTable({ title, rows, columns, emptyText }) {
  const template = columns.map((column) => column.width || 'minmax(0, 1fr)').join(' ');

  return (
    <div className="card panel dashboard-panel">
      <div className="dashboard-panel-header compact">
        <h3 className="section-title">{title}</h3>
      </div>
      {rows?.length ? (
        <div className="dashboard-mini-table">
          <div className="dashboard-mini-head" style={{ gridTemplateColumns: template }}>
            {columns.map((column) => <div key={column.key}>{column.label}</div>)}
          </div>
          {rows.map((row, index) => (
            <div className="dashboard-mini-row" style={{ gridTemplateColumns: template }} key={`${title}-${index}`}>
              {columns.map((column) => <div key={column.key}>{row[column.key] ?? '-'}</div>)}
            </div>
          ))}
        </div>
      ) : <div className="dashboard-empty">{emptyText}</div>}
    </div>
  );
}

export default function ChannelHighlights({ topRoas, problemProducts }) {
  return (
    <div className="dashboard-bottom-grid">
      <HighlightTable
        title="Top products by ROAS"
        rows={(topRoas || []).slice(0, 5)}
        columns={[
          { key: 'product_name', label: 'Produs', width: 'minmax(220px, 2fr)' },
          { key: 'ads_roas', label: 'ROAS', width: '96px' },
          { key: 'cost', label: 'Cost', width: '110px' },
        ]}
        emptyText="Nu există produse cu ROAS în contextul curent."
      />
      <HighlightTable
        title="Products that need attention"
        rows={(problemProducts || []).slice(0, 5)}
        columns={[
          { key: 'product_name', label: 'Produs', width: 'minmax(220px, 2.2fr)' },
          { key: 'item_id', label: 'Item ID', width: '92px' },
          { key: 'campaign_name', label: 'Campanie', width: 'minmax(180px, 1.5fr)' },
          { key: 'cost', label: 'Cost', width: '110px' },
          { key: 'conversions', label: 'Conversii', width: '96px' },
        ]}
        emptyText="Nu există produse problematice în contextul curent."
      />
    </div>
  );
}
