import { useEffect, useState } from "react";
import { API_BASE, API_V1_BASE } from "../config.js";

export function useBackendStatus() {
  const [health, setHealth] = useState(null);
  const [config, setConfig] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    let timer;

    async function loadStatus() {
      try {
        const [healthResponse, configResponse] = await Promise.all([
          fetch(`${API_V1_BASE}/health`).catch(() => fetch(`${API_BASE}/health`)),
          fetch(`${API_V1_BASE}/config`).catch(() => fetch(`${API_BASE}/config`)),
        ]);
        if (!healthResponse.ok || !configResponse.ok) {
          throw new Error("Backend status request failed");
        }
        const [healthData, configData] = await Promise.all([healthResponse.json(), configResponse.json()]);
        if (!cancelled) {
          setHealth(healthData);
          setConfig(configData);
          setError(null);
        }
      } catch (requestError) {
        if (!cancelled) setError(requestError.message);
      } finally {
        if (!cancelled) timer = window.setTimeout(loadStatus, 5000);
      }
    }

    loadStatus();
    return () => {
      cancelled = true;
      window.clearTimeout(timer);
    };
  }, []);

  return { health, config, error };
}
