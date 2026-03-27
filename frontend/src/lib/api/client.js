export const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

function sanitizeParams(params = {}) {
  return Object.fromEntries(
    Object.entries(params).filter(([, value]) => value !== undefined && value !== null)
  );
}

function qs(params) {
  return new URLSearchParams(sanitizeParams(params)).toString();
}

export async function getJson(path, params) {
  const url = params ? `${API_BASE}${path}?${qs(params)}` : `${API_BASE}${path}`;
  const response = await fetch(url);
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed with status ${response.status}`);
  }
  return response.json();
}

export async function postJson(path, body) {
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
