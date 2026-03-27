import { useEffect, useMemo, useState } from 'react';
import { fetchAiProviders, sendCopilotMessage } from '../lib/api/copilot';

const COPILOT_MODES = [
  { id: 'Explain', label: 'Explain', hint: 'Explică ce se întâmplă' },
  { id: 'Diagnose', label: 'Diagnose', hint: 'Găsește problema' },
  { id: 'Recommend', label: 'Recommend', hint: 'Spune ce acțiuni să fac' },
  { id: 'Compare', label: 'Compare', hint: 'Compară perioade, canale sau produse' },
];

function normalizeSections(content) {
  const template = {
    Summary: '',
    Evidence: '',
    'Probable cause': '',
    'Recommended actions': '',
    'Estimated impact': '',
    Confidence: '',
  };

  if (!content) return template;
  let activeKey = 'Summary';
  const lines = String(content).split(/\r?\n/);
  for (const rawLine of lines) {
    const line = rawLine.trim();
    const match = line.match(/^(Summary|Evidence|Probable cause|Recommended actions|Estimated impact|Confidence)\s*:\s*(.*)$/i);
    if (match) {
      const key = Object.keys(template).find((item) => item.toLowerCase() === match[1].toLowerCase()) || 'Summary';
      activeKey = key;
      if (match[2]) template[key] += (template[key] ? '\n' : '') + match[2].trim();
      continue;
    }
    if (line) {
      template[activeKey] += (template[activeKey] ? '\n' : '') + line;
    }
  }
  return template;
}

function SuggestedPromptButtons({ prompts, onSelect }) {
  if (!prompts?.length) return null;
  return (
    <div className="copilot-suggestions">
      {prompts.map((prompt) => (
        <button key={prompt} className="chip copilot-suggestion" onClick={() => onSelect(prompt)}>
          {prompt}
        </button>
      ))}
    </div>
  );
}

function QuickActions({ actions, onAction }) {
  if (!actions?.length) return null;
  return (
    <div className="copilot-quick-actions">
      {actions.map((action) => (
        <button key={action.id} className="copilot-quick-action" onClick={() => onAction(action)}>
          {action.label}
        </button>
      ))}
    </div>
  );
}

function AssistantMessage({ message, onAction }) {
  const sections = normalizeSections(message.content);
  return (
    <div
      style={{
        padding: '12px 14px',
        borderRadius: 14,
        border: '1px solid rgba(148,163,184,0.16)',
        background: 'rgba(255,255,255,0.03)',
      }}
    >
      <div style={{ fontSize: 12, color: '#93a4bd', marginBottom: 10, fontWeight: 700 }}>
        AI Copilot
      </div>

      <div className="copilot-message-grid">
        {Object.entries(sections)
          .filter(([, value]) => value)
          .map(([title, value]) => (
            <div className="copilot-message-card" key={title}>
              <div className="copilot-message-title">{title}</div>
              <div className="copilot-message-body">{value}</div>
            </div>
          ))}
      </div>

      {message.provider || message.model ? (
        <div style={{ marginTop: 8, fontSize: 12, color: '#93a4bd' }}>
          {message.provider || 'provider'} · {message.model || 'model'}
        </div>
      ) : null}
      {message.toolsUsed?.length ? (
        <div style={{ marginTop: 6, fontSize: 12, color: '#93a4bd' }}>
          Tool-uri folosite: {message.toolsUsed.join(', ')}
        </div>
      ) : null}
      <QuickActions actions={message.quickActions} onAction={onAction} />
    </div>
  );
}

export default function CopilotPanelV3({ filters, currentTab, currentView, contextSnapshot, onApplyAction, prefillPrompt = "" }) {
  const [providers, setProviders] = useState([]);
  const [provider, setProvider] = useState('openai');
  const [model, setModel] = useState('');
  const [mode, setMode] = useState('Diagnose');
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content:
        'Summary: Sunt copilotul intern al aplicației.\nEvidence: Pot folosi doar datele și tool-urile interne.\nProbable cause: Momentan nu am încă o întrebare concretă.\nRecommended actions: Alege un mod de lucru și una dintre întrebările sugerate.\nEstimated impact: Timp mai mic până la insight.\nConfidence: ridicată.',
      toolsUsed: [],
      provider: null,
      model: null,
      quickActions: [],
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!prefillPrompt) return;
    setInput(prefillPrompt);
  }, [prefillPrompt]);

  useEffect(() => {
    const loadProviders = async () => {
      try {
        const items = await fetchAiProviders();
        setProviders(items || []);
        const firstConfigured = (items || []).find((p) => p.configured) || (items || [])[0];
        if (firstConfigured) {
          setProvider(firstConfigured.id);
          setModel(firstConfigured.default_model || firstConfigured.models?.[0] || '');
        }
      } catch (err) {
        setError(err.message || 'Nu am putut încărca providerii AI.');
      }
    };
    loadProviders();
  }, []);

  const selectedProvider = useMemo(
    () => providers.find((p) => p.id === provider) || null,
    [providers, provider]
  );

  useEffect(() => {
    if (!selectedProvider) return;
    const candidate = selectedProvider.models?.includes(model)
      ? model
      : selectedProvider.default_model || selectedProvider.models?.[0] || '';
    setModel(candidate);
  }, [provider, selectedProvider]);

  const modePrompts = useMemo(() => {
    const viewLabel = currentView || currentTab || 'zona curentă';
    const selectedProduct = filters.productFilter || contextSnapshot?.selectedProduct;
    const selectedCampaign = filters.campaignFilter || contextSnapshot?.selectedCampaign;
    const selectedItem = filters.selectedItemId || contextSnapshot?.selectedItemId;

    const base = {
      Explain: [
        `Explică-mi ce se întâmplă în ${viewLabel}.`,
        `Rezuma performanța curentă pentru ${viewLabel} și filtrele active.`,
        selectedProduct ? `Explică performanța produsului ${selectedProduct}.` : `Explică principalele schimbări din ${viewLabel}.`,
      ],
      Diagnose: [
        `Unde este problema principală în ${viewLabel}?`,
        selectedCampaign ? `Diagnostichează campania ${selectedCampaign}.` : `Care este cauza probabilă a scăderii performanței?`,
        selectedItem ? `Ce anomalie vezi pentru item ID ${selectedItem}?` : `Ce anomalie merită investigată prima?`,
      ],
      Recommend: [
        `Ce acțiuni concrete recomanzi pentru ${viewLabel}?`,
        `Generează un plan de optimizare pentru perioada curentă.`,
        `Care sunt primele 3 acțiuni cu impact mare și efort mic?`,
      ],
      Compare: [
        `Compară performanța curentă cu perioada anterioară.`,
        `Compară Google Ads cu Meta pentru filtrele active.`,
        selectedProduct ? `Compară produsul ${selectedProduct} cu restul portofoliului.` : `Compară cele mai relevante surse sau canale.`,
      ],
    };

    return base[mode] || [];
  }, [mode, currentView, currentTab, filters, contextSnapshot]);

  const proactiveAlerts = useMemo(() => {
    return (contextSnapshot?.topAnomalies || []).slice(0, 4);
  }, [contextSnapshot]);

  const quickActionTemplates = useMemo(() => {
    const selectedProduct = filters.productFilter || contextSnapshot?.selectedProduct || 'produsul afectat';
    return [
      {
        id: 'show-affected-products',
        label: 'Vezi produsele afectate',
        prompt: `Arată-mi ce produse afectate ar trebui investigate și de ce.`,
        action: 'open-products',
      },
      {
        id: 'compare-prev-period',
        label: 'Compară cu perioada anterioară',
        prompt: 'Compară performanța curentă cu perioada anterioară și evidențiază diferențele importante.',
        action: 'compare-previous-period',
      },
      {
        id: 'show-meta',
        label: 'Arată doar Meta',
        prompt: 'Concentrează analiza doar pe Meta și explică ce vezi.',
        action: 'focus-meta',
      },
      {
        id: 'show-mobile',
        label: 'Arată doar mobile',
        prompt: 'Analizează doar traficul mobile și explică unde se rupe funnel-ul.',
        action: 'focus-mobile',
      },
      {
        id: 'test-plan',
        label: 'Generează plan de test',
        prompt: `Generează un plan de test pentru ${selectedProduct}.`,
        action: 'generate-test-plan',
      },
    ];
  }, [filters, contextSnapshot]);

  const handleQuickAction = async (action) => {
    if (action.prompt) setInput(action.prompt);
    if (onApplyAction) onApplyAction(action);
  };

  const onSend = async (overrideText = '') => {
    const text = (overrideText || input).trim();
    if (!text || loading) return;

    const nextMessages = [...messages, { role: 'user', content: text }];
    setMessages(nextMessages);
    setInput('');
    setLoading(true);
    setError('');

    try {
      const response = await sendCopilotMessage({
        message: text,
        filters,
        current_tab: currentTab,
        current_view: currentView,
        mode,
        context: contextSnapshot,
        conversation: nextMessages.map((m) => ({ role: m.role, content: m.content })),
        provider,
        model,
      });

      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: response.answer || 'Nu am reușit să formulez un răspuns.',
          toolsUsed: response.tools_used || [],
          provider: response.provider || provider,
          model: response.model || model,
          quickActions: quickActionTemplates,
        },
      ]);
    } catch (err) {
      setError(err.message || 'A apărut o eroare la copilot.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card panel" style={{ marginTop: 14 }}>
      <div className="copilot-header-row">
        <div>
          <h3 className="section-title">AI Copilot / Insights Center</h3>
          <p className="section-subtitle" style={{ marginBottom: 0 }}>
            Moduri de lucru, context automat, alert cards și răspunsuri orientate pe acțiune.
          </p>
        </div>
        <div className="copilot-mode-chips">
          {COPILOT_MODES.map((item) => (
            <button
              key={item.id}
              className={`tab ${mode === item.id ? 'active' : ''}`}
              title={item.hint}
              onClick={() => setMode(item.id)}
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>

      <div className="copilot-context-grid">
        <div className="copilot-context-card">
          <div className="copilot-context-title">Context curent</div>
          <div className="copilot-context-list">
            <div><strong>Zonă:</strong> {currentTab || 'N/A'}</div>
            <div><strong>View:</strong> {currentView || 'N/A'}</div>
            <div><strong>GA4:</strong> {filters.ga4Start} → {filters.ga4End}</div>
            <div><strong>Ads:</strong> {filters.adsDateRange}</div>
            <div><strong>Meta:</strong> {filters.metaDateRange}</div>
            {filters.campaignFilter ? <div><strong>Campanie:</strong> {filters.campaignFilter}</div> : null}
            {filters.productFilter ? <div><strong>Produs:</strong> {filters.productFilter}</div> : null}
            {filters.selectedItemId ? <div><strong>Item ID:</strong> {filters.selectedItemId}</div> : null}
          </div>
        </div>

        <div className="copilot-context-card">
          <div className="copilot-context-title">Dataset summary</div>
          <div className="copilot-context-list">
            {(contextSnapshot?.datasetSummary || []).length ? (
              contextSnapshot.datasetSummary.map((item) => (
                <div key={item.label}><strong>{item.label}:</strong> {item.value}</div>
              ))
            ) : (
              <div>Nu există încă un summary live pentru view-ul curent.</div>
            )}
          </div>
        </div>
      </div>

      {proactiveAlerts.length ? (
        <div style={{ marginBottom: 14 }}>
          <div className="copilot-block-title">Alerts generate automat</div>
          <div className="copilot-alerts-grid">
            {proactiveAlerts.map((alert, index) => (
              <button
                key={`${alert.title}-${index}`}
                className="copilot-alert-card"
                onClick={() => setInput(`Explain this anomaly: ${alert.title}. ${alert.detail}`)}
              >
                <div className="copilot-alert-title">{alert.title}</div>
                <div className="copilot-alert-detail">{alert.detail}</div>
                <div className="copilot-alert-cta">Explain this anomaly</div>
              </button>
            ))}
          </div>
        </div>
      ) : null}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginBottom: 12 }}>
        <div>
          <div className="label">Provider</div>
          <select className="select" value={provider} onChange={(e) => setProvider(e.target.value)}>
            {providers.map((item) => (
              <option key={item.id} value={item.id}>
                {item.label}{item.configured ? '' : ' (missing key)'}
              </option>
            ))}
          </select>
        </div>
        <div>
          <div className="label">Model</div>
          <select className="select" value={model} onChange={(e) => setModel(e.target.value)}>
            {(selectedProvider?.models || []).map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </select>
        </div>
      </div>

      {selectedProvider && !selectedProvider.configured ? (
        <div style={{ color: '#fca5a5', marginBottom: 12 }}>
          Lipsește cheia pentru {selectedProvider.label}. Setează {selectedProvider.env_key_name} înainte să folosești acest provider.
        </div>
      ) : null}

      <div className="copilot-block-title">Întrebări sugerate pentru modul {mode}</div>
      <SuggestedPromptButtons prompts={modePrompts} onSelect={setInput} />

      <div style={{ display: 'grid', gap: 10, maxHeight: 420, overflowY: 'auto', marginBottom: 12 }}>
        {messages.map((message, index) =>
          message.role === 'user' ? (
            <div
              key={index}
              style={{
                padding: '12px 14px',
                borderRadius: 14,
                border: '1px solid rgba(148,163,184,0.16)',
                background: 'rgba(96,165,250,0.12)',
              }}
            >
              <div style={{ fontSize: 12, color: '#93a4bd', marginBottom: 6, fontWeight: 700 }}>Tu</div>
              <div style={{ whiteSpace: 'pre-wrap', lineHeight: 1.5 }}>{message.content}</div>
            </div>
          ) : (
            <AssistantMessage key={index} message={message} onAction={handleQuickAction} />
          )
        )}
      </div>

      {error ? <div style={{ color: '#fca5a5', marginBottom: 10 }}>{error}</div> : null}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: 10 }}>
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
              e.preventDefault();
              onSend();
            }
          }}
          placeholder="Întreabă despre datele din aplicație..."
          rows={4}
          style={{
            width: '100%',
            resize: 'vertical',
            background: 'rgba(255,255,255,0.03)',
            border: '1px solid rgba(148,163,184,0.26)',
            borderRadius: 12,
            color: '#e5ecf6',
            padding: '12px 14px',
          }}
        />
        <button className="button" onClick={() => onSend()} disabled={loading || !selectedProvider?.configured} style={{ alignSelf: 'end', marginBottom: 0 }}>
          {loading ? 'Thinking…' : 'Send'}
        </button>
      </div>
      <div style={{ marginTop: 8, fontSize: 12, color: '#93a4bd' }}>Tip: Ctrl/Cmd + Enter pentru trimitere rapidă.</div>
    </div>
  );
}
