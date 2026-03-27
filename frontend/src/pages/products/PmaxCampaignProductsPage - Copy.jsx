import { useEffect, useMemo, useState } from 'react';
import DataTable from '../../components/DataTable';
import { fetchPmaxCampaignProducts } from '../../lib/api/googleAds';

function formatInteger(value) {
  const num = Number(value);
  if (!Number.isFinite(num)) return 0;
  return Math.round(num);
}

function formatDecimal(value, digits = 2) {
  const num = Number(value);
  if (!Number.isFinite(num)) return (0).toFixed(digits);
  return num.toFixed(digits);
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

function decorateRow(row) {
  return {
    ...row,
    clicks: formatInteger(row?.clicks),
    impressions: formatInteger(row?.impressions),
    cost: formatDecimal(row?.cost),
    conversions: formatDecimal(row?.conversions),
    conversion_value: formatDecimal(row?.conversion_value),
    ctr: formatDecimal(row?.ctr),
    cpc: formatDecimal(row?.cpc),
    cpa: formatDecimal(row?.cpa),
    roas: formatDecimal(row?.roas),
  };
}

function decorateInsight(row) {
  return {
    ...row,
    cost: formatDecimal(row?.cost),
    clicks: formatInteger(row?.clicks),
    conversions: formatDecimal(row?.conversions),
    roas: formatDecimal(row?.roas),
  };
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
      const result = await fetchPmaxCampaignProducts({
        ...filters,
        pmaxCampaignName: campaignName || '',
      });
      setData(result);
    } catch (err) {
      setError(err.message || 'A apărut o eroare la încărcarea raportului PMAX.');
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setSelectedCampaign('');
    load('');
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters.adsDateRange, filters.campaignFilter, filters.productFilter, filters.selectedItemId]);

  const campaigns = data?.campaigns || [];
  const metrics = data?.metrics || {};

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

  const formattedRows = useMemo(
    () => (data?.rows || []).map(decorateRow),
    [data]
  );

  const formattedInsights = useMemo(
    () => (data?.insights || []).map(decorateInsight),
    [data]
  );

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

          <DataTable
            title="PMAX campaign products"
            rows={formattedRows}
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
            rows={formattedInsights}
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
