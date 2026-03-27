import { useCallback, useMemo } from 'react';
import { fetchFunnelCoverage } from '../../api.client';
import useRemoteResource from '../../hooks/useRemoteResource';
import MetricCard from '../../components/ui/MetricCard';
import ErrorBox from '../../components/ui/ErrorBox';
import SectionHeader from '../../components/ui/SectionHeader';
import DataTable from '../../components/DataTable';

function formatValue(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return value ?? '-';
  const num = Number(value);
  return Number.isInteger(num) ? String(num) : num.toFixed(2);
}

function stageClass(stage) {
  const key = String(stage || '').toUpperCase();
  if (key === 'TOF') return 'stage-badge stage-badge-tof';
  if (key === 'MOF') return 'stage-badge stage-badge-mof';
  if (key === 'BOF') return 'stage-badge stage-badge-bof';
  return 'stage-badge';
}

function buildPieGradient(items) {
  const colors = ['#60a5fa', '#22c55e', '#f59e0b', '#f472b6', '#a78bfa', '#38bdf8'];
  const total = items.reduce((sum, item) => sum + Number(item.value || 0), 0);
  if (!total) {
    return 'conic-gradient(rgba(148,163,184,0.28) 0deg 360deg)';
  }

  let current = 0;
  const segments = items.map((item, index) => {
    const value = Number(item.value || 0);
    const angle = (value / total) * 360;
    const start = current;
    const end = current + angle;
    current = end;
    return `${colors[index % colors.length]} ${start}deg ${end}deg`;
  });

  return `conic-gradient(${segments.join(', ')})`;
}

function PieCard({ title, subtitle, items }) {
  const total = items.reduce((sum, item) => sum + Number(item.value || 0), 0);
  const gradient = buildPieGradient(items);

  return (
    <div className="card panel funnel-pie-card">
      <div className="funnel-pie-header">
        <h3 className="section-title">{title}</h3>
        <p className="section-subtitle">{subtitle}</p>
      </div>
      <div className="funnel-pie-layout">
        <div className="funnel-pie" style={{ background: gradient }}>
          <div className="funnel-pie-hole">
            <div className="funnel-pie-hole-label">Total</div>
            <div className="funnel-pie-hole-value">{formatValue(total)}</div>
          </div>
        </div>
        <div className="funnel-pie-legend">
          {items.map((item, index) => (
            <div className="funnel-pie-legend-row" key={`${item.label}-${index}`}>
              <div className="funnel-pie-dot" style={{ background: ['#60a5fa', '#22c55e', '#f59e0b', '#f472b6', '#a78bfa', '#38bdf8'][index % 6] }} />
              <div className="funnel-pie-label-group">
                <div className="funnel-pie-label">{item.label}</div>
                <div className="funnel-pie-subvalue">{formatValue(item.value)}</div>
              </div>
              <div className="funnel-pie-share">
                {total ? `${((Number(item.value || 0) / total) * 100).toFixed(1)}%` : '0.0%'}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}


function ComparisonMetricCards({ comparison }) {
  if (!comparison?.available || !comparison.metrics?.length) {
    return (
      <div className="card panel">
        <h3 className="section-title">Comparație cu perioada anterioară</h3>
        <p className="section-subtitle">{comparison?.reason || 'Comparația nu este disponibilă pentru intervalele selectate.'}</p>
      </div>
    );
  }

  return (
    <div className="card panel">
      <div className="comparison-header">
        <div>
          <h3 className="section-title">Comparativ cu perioada anterioară</h3>
          <p className="section-subtitle">
            Ads: {comparison.current_ads_range} vs {comparison.previous_ads_range || 'n/a'} · Meta: {comparison.current_meta_range} vs {comparison.previous_meta_range || 'n/a'}
          </p>
        </div>
      </div>
      <div className="comparison-metrics-grid">
        {comparison.metrics.map((item) => {
          const delta = Number(item.delta || 0);
          const positive = delta >= 0;
          return (
            <div className="comparison-metric-card" key={item.label}>
              <div className="comparison-metric-label">{item.label}</div>
              <div className="comparison-metric-values">
                <div><span className="comparison-kicker">Curent</span> {formatValue(item.current)}</div>
                <div><span className="comparison-kicker">Anterior</span> {formatValue(item.previous)}</div>
              </div>
              <div className={`comparison-delta ${positive ? 'is-positive' : 'is-negative'}`}>
                {positive ? '▲' : '▼'} {formatValue(Math.abs(delta))} ({formatValue(Math.abs(item.delta_pct || 0))}%)
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function ComparisonTable({ title, subtitle, rows }) {
  return (
    <div className="card panel">
      <h3 className="section-title">{title}</h3>
      <p className="section-subtitle">{subtitle}</p>
      {!rows?.length ? (
        <div className="table-placeholder">Nu există date pentru comparație.</div>
      ) : (
        <div className="comparison-table">
          <div className="comparison-table-head">
            <div>Grup</div>
            <div>Curent</div>
            <div>Anterior</div>
            <div>Delta</div>
          </div>
          {rows.map((row) => {
            const delta = Number(row.delta || 0);
            const maxValue = Math.max(...rows.map((r) => Math.max(Number(r.current || 0), Number(r.previous || 0))), 1);
            const currentWidth = `${Math.max((Number(row.current || 0) / maxValue) * 100, 4)}%`;
            const previousWidth = `${Math.max((Number(row.previous || 0) / maxValue) * 100, 4)}%`;
            return (
              <div className="comparison-table-row" key={row.label}>
                <div className="comparison-row-label">{row.label}</div>
                <div>
                  <div className="comparison-bar-track">
                    <div className="comparison-bar comparison-bar-current" style={{ width: currentWidth }} />
                  </div>
                  <div className="comparison-bar-value">{formatValue(row.current)}</div>
                </div>
                <div>
                  <div className="comparison-bar-track">
                    <div className="comparison-bar comparison-bar-previous" style={{ width: previousWidth }} />
                  </div>
                  <div className="comparison-bar-value">{formatValue(row.previous)}</div>
                </div>
                <div className={`comparison-delta ${delta >= 0 ? 'is-positive' : 'is-negative'}`}>
                  {delta >= 0 ? '+' : ''}{formatValue(delta)} ({formatValue(row.delta_pct || 0)}%)
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

function deriveReportAction(text = '') {
  const lower = String(text).toLowerCase();
  if (lower.includes('meta')) return { tab: 'Channels', subTab: 'Meta Campaigns' };
  if (lower.includes('google')) return { tab: 'Channels', subTab: 'Google Ads' };
  if (lower.includes('pmax') || lower.includes('performance max')) return { tab: 'Products', subTab: 'PMAX Campaign Products' };
  if (lower.includes('bof') || lower.includes('conversion') || lower.includes('remarketing')) return { tab: 'Products', subTab: 'Google Ads Products' };
  return { tab: 'Diagnostics', subTab: 'Funnel Coverage' };
}

function RecommendationCards({ items, onOpenCopilot, onOpenReport }) {
  if (!items?.length) {
    return <div className="card panel table-placeholder">Nu există recomandări.</div>;
  }

  return (
    <div className="funnel-rec-grid">
      {items.map((item, idx) => {
        const prompt = `Diagnose funnel issue: ${item.gap}. Recommendation: ${item.recommendation}`;
        return (
          <div className="card panel funnel-rec-card" key={`${item.gap}-${idx}`}>
            <div className="funnel-rec-top">
              <span className={`priority-chip priority-${String(item.priority || '').toLowerCase()}`}>{item.priority || 'Info'}</span>
              <span className="funnel-rec-gap">{item.gap}</span>
            </div>
            <p className="funnel-rec-text">{item.recommendation}</p>
            <div className="funnel-action-row">
              <button className="button button-secondary" onClick={() => onOpenReport?.(deriveReportAction(`${item.gap} ${item.recommendation}`))}>
                Vezi raport relevant
              </button>
              <button className="button" onClick={() => onOpenCopilot?.(prompt)}>
                Explain in Copilot
              </button>
            </div>
          </div>
        );
      })}
    </div>
  );
}

function CampaignActionList({ campaigns, onOpenCopilot, onOpenReport }) {
  const topCampaigns = [...(campaigns || [])]
    .sort((a, b) => Number(b.spend || 0) - Number(a.spend || 0))
    .slice(0, 8);

  return (
    <div className="card panel">
      <h3 className="section-title">Campanii de verificat rapid</h3>
      <p className="section-subtitle">Cele mai relevante campanii după spend, cu acces rapid spre analiză și raport.</p>
      {!topCampaigns.length ? (
        <div className="table-placeholder">Nu există campanii pentru acțiuni rapide.</div>
      ) : (
        <div className="funnel-quick-list">
          {topCampaigns.map((row, idx) => {
            const prompt = `Explain campaign in funnel context: ${row.campaign_name}. Platform: ${row.platform}. Stage: ${row.funnel_stage}. Signal: ${row.signal}. Stage reason: ${row.stage_reason}. Spend: ${row.spend}. Conversions: ${row.primary_conversions}. ROAS: ${row.roas}.`;
            return (
              <div className="funnel-quick-row" key={`${row.campaign_name}-${idx}`}>
                <div className="funnel-quick-main">
                  <div className="funnel-quick-title">{row.campaign_name}</div>
                  <div className="funnel-quick-meta">
                    <span className="chip chip-inline">{row.platform}</span>
                    <span className={stageClass(row.funnel_stage)}>{row.funnel_stage}</span>
                    <span className="chip chip-inline">Spend {formatValue(row.spend)}</span>
                    <span className="chip chip-inline">ROAS {formatValue(row.roas)}</span>
                  </div>
                  <div className="funnel-quick-reason">{row.stage_reason}</div>
                </div>
                <div className="funnel-action-column">
                  <button className="button button-secondary" onClick={() => onOpenReport?.(deriveReportAction(`${row.platform} ${row.funnel_stage} ${row.signal}`))}>
                    Vezi raport
                  </button>
                  <button className="button" onClick={() => onOpenCopilot?.(prompt)}>
                    Explain in Copilot
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default function FunnelCoveragePage({ filters, onOpenCopilot, onOpenReport }) {
  const chips = useMemo(
    () => [
      `Ads: ${filters.adsDateRange}`,
      `Meta: ${filters.metaDateRange}`,
      filters.campaignFilter ? `Campanie: ${filters.campaignFilter}` : null,
    ].filter(Boolean),
    [filters]
  );

  const loader = useCallback(() => fetchFunnelCoverage(filters), [filters]);
  const { loading, error, data, load } = useRemoteResource(loader, [JSON.stringify(filters)]);

  const metrics = data?.metrics || {
    active_campaigns: 0,
    covered_stages: 0,
    total_spend: 0,
    total_conversions: 0,
    total_value: 0,
  };

  const stageDistribution = useMemo(() => {
    const summary = data?.summary || [];
    const map = new Map();
    summary.forEach((row) => {
      const key = String(row.funnel_stage || 'Other');
      const value = Number(row.spend || 0);
      map.set(key, (map.get(key) || 0) + value);
    });
    return ['TOF', 'MOF', 'BOF'].map((stage) => ({ label: stage, value: map.get(stage) || 0 }));
  }, [data]);

  const platformDistribution = useMemo(() => {
    const summary = data?.summary || [];
    const map = new Map();
    summary.forEach((row) => {
      const key = String(row.platform || 'Other');
      const value = Number(row.spend || 0);
      map.set(key, (map.get(key) || 0) + value);
    });
    return Array.from(map.entries()).map(([label, value]) => ({ label, value }));
  }, [data]);

  const topSignals = useMemo(() => {
    const campaigns = data?.campaigns || [];
    return [...campaigns]
      .sort((a, b) => Number(b.spend || 0) - Number(a.spend || 0))
      .slice(0, 10)
      .map((row) => ({
        ...row,
        funnel_stage_badge: row.funnel_stage,
      }));
  }, [data]);

  return (
    <>
      <SectionHeader
        title="Funnel Coverage"
        subtitle="Campanii active din Google Ads și Meta, clasificate în principal pe semnalele structurate din API."
        chips={chips}
      />

      <div className="card panel">
        <div className="section-subtitle">
          Google Ads este clasificat după <strong>advertising_channel_type</strong> / raw enum ID mapat, iar Meta după <strong>objective</strong>. campaign_name rămâne doar fallback.
        </div>
      </div>

      <button className="button" onClick={load} disabled={loading}>
        {loading ? 'Loading…' : 'Refresh funnel coverage'}
      </button>

      <ErrorBox error={error || data?.error} />

      {data ? (
        <>
          <div className="metrics-grid metrics-grid-4">
            <MetricCard label="Campanii active" value={metrics.active_campaigns} />
            <MetricCard label="Stage-uri acoperite" value={`${metrics.covered_stages}/3`} />
            <MetricCard label="Spend total" value={metrics.total_spend} />
            <MetricCard label="Conversii totale" value={metrics.total_conversions} />
          </div>

          <ComparisonMetricCards comparison={data.comparison} />

          <div className="two-col funnel-overview-grid" style={{ gridTemplateColumns: '1fr 1fr', alignItems: 'start' }}>
            <ComparisonTable
              title="Spend pe stage: curent vs anterior"
              subtitle="Vezi rapid dacă bugetul s-a mutat între TOF, MOF și BOF."
              rows={data.comparison?.stage_spend || []}
            />
            <ComparisonTable
              title="Spend pe platformă: curent vs anterior"
              subtitle="Comparație simplă între Google Ads și Meta față de perioada anterioară."
              rows={data.comparison?.platform_spend || []}
            />
          </div>

          <div className="two-col funnel-overview-grid" style={{ gridTemplateColumns: '1fr 1fr', alignItems: 'start' }}>
            <PieCard
              title="Distribuție spend pe stage"
              subtitle="Vezi rapid dacă bugetul stă prea mult în TOF sau lipsește din BOF."
              items={stageDistribution}
            />
            <PieCard
              title="Distribuție spend pe platformă"
              subtitle="Comparație simplă între Google Ads și Meta în funnel."
              items={platformDistribution}
            />
          </div>

          <div className="two-col funnel-overview-grid" style={{ gridTemplateColumns: '1.05fr 0.95fr', alignItems: 'start' }}>
            <DataTable
              title="Matrix funnel"
              rows={data.matrix || []}
              columns={[
                { key: 'stage', label: 'Stage' },
                { key: 'google_ads_status', label: 'Google status' },
                { key: 'google_ads_campaigns', label: 'Google campaigns' },
                { key: 'google_ads_spend', label: 'Google spend' },
                { key: 'meta_ads_status', label: 'Meta status' },
                { key: 'meta_ads_campaigns', label: 'Meta campaigns' },
                { key: 'meta_ads_spend', label: 'Meta spend' },
                { key: 'overall_status', label: 'Overall status' },
                { key: 'total_active_campaigns', label: 'Total campaigns' },
                { key: 'total_spend', label: 'Total spend' },
              ]}
            />

            <div>
              <RecommendationCards
                items={data.recommendations || []}
                onOpenCopilot={onOpenCopilot}
                onOpenReport={onOpenReport}
              />
            </div>
          </div>

          <CampaignActionList
            campaigns={data.campaigns || []}
            onOpenCopilot={onOpenCopilot}
            onOpenReport={onOpenReport}
          />

          <DataTable
            title="Rezumat pe platformă și stage"
            rows={data.summary || []}
            columns={[
              { key: 'platform', label: 'Platformă' },
              { key: 'funnel_stage', label: 'Stage' },
              { key: 'active_campaigns', label: 'Campanii active' },
              { key: 'impressions', label: 'Impresii' },
              { key: 'clicks', label: 'Clickuri' },
              { key: 'spend', label: 'Spend' },
              { key: 'conversions', label: 'Conversii' },
              { key: 'conversion_value', label: 'Valoare conversii' },
              { key: 'ctr', label: 'CTR %' },
              { key: 'cpa', label: 'CPA' },
              { key: 'roas', label: 'ROAS' },
            ]}
          />

          <DataTable
            title="Campanii clasificate în funnel"
            rows={topSignals}
            columns={[
              { key: 'platform', label: 'Platformă' },
              { key: 'funnel_stage', label: 'Stage' },
              { key: 'campaign_name', label: 'Campanie' },
              { key: 'signal', label: 'Semnal API' },
              { key: 'stage_reason', label: 'Motiv clasificare' },
              { key: 'impressions', label: 'Impresii' },
              { key: 'clicks', label: 'Clickuri' },
              { key: 'spend', label: 'Spend' },
              { key: 'primary_conversions', label: 'Conversii' },
              { key: 'primary_value', label: 'Valoare conversii' },
              { key: 'ctr', label: 'CTR %' },
              { key: 'cpa', label: 'CPA' },
              { key: 'roas', label: 'ROAS' },
            ]}
          />
        </>
      ) : null}
    </>
  );
}
