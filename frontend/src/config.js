const DEFAULT_API_BASE = "";
const WS_PROTOCOL = window.location.protocol === "https:" ? "wss:" : "ws:";
const DEFAULT_WS_BASE = `${WS_PROTOCOL}//${window.location.host}`;

export const API_BASE = (import.meta.env.VITE_API_BASE || DEFAULT_API_BASE).replace(/\/+$/, "");
export const API_V1_BASE = `${API_BASE}/api/v1`;
export const WS_THREAT_URL = (import.meta.env.VITE_WS_THREAT_URL || `${DEFAULT_WS_BASE}/ws/threat`).replace(
  /\/+$/,
  "",
);
