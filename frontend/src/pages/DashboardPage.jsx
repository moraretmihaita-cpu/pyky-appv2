
import { useEffect, useMemo } from 'react';
import { fetchOverview } from '../lib/api/overview';
import useRemoteResource from '../hooks/useRemoteResource';
import ExecutiveMetrics from '../features/dashboard/ExecutiveMetrics';
import AlertsPanel from '../features/dashboard/AlertsPanel';
import FunnelSnapshot from '../features/dashboard/FunnelSnapshot';
import AiInsightsPanel from '../features/dashboard/AiInsightsPanel';
import ChannelHighlights from '../features/dashboard/ChannelHighlights';

function fmt(num) {
  if (num === null || num === undefined) return '0';
  if (typeof num !== 'number') return String(num);
  return new Intl.NumberFormat('ro-RO', { maximumFractionDigits: 2 }).format(num);
}

function deriveRates(metrics) {
  const views = Number(metrics.ga4_views || 0);
  const atc = Number(metrics.ga4_add_to_cart || 0);
  const purchases = Number(metrics.ga4_purchases || 0);
  return {
    viewToCartRate: views ? ((atc / views) * 100).toFixed(2) : '0.00',
    cartToPurchaseRate: atc ? ((purchases / atc) * 100).toFixed(2) : '0.00',
    viewToPurchaseRate: views ? ((purchases / views) * 100).toFixed(2) : '0.00',
  };
}

function deriveAlerts(overview, comparison) {
  const alerts = [];
  const metrics = overview.metrics || {};
  const deltas = comparison?.metric_deltas || {};
  const problemProducts = overview.problem_products || [];
  const topRoas = overview.top_roas || [];

  if ((metrics.ads_cost || 0) > 0 && (metrics.ads_roas || 0) < 3) {
    const roasDelta = deltas.ads_roas?.pct;
    alerts.push({
      title: 'ROAS general sub pragul dorit',
      detail: `ROAS-ul total este ${fmt(metrics.ads_roas)} la un cost de ${fmt(metrics.ads_cost)}.${roasDelta !== undefined && roasDelta !== null ? ` Trend vs anterior: ${roasDelta > 0 ? '+' : ''}${fmt(roasDelta)}%.` : ''}`,
      severity: 'high',
      reportAction: { tab: 'Products', subTab: 'Google Ads Products' },
    });
  }

  if ((problemProducts || []).length) {
    const first = problemProducts[0];
    alerts.push({
      title: `${problemProducts.length} produse consumă cost fără conversii`,
      detail: `${first.product_name || 'Un produs'} este primul semnal și a consumat ${fmt(first.cost)} fără conversii vizibile.`,
      severity: 'high',
      reportAction: { tab: 'Products', subTab: 'GA4 Products' },
    });
  }

  if ((metrics.ga4_views || 0) > 0 && Number(deriveRates(metrics).viewToCartRate) < 2) {
    alerts.push({
      title: 'View → Add To Cart este slab',
      detail: `Rata actuală este ${deriveRates(metrics).viewToCartRate}%, ceea ce poate indica o problemă de ofertă, preț sau UX.`,
      severity: 'medium',
      reportAction: { tab: 'Diagnostics', subTab: 'Funnel Coverage' },
    });
  }

  if ((topRoas || []).length) {
    const best = topRoas[0];
    alerts.push({
      title: 'Există produse care merită scalate',
      detail: `${best.product_name || 'Un produs'} are ROAS ${fmt(best.ads_roas)} și poate fi o oportunitate pentru buget suplimentar.`,
      severity: 'low',
      reportAction: { tab: 'Products', subTab: 'Product Channels' },
    });
  }

  return alerts.slice(0, 4);
}

function deriveAiInsights(overview, rates, comparison) {
  const metrics = overview.metrics || {};
  const problemProducts = overview.problem_products || [];
  const topRoas = overview.top_roas || [];
  const roasDelta = comparison?.metric_deltas?.ads_roas?.pct;
  return [
    {
      title: 'Unde este cea mai mare oportunitate',
      body: topRoas.length
        ? `Primele produse după ROAS arată că există cerere deja validată. Merită verificată scalarea bugetului pentru performerii buni.`
        : 'Nu există încă un performer evident. Merită analizate canalele și produsele individual.',
    },
    {
      title: 'Unde pare să se rupă funnel-ul',
      body: Number(rates.viewToCartRate) < 2
        ? `Frâna principală pare între view și add to cart. Asta sugerează problemă pe pagină, ofertă sau calitatea traficului.`
        : `Funnel-ul de produs nu pare blocat sever între view și add to cart în contextul curent.`,
    },
    {
      title: 'Ce trebuie investigat azi',
      body: problemProducts.length
        ? `Începe cu produsele care au cost semnificativ și zero conversii. Acolo pierderea de eficiență e cea mai vizibilă.`
        : `Nu există pierderi evidente în produse. Poți trece pe comparație între canale și devices.`,
    },
    {
      title: 'Rezumat executiv',
      body: `Cost ${fmt(metrics.ads_cost)}, valoare ${fmt(metrics.ads_value)}, ROAS ${fmt(metrics.ads_roas)} și ${fmt(metrics.ga4_purchases)} purchases în perioada curentă.${roasDelta !== undefined && roasDelta !== null ? ` ROAS vs anterior: ${roasDelta > 0 ? '+' : ''}${fmt(roasDelta)}%.` : ''}`,
    },
  ];
}

function humanizePeriodPreset(periodPreset) {
  const map = {
    LAST_7_DAYS: 'Last 7 days',
    LAST_30_DAYS: 'Last 30 days',
    THIS_MONTH: 'This month',
    LAST_MONTH: 'Last month',
    CUSTOM_RANGE: 'Custom range',
  };
  return map[periodPreset] || periodPreset || 'Last period';
}

export default function DashboardPage({ filters, onOpenCopilot, onContextChange, onOpenReport }) {
  const { loading, error, data, load } = useRemoteResource(() => fetchOverview(filters), [JSON.stringify(filters)]);

  const metrics = data?.metrics || {
    ads_cost: 0,
    ads_value: 0,
    ads_roas: 0,
    ga4_views: 0,
    ga4_add_to_cart: 0,
    ga4_purchases: 0,
  };
  const funnel = data?.funnel || [
    { label: 'Views', value: 0 },
    { label: 'Add To Cart', value: 0 },
    { label: 'Purchases', value: 0 },
  ];
  const comparison = data?.comparison || { available: false, metric_deltas: {} };

  const rates = useMemo(() => deriveRates(metrics), [metrics]);
  const alerts = useMemo(() => (data ? deriveAlerts(data, comparison) : []), [data, comparison]);
  const insights = useMemo(() => (data ? deriveAiInsights(data, rates, comparison) : []), [data, rates, comparison]);

  useEffect(() => {
    if (!data || !onContextChange) return;
    onContextChange({
      currentView: 'Dashboard',
      datasetSummary: [
        { label: 'Ads Cost', value: fmt(metrics.ads_cost) },
        { label: 'Ads Value', value: fmt(metrics.ads_value) },
        { label: 'ROAS', value: fmt(metrics.ads_roas) },
        { label: 'GA4 Purchases', value: fmt(metrics.ga4_purchases) },
      ],
      topAnomalies: alerts,
      visibleMetrics: [
        { label: 'View → ATC', value: `${rates.viewToCartRate}%` },
        { label: 'ATC → Purchase', value: `${rates.cartToPurchaseRate}%` },
        { label: 'View → Purchase', value: `${rates.viewToPurchaseRate}%` },
      ],
      selectedCampaign: filters.campaignFilter || '',
      selectedProduct: filters.productFilter || '',
      selectedItemId: filters.selectedItemId || '',
    });
  }, [data, onContextChange, alerts, rates, metrics, filters]);

  const chips = [
    `Period: ${humanizePeriodPreset(filters.periodPreset)}${filters.periodPreset === 'CUSTOM_RANGE' ? ` (${filters.ga4Start} → ${filters.ga4End})` : ''}`,
    filters.comparePrevious ? 'Compare: activ' : null,
    filters.campaignFilter ? `Campanie: ${filters.campaignFilter}` : null,
    filters.productFilter ? `Produs: ${filters.productFilter}` : null,
  ].filter(Boolean);

  return (
    <>
      <div className="card section-card dashboard-hero-card">
        <h2 className="section-title">Marketing Performance Dashboard</h2>
        <p className="section-subtitle">Ecranul principal de decizie: performanță, alerte, funnel și insight-uri AI într-un singur loc.</p>
      </div>

      <div className="chips">
        {chips.map((chip) => <div className="chip" key={chip}>{chip}</div>)}
      </div>

      <button className="button" onClick={() => load().catch(() => {})} disabled={loading}>
        {loading ? 'Loading…' : 'Refresh dashboard'}
      </button>

      {error ? <div className="card panel dashboard-error">{error}</div> : null}

      {comparison.available ? (
        <div className="card panel compare-panel dashboard-compare-panel">
          <div className="compare-strip-title">Compare activ</div>
          <div className="compare-strip-body">Ads: {comparison.current_ads_range} vs {comparison.previous_ads_range} · GA4: {comparison.current_ga4_start} → {comparison.current_ga4_end} vs {comparison.previous_ga4_start} → {comparison.previous_ga4_end}</div>
        </div>
      ) : null}

      <ExecutiveMetrics metrics={{
        ads_cost: fmt(metrics.ads_cost),
        ads_value: fmt(metrics.ads_value),
        ads_roas: fmt(metrics.ads_roas),
        ga4_views: fmt(metrics.ga4_views),
        ga4_add_to_cart: fmt(metrics.ga4_add_to_cart),
        ga4_purchases: fmt(metrics.ga4_purchases),
      }} rates={rates} metricDeltas={comparison.metric_deltas || {}} />

      <div className="dashboard-main-grid">
        <AlertsPanel
          alerts={alerts}
          onExplain={(alert) => onOpenCopilot?.(`Explain this anomaly: ${alert.title}. ${alert.detail}`)}
          onViewReport={onOpenReport}
        />
        <AiInsightsPanel
          insights={insights}
          onOpenCopilot={() => onOpenCopilot?.('Rezuma dashboardul actual și spune-mi ce trebuie făcut azi.')}
          onActionPlan={() => onOpenCopilot?.('Generează un action plan pentru dashboardul curent, cu priorități și impact estimat.')}
        />
      </div>

      <FunnelSnapshot funnel={funnel} rates={rates} />

      <ChannelHighlights topRoas={data?.top_roas || []} problemProducts={data?.problem_products || []} />
    </>
  );
}
