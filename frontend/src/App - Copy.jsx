import { useMemo, useState } from 'react';
import CopilotPanelV3 from './components/CopilotPanelV3';
import FiltersSidebar, { defaultFilters } from './components/layout/FiltersSidebar';

import DashboardPage from './pages/DashboardPage';
import OverviewPage from './pages/OverviewPage';
import GoogleAdsCampaignsPage from './pages/channels/GoogleAdsCampaignsPage';
import MetaCampaignsPage from './pages/channels/MetaCampaignsPage';
import MetaAdSetsPage from './pages/channels/MetaAdSetsPage';
import Ga4TrafficPage from './pages/channels/Ga4TrafficPage';
import FaviPage from './pages/channels/FaviPage';

import Ga4ProductsPage from './pages/products/Ga4ProductsPage';
import GoogleAdsProductsPage from './pages/products/GoogleAdsProductsPage';
import MetaProductsPage from './pages/products/MetaProductsPage';
import ProductChannelsPage from './pages/products/ProductChannelsPage';
import PmaxCampaignProductsPage from './pages/products/PmaxCampaignProductsPage';

import LandingPagesPage from './pages/diagnostics/LandingPagesPage';
import DevicesPage from './pages/diagnostics/DevicesPage';
import JoinAdsGa4Page from './pages/diagnostics/JoinAdsGa4Page';
import PmaxPage from './pages/diagnostics/PmaxPage';
import FunnelCoveragePage from './pages/diagnostics/FunnelCoveragePage';

const topTabs = ['Dashboard', 'Summary', 'Channels', 'Products', 'Diagnostics', 'AI Copilot'];
const channelTabs = ['Google Ads', 'Meta Campaigns', 'Meta Ad Sets', 'GA4 Traffic', 'FAVI'];
const productTabs = ['GA4 Products', 'Google Ads Products', 'Meta Products', 'Product Channels', 'PMAX Campaign Products'];
const diagnosticsTabs = ['Landing Pages', 'GA4 Devices', 'Join Ads + GA4', 'PMAX', 'Funnel Coverage'];

function getCurrentView(activeTab, activeChannelTab, activeProductTab, activeDiagnosticsTab, dashboardContext) {
  if (activeTab === 'Dashboard') return dashboardContext?.currentView || 'Dashboard';
  if (activeTab === 'Channels') return activeChannelTab;
  if (activeTab === 'Products') return activeProductTab;
  if (activeTab === 'Diagnostics') return activeDiagnosticsTab;
  return activeTab;
}

function buildContextSnapshot(activeTab, activeChannelTab, activeProductTab, activeDiagnosticsTab, filters, dashboardContext) {
  const fallbackSummary = [
    { label: 'Ads Cost', value: '0' },
    { label: 'Ads ROAS', value: '0' },
    { label: 'GA4 Views', value: '0' },
    { label: 'GA4 Purchases', value: '0' },
  ];

  const fallbackAnomalies = [
    {
      title: 'Nu există încă alerte generate',
      detail: 'Rulează dashboardul sau schimbă filtrele pentru a trimite mai mult context către copilot.',
      severity: 'low',
    },
  ];

  return {
    currentView: getCurrentView(activeTab, activeChannelTab, activeProductTab, activeDiagnosticsTab, dashboardContext),
    datasetSummary: dashboardContext?.datasetSummary || fallbackSummary,
    topAnomalies: dashboardContext?.topAnomalies || fallbackAnomalies,
    selectedCampaign: filters.campaignFilter || dashboardContext?.selectedCampaign || '',
    selectedProduct: filters.productFilter || dashboardContext?.selectedProduct || '',
    selectedItemId: filters.selectedItemId || dashboardContext?.selectedItemId || '',
    visibleMetrics: dashboardContext?.visibleMetrics || fallbackSummary,
  };
}

export default function App() {
  const [activeTab, setActiveTab] = useState('Dashboard');
  const [activeChannelTab, setActiveChannelTab] = useState('Google Ads');
  const [activeProductTab, setActiveProductTab] = useState('GA4 Products');
  const [activeDiagnosticsTab, setActiveDiagnosticsTab] = useState('Landing Pages');
  const [filters, setFilters] = useState(defaultFilters);
  const [dashboardContext, setDashboardContext] = useState(null);
  const [copilotDraft, setCopilotDraft] = useState('');

  const updateFilter = (key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  const contextSnapshot = useMemo(
    () => buildContextSnapshot(activeTab, activeChannelTab, activeProductTab, activeDiagnosticsTab, filters, dashboardContext),
    [activeTab, activeChannelTab, activeProductTab, activeDiagnosticsTab, filters, dashboardContext]
  );

  const openCopilotWithPrompt = (prompt) => {
    setCopilotDraft(prompt || '');
    setActiveTab('AI Copilot');
  };

  const openDetailedReport = (reportAction) => {
    if (!reportAction) return;
    if (reportAction.tab) {
      setActiveTab(reportAction.tab);
    }
    if (reportAction.subTab && reportAction.tab === 'Products') {
      setActiveProductTab(reportAction.subTab);
    }
    if (reportAction.subTab && reportAction.tab === 'Channels') {
      setActiveChannelTab(reportAction.subTab);
    }
    if (reportAction.subTab && reportAction.tab === 'Diagnostics') {
      setActiveDiagnosticsTab(reportAction.subTab);
    }
  };

  const handleCopilotAction = (action) => {
    switch (action.action) {
      case 'open-products':
        setActiveTab('Products');
        break;
      case 'focus-meta':
        setActiveTab('Channels');
        setActiveChannelTab('Meta Campaigns');
        break;
      case 'focus-mobile':
        setActiveTab('Diagnostics');
        setActiveDiagnosticsTab('GA4 Devices');
        break;
      case 'compare-previous-period':
        setActiveTab('Dashboard');
        setCopilotDraft(action.prompt || 'Compară performanța curentă cu perioada anterioară.');
        break;
      default:
        break;
    }
  };

  return (
    <div className="app-shell">
      <FiltersSidebar filters={filters} onChange={updateFilter} />

      <main className="content">
        <div className="card hero">
          <div className="hero-kicker">Executive dashboard</div>
          <h2 className="hero-title">AI Ads Analyst</h2>
          <div className="hero-subtitle">Dashboard de decizie pentru marketing performance, funnel și insight-uri AI.</div>
        </div>

        <div className="tabs">
          {topTabs.map((tab) => (
            <button
              key={tab}
              className={`tab ${activeTab === tab ? 'active' : ''}`}
              onClick={() => setActiveTab(tab)}
            >
              {tab}
            </button>
          ))}
        </div>

        {activeTab === 'Dashboard' && (
          <DashboardPage
            filters={filters}
            onOpenCopilot={openCopilotWithPrompt}
            onContextChange={setDashboardContext}
            onOpenReport={openDetailedReport}
          />
        )}

        {activeTab === 'Summary' && <OverviewPage filters={filters} />}

        {activeTab === 'Channels' && (
          <>
            <div className="tabs">
              {channelTabs.map((tab) => (
                <button
                  key={tab}
                  className={`tab ${activeChannelTab === tab ? 'active' : ''}`}
                  onClick={() => setActiveChannelTab(tab)}
                >
                  {tab}
                </button>
              ))}
            </div>

            {activeChannelTab === 'Google Ads' && <GoogleAdsCampaignsPage filters={filters} />}
            {activeChannelTab === 'Meta Campaigns' && <MetaCampaignsPage filters={filters} />}
            {activeChannelTab === 'Meta Ad Sets' && <MetaAdSetsPage filters={filters} />}
            {activeChannelTab === 'GA4 Traffic' && <Ga4TrafficPage filters={filters} />}
            {activeChannelTab === 'FAVI' && <FaviPage filters={filters} />}
          </>
        )}

        {activeTab === 'Products' && (
          <>
            <div className="tabs">
              {productTabs.map((tab) => (
                <button
                  key={tab}
                  className={`tab ${activeProductTab === tab ? 'active' : ''}`}
                  onClick={() => setActiveProductTab(tab)}
                >
                  {tab}
                </button>
              ))}
            </div>

            {activeProductTab === 'GA4 Products' && <Ga4ProductsPage filters={filters} />}
            {activeProductTab === 'Google Ads Products' && <GoogleAdsProductsPage filters={filters} />}
            {activeProductTab === 'Meta Products' && <MetaProductsPage filters={filters} />}
            {activeProductTab === 'Product Channels' && <ProductChannelsPage filters={filters} />}
            {activeProductTab === 'PMAX Campaign Products' && <PmaxCampaignProductsPage filters={filters} />}
          </>
        )}

        {activeTab === 'Diagnostics' && (
          <>
            <div className="tabs">
              {diagnosticsTabs.map((tab) => (
                <button
                  key={tab}
                  className={`tab ${activeDiagnosticsTab === tab ? 'active' : ''}`}
                  onClick={() => setActiveDiagnosticsTab(tab)}
                >
                  {tab}
                </button>
              ))}
            </div>

            {activeDiagnosticsTab === 'Landing Pages' && <LandingPagesPage filters={filters} />}
            {activeDiagnosticsTab === 'GA4 Devices' && <DevicesPage filters={filters} />}
            {activeDiagnosticsTab === 'Join Ads + GA4' && <JoinAdsGa4Page filters={filters} />}
            {activeDiagnosticsTab === 'PMAX' && <PmaxPage filters={filters} />}
            {activeDiagnosticsTab === 'Funnel Coverage' && (
              <FunnelCoveragePage
                filters={filters}
                onOpenCopilot={openCopilotWithPrompt}
                onOpenReport={openDetailedReport}
              />
            )}
          </>
        )}

        {activeTab === 'AI Copilot' && (
          <CopilotPanelV3
            filters={filters}
            currentTab={activeTab}
            currentView={contextSnapshot.currentView}
            contextSnapshot={contextSnapshot}
            onApplyAction={handleCopilotAction}
            prefillPrompt={copilotDraft}
          />
        )}
      </main>
    </div>
  );
}
