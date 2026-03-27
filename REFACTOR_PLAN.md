# React + FastAPI Consolidation Plan

## Goal
Transform the project into a single maintained product line:
- React frontend only
- FastAPI backend only
- Streamlit removed
- legacy/archived code removed from active tree
- AI Copilot promoted from side chat to contextual assistant

## Phase 1 — Safe cleanup
Delete from active repo:
- app/ui.py
- app/theme.py
- app/ui_sections/
- app/archived/
- app/__pycache__/
- frontend/src/archived/
- frontend/src/components/Archived/
- frontend/node_modules/
- Marketing-Ai-Ads-feature-frontend-react-migration/
- root token.json / oauth_client.json / Claude API KEY.txt / Text lipit.txt

Review before delete:
- app/main.py (debug script, should be removed or replaced with backend entry instructions)
- frontend/src/App.jsx
- frontend/src/main.live.jsx
- frontend/src/main.live.refactor.v1.jsx
- frontend/src/main.live.v2.jsx
- frontend/src/api.refactor.v1.js

Keep for now:
- app/api_server_refactor_v1.py
- app/tools/
- app/ai/
- app/services/
- frontend/src/AppLiveRefactorV2.jsx (temporary until split)
- frontend/src/api.client.js
- frontend/src/components/CopilotPanelV3.jsx
- frontend/src/components/DataTable.jsx
- frontend/src/main.jsx

## Phase 2 — Target backend structure

app/
  api/
    main.py
    routes/
      overview.py
      google_ads.py
      meta.py
      ga4.py
      diagnostics.py
      copilot.py
    schemas/
      filters.py
      responses.py
  services/
    overview_service.py
    google_ads_service.py
    meta_service.py
    ga4_service.py
    diagnostics_service.py
    copilot_service.py
  domain/
    filters.py
    metrics.py
    insights.py
  integrations/
    ads.py
    ga4.py
    meta_ads.py
  ai/
    config.py
    providers.py
    service.py
    tools_registry.py

## Phase 3 — Target frontend structure

frontend/src/
  app/
    App.jsx
    routes.jsx
    providers.jsx
  pages/
    OverviewPage.jsx
    PaidMediaPage.jsx
    FunnelPage.jsx
    CopilotPage.jsx
  features/
    filters/
    overview/
    paid-media/
    funnel/
    copilot/
  components/
    layout/
    cards/
    tables/
    charts/
    feedback/
  lib/
    api/
      client.js
      overview.js
      paidMedia.js
      funnel.js
      copilot.js
    format/
    filters/
  styles/
    tokens.css
    globals.css

## Product navigation
1. Overview
2. Paid Media
3. Funnel & Diagnostics
4. AI Copilot

## AI Copilot direction
- contextual prompts based on current page
- quick actions from insights
- structured answers: summary, evidence, cause, action, impact, confidence
- proactive alerts from backend-generated anomalies

## Immediate first implementation steps
1. Remove dead frontend entrypoints and archived folders.
2. Keep a single frontend entrypoint: `frontend/src/main.jsx`.
3. Rename `AppLiveRefactorV2.jsx` to `App.jsx` after split.
4. Extract shared filter state into dedicated module.
5. Split backend endpoints by domain, without changing response contracts initially.
