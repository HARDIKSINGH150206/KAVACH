import { useState, useEffect, useRef } from 'react';

const API_BASE_URL = '/api';
const WS_BASE_URL = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/api/ws/threat`;

export function useKavachBackend() {
  const [config, setConfig] = useState(null);
  const [health, setHealth] = useState(null);
  const [threatEvents, setThreatEvents] = useState({
    audio: [],
    sms: [],
    transcript: [],
    fusion: []
  });
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef(null);

  useEffect(() => {
    // Fetch initial health and config
    const fetchInitialData = async () => {
      try {
        const [healthRes, configRes] = await Promise.all([
          fetch(`${API_BASE_URL}/health`),
          fetch(`${API_BASE_URL}/config`)
        ]);
        const healthData = await healthRes.json();
        const configData = await configRes.json();
        setHealth(healthData);
        setConfig(configData);
      } catch (error) {
        console.error('Failed to fetch initial data from backend:', error);
      }
    };

    fetchInitialData();

    // Setup WebSocket
    const connectWs = () => {
      const ws = new WebSocket(WS_BASE_URL);
      
      ws.onopen = () => {
        setIsConnected(true);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          // Assuming data has a 'type' field corresponding to event types: 'audio', 'sms', 'transcript', 'fusion'
          // If the backend format differs slightly, we can adjust here.
          setThreatEvents(prev => {
            const type = data.type || 'fusion'; // fallback
            // keep last 50 events to prevent memory leaks
            const updatedList = [data, ...(prev[type] || [])].slice(0, 50);
            return {
              ...prev,
              [type]: updatedList
            };
          });
        } catch (e) {
          console.error("Failed to parse websocket message", e);
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        // Attempt to reconnect after a delay
        setTimeout(connectWs, 3000);
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        ws.close();
      };

      wsRef.current = ws;
    };

    connectWs();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  return { config, health, threatEvents, isConnected };
}
