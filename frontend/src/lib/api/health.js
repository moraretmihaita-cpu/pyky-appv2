import { getJson } from './client';

export async function fetchHealth() {
  return getJson('/health');
}
