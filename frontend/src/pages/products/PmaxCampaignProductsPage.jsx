import { useEffect, useMemo, useState } from 'react';
import DataTable from '../../components/DataTable';
import { fetchPmaxCampaignProducts } from '../../lib/api/googleAds';

function toNumber(value) {
  const num = Number(value);
  return Number.isFinite(num) ? num : 0;
}

function formatDecimal(value, digits = 2) {
  const num = Number(value);
  return Number.isFinite(num) ? num.toFixed(digits) : '0.00';
}

function formatInteger(value) {
  const num = Number(value);
  return Number.isFinite(num) ? String(Math.round(num)) : '0';
}

function MetricCard({ label, value }) {
  return (
    <div className="card metric-card">
      <div className="metric-label">{label}</div>
      <div className="metric-value">{value}</div>
    </div>
  );
}

function ErrorBox({ error }) {
  if (!error) return null;
  return <div className="card panel" style={{ color: '#fca5a5' }}>{error}</div>;
}

function MiniInsightCard({ title, value, subtitle }) {
  return (
    <div className="card panel">
      <div style={{ fontSize: 12, color: '#93a4bd', marginBottom: 8 }}>{title}</div>
      <div style={{ fontSize: 24, fontWeight: 700, color: '#f8fafc', marginBottom: 6 }}>{value}</div>
      <div style={{ fontSize: 13, color: '#cbd5e1' }}>{subtitle}</div>
    </div>
  );
}

function SimpleBarChart({ title, rows, valueKey, labelKey, formatter = formatDecimal, emptyMessage }) {
  const maxValue = Math.max(...rows.map((row) => toNumber(row[valueKey])), 0);

  return (
    <div className="card panel">
      <h3 className="section-title">{title}</h3>
      {rows.length === 0 ? (
        <div className="table-placeholder">{emptyMessage || 'Nu există date suficiente.'}</div>
      ) : (
        <div style={{ display: 'grid', gap: 12 }}>
          {rows.map((row, index) => {
            const value = toNumber(row[valueKey]);
            const width = maxValue > 0 ? `${Math.max((value / maxValue) * 100, 4)}%` : '0%';
            const label = row[labelKey] || row.item_id || `Row ${index + 1}`;
            return (
              <div key={`${label}-${index}`}>
                <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, marginBottom: 6 }}>
                  <div style={{ color: '#e5ecf6', fontSize: 13, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={label}>
                    {label}
                  </div>
                  <div style={{ color: '#93a4bd', fontSize: 13, whiteSpace: 'nowrap' }}>{formatter(value)}</div>
                </div>
                <div style={{ height: 10, borderRadius: 999, background: 'rgba(148,163,184,0.12)', overflow: 'hidden' }}>
                  <div
                    style={{
                      width,
                      height: '100%',
                      borderRadius: 999,
                      background: 'linear-gradient(90deg, rgba(96,165,250,0.9), rgba(52,211,153,0.9))',
                    }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default function PmaxCampaignProductsPage({ filters }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [data, setData] = useState(null);
  const [selectedCampaign, setSelectedCampaign] = useState('');

  const load = async (campaignName = selectedCampaign) => {
    try {
      setLoading(true);
      setError('');
      const result = await fetchPmaxCampaignProducts({ ...filters, pmaxCampaignName: campaignName || '' });
      setData(result);
    } catch (err) {
      setError(err.message || 'A apărut o eroare la încărcarea raportului PMAX.');
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load('');
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters.adsDateRange, filters.campaignFilter, filters.productFilter, filters.selectedItemId]);

  const campaigns = data?.campaigns || [];
  const metrics = data?.metrics || {};
  const rawRows = data?.rows || [];

  const chips = useMemo(
    () => [
      `Ads: ${filters.adsDateRange}`,
      `Campaign type: ${data?.campaign_type || 'PERFORMANCE_MAX'}`,
      `Identified by: ${data?.identification_method || 'channel_type'}`,
      selectedCampaign ? `Selected PMAX campaign: ${selectedCampaign}` : null,
      filters.selectedItemId ? `Item ID: ${filters.selectedItemId}` : null,
      filters.productFilter ? `Product filter: ${filters.productFilter}` : null,
    ].filter(Boolean),
    [filters, selectedCampaign, data]
  );

  const displayRows = useMemo(
    () =>
      rawRows.map((row) => ({
        ...row,
        clicks: formatInteger(row.clicks),
        impressions: formatInteger(row.impressions),
        cost: formatDecimal(row.cost),
        conversions: formatDecimal(row.conversions),
        conversion_value: formatDecimal(row.conversion_value),
        ctr: formatDecimal(row.ctr),
        cpc: formatDecimal(row.cpc),
        cpa: formatDecimal(row.cpa),
        roas: formatDecimal(row.roas),
      })),
    [rawRows]
  );

  const displayInsights = useMemo(
    () =>
      (data?.insights || []).map((row) => ({
        ...row,
        cost: formatDecimal(row.cost),
        clicks: formatInteger(row.clicks),
        conversions: formatDecimal(row.conversions),
        roas: formatDecimal(row.roas),
      })),
    [data]
  );

  const topByValue = useMemo(
    () => [...rawRows].sort((a, b) => toNumber(b.conversion_value) - toNumber(a.conversion_value)).slice(0, 8),
    [rawRows]
  );

  const topByCost = useMemo(
    () => [...rawRows].sort((a, b) => toNumber(b.cost) - toNumber(a.cost)).slice(0, 8),
    [rawRows]
  );

  const weakRoasProducts = useMemo(
    () =>
      [...rawRows]
        .filter((row) => toNumber(row.cost) > 0)
        .sort((a, b) => {
          const roasDiff = toNumber(a.roas) - toNumber(b.roas);
          if (roasDiff !== 0) return roasDiff;
          return toNumber(b.cost) - toNumber(a.cost);
        })
        .slice(0, 8),
    [rawRows]
  );

  const watchMetrics = useMemo(() => {
    const spendNoConv = rawRows.filter((row) => toNumber(row.cost) > 0 && toNumber(row.conversions) === 0).length;
    const lowRoas = rawRows.filter((row) => toNumber(row.cost) > 0 && toNumber(row.roas) > 0 && toNumber(row.roas) < 1).length;
    const strongRoas = rawRows.filter((row) => toNumber(row.roas) >= 3).length;

    return { spendNoConv, lowRoas, strongRoas };
  }, [rawRows]);

  return (
    <>
      <div className="card section-card">
        <h2 className="section-title">PMAX Campaign Products</h2>
        <p className="section-subtitle">
          Produse din campaniile Google Ads de tip <strong>PERFORMANCE_MAX</strong>, identificate după <strong>channel_type</strong>, nu după denumirea campaniei.
        </p>
      </div>

      <div className="chips">
        {chips.map((chip) => (
          <div className="chip" key={chip}>{chip}</div>
        ))}
      </div>

      <div className="card panel" style={{ marginBottom: 16 }}>
        <div style={{ display: 'grid', gap: 12, gridTemplateColumns: '2fr 1fr', alignItems: 'end' }}>
          <div>
            <label className="label">Campanie PMAX</label>
            <select
              className="select"
              value={selectedCampaign}
              onChange={(e) => setSelectedCampaign(e.target.value)}
            >
              <option value="">Toate campaniile PMAX</option>
              {campaigns.map((name) => (
                <option key={name} value={name}>{name}</option>
              ))}
            </select>
          </div>
          <button className="button" onClick={() => load(selectedCampaign)} disabled={loading}>
            {loading ? 'Loading…' : 'Rulează raportul PMAX'}
          </button>
        </div>
      </div>

      <ErrorBox error={error || data?.error} />

      {data ? (
        <>
          <div className="metrics-grid">
            <MetricCard label="Cost" value={formatDecimal(metrics.cost)} />
            <MetricCard label="Clicks" value={formatInteger(metrics.clicks)} />
            <MetricCard label="Conversions" value={formatDecimal(metrics.conversions)} />
            <MetricCard label="Value" value={formatDecimal(metrics.value)} />
            <MetricCard label="ROAS" value={formatDecimal(metrics.roas)} />
          </div>

          <div className="metrics-grid metrics-grid-3">
            <MetricCard label="PMAX Campaigns" value={formatInteger(metrics.campaign_count)} />
            <MetricCard label="Products" value={formatInteger(metrics.product_count)} />
            <MetricCard label="Type" value={data.campaign_type || 'PERFORMANCE_MAX'} />
          </div>

          <div className="metrics-grid metrics-grid-3" style={{ marginBottom: 16 }}>
            <MiniInsightCard
              title="Spend fără conversii"
              value={formatInteger(watchMetrics.spendNoConv)}
              subtitle="Produse care consumă buget, dar nu au conversii în intervalul selectat."
            />
            <MiniInsightCard
              title="ROAS sub 1"
              value={formatInteger(watchMetrics.lowRoas)}
              subtitle="Produse care întorc mai puțină valoare decât costul media atribuită."
            />
            <MiniInsightCard
              title="ROAS 3+"
              value={formatInteger(watchMetrics.strongRoas)}
              subtitle="Produse care merită urmărite pentru scalare și asset support."
            />
          </div>

          <div style={{ display: 'grid', gap: 16, gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', marginBottom: 16 }}>
            <SimpleBarChart
              title="Top produse după Value"
              rows={topByValue}
              valueKey="conversion_value"
              labelKey="item_name"
              formatter={(value) => formatDecimal(value)}
            />
            <SimpleBarChart
              title="Top produse după Cost"
              rows={topByCost}
              valueKey="cost"
              labelKey="item_name"
              formatter={(value) => formatDecimal(value)}
            />
            <SimpleBarChart
              title="Produse cu ROAS slab"
              rows={weakRoasProducts}
              valueKey="roas"
              labelKey="item_name"
              formatter={(value) => formatDecimal(value)}
              emptyMessage="Nu există produse eligibile pentru analiza de ROAS."
            />
          </div>

          <DataTable
            title="PMAX campaign products"
            rows={displayRows}
            columns={[
              { key: 'campaign_name', label: 'Campanie' },
              { key: 'item_id', label: 'Item ID' },
              { key: 'item_name', label: 'Produs' },
              { key: 'clicks', label: 'Clicks' },
              { key: 'impressions', label: 'Impresii' },
              { key: 'cost', label: 'Cost' },
              { key: 'conversions', label: 'Conversii' },
              { key: 'conversion_value', label: 'Value' },
              { key: 'ctr', label: 'CTR %' },
              { key: 'cpc', label: 'CPC' },
              { key: 'cpa', label: 'CPA' },
              { key: 'roas', label: 'ROAS' },
            ]}
          />

          <DataTable
            title="PMAX product insights"
            rows={displayInsights}
            columns={[
              { key: 'type', label: 'Tip insight' },
              { key: 'campaign_name', label: 'Campanie' },
              { key: 'item_id', label: 'Item ID' },
              { key: 'item_name', label: 'Produs' },
              { key: 'cost', label: 'Cost' },
              { key: 'clicks', label: 'Clicks' },
              { key: 'conversions', label: 'Conversii' },
              { key: 'roas', label: 'ROAS' },
              { key: 'message', label: 'Mesaj' },
            ]}
          />
        </>
      ) : null}
    </>
  );
}
