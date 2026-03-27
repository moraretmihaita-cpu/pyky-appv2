const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

function qs(params) {
  return new URLSearchParams(params).toString();
}

async function getJson(path, params) {
  const url = params ? `${API_BASE}${path}?${qs(params)}` : `${API_BASE}${path}`;
  const response = await fetch(url);
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed with status ${response.status}`);
  }
  return response.json();
}

async function postJson(path, body) {
  const response = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed with status ${response.status}`);
  }
  return response.json();
}

export * from './api.v9';

export async function fetchAiProviders() {
  return getJson('/api/ai/providers');
}

export async function sendCopilotMessageV2(payload) {
  return postJson('/api/copilot/chat', payload);
}
