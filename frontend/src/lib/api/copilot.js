import { getJson, postJson } from './client';

export async function fetchAiProviders() {
  return getJson('/api/ai/providers');
}

export async function sendCopilotMessage(payload) {
  return postJson('/api/copilot/chat', payload);
}
