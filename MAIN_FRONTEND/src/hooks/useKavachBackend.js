import { useEffect, useRef, useState } from 'react';
import { API_V1_BASE, WS_THREAT_URL } from '../config';

export function useKavachBackend() {
  const [config, setConfig] = useState(null);
  const [health, setHealth] = useState(null);
  const [backendReady, setBackendReady] = useState(false);
  const [threatEvents, setThreatEvents] = useState({
    audio: [],
    sms: [],
    transcript: [],
    fusion: []
  });
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef(null);
  const reconnectTimerRef = useRef(null);
  const healthTimerRef = useRef(null);
  const intentionallyClosedRef = useRef(false);

  useEffect(() => {
    let cancelled = false;

    const pollBackend = async () => {
      try {
        const [healthRes, configRes] = await Promise.all([
          fetch(`${API_V1_BASE}/health`),
          fetch(`${API_V1_BASE}/config`)
        ]);

        if (!healthRes.ok || !configRes.ok) {
          throw new Error('Backend status request failed');
        }

        const healthData = await healthRes.json();
        const configData = await configRes.json();

        if (cancelled) return;
        setHealth(healthData);
        setConfig(configData);
        setBackendReady(true);
      } catch (error) {
        if (!cancelled) {
          setBackendReady(false);
          console.error('Failed to fetch initial data from backend:', error);
        }
      } finally {
        if (!cancelled) {
          healthTimerRef.current = window.setTimeout(pollBackend, 5000);
        }
      }
    };

    pollBackend();

    return () => {
      cancelled = true;
      if (healthTimerRef.current) {
        window.clearTimeout(healthTimerRef.current);
      }
    };
  }, []);

  useEffect(() => {
    if (!backendReady) return undefined;

    let cancelled = false;
    let hasOpened = false;

    const connectWs = () => {
      if (cancelled) return;

      intentionallyClosedRef.current = false;
      hasOpened = false;

      const ws = new WebSocket(WS_THREAT_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        if (cancelled) return;
        hasOpened = true;
        setIsConnected(true);
      };

      ws.onmessage = (event) => {
        if (cancelled) return;
        try {
          const data = JSON.parse(event.data);
          setThreatEvents((prev) => {
            const type = data.type || 'fusion';
            const updatedList = [data, ...(prev[type] || [])].slice(0, 50);
            return {
              ...prev,
              [type]: updatedList
            };
          });
        } catch (error) {
          console.error('Failed to parse websocket message', error);
        }
      };

      ws.onclose = () => {
        if (cancelled || intentionallyClosedRef.current) return;
        setIsConnected(false);
        if (!hasOpened) {
          reconnectTimerRef.current = window.setTimeout(connectWs, 3000);
          return;
        }
        reconnectTimerRef.current = window.setTimeout(connectWs, 3000);
      };

      ws.onerror = () => {
        if (cancelled) return;
        setIsConnected(false);
      };
    };

    connectWs();

    return () => {
      cancelled = true;
      intentionallyClosedRef.current = true;

      if (reconnectTimerRef.current) {
        window.clearTimeout(reconnectTimerRef.current);
      }

      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.close(1000, 'component unmounted');
      }

      wsRef.current = null;
    };
  }, [backendReady]);

  return { config, health, threatEvents, isConnected, backendReady };
}
