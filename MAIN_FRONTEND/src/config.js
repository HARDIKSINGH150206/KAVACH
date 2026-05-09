const DEFAULT_API_BASE = '/api';
const DEFAULT_WS_BASE =
  window.location.protocol === 'https:'
    ? 'wss://'
    : 'ws://';

export const API_BASE = (import.meta.env.VITE_API_BASE || DEFAULT_API_BASE).replace(/\/+$/, '');
export const API_V1_BASE = `${API_BASE}/v1`;
export const WS_THREAT_URL = (
  import.meta.env.VITE_WS_THREAT_URL || `${DEFAULT_WS_BASE}${window.location.host}/ws/threat`
).replace(/\/+$/, '');
