import { useEffect, useRef, useState } from "react";

export function useWebSocket(url) {
  const [data, setData] = useState(null);
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState(null);
  const [lastMessageAt, setLastMessageAt] = useState(null);
  const [retryCount, setRetryCount] = useState(0);
  const socket = useRef(null);

  useEffect(() => {
    let retryTimer;

    function connect() {
      socket.current = new WebSocket(url);
      socket.current.onopen = () => {
        setConnected(true);
        setError(null);
        setRetryCount(0);
      };
      socket.current.onclose = () => {
        setConnected(false);
        setRetryCount((count) => count + 1);
        retryTimer = window.setTimeout(connect, 1500);
      };
      socket.current.onerror = () => {
        setError("WebSocket connection failed");
      };
      socket.current.onmessage = (event) => {
        try {
          setData(JSON.parse(event.data));
          setLastMessageAt(Date.now());
        } catch {
          setError("Invalid WebSocket payload");
        }
      };
    }

    connect();
    return () => {
      window.clearTimeout(retryTimer);
      socket.current?.close();
    };
  }, [url]);

  return { data, connected, error, lastMessageAt, retryCount };
}
