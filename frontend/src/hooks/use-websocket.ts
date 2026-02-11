import { useEffect, useRef } from 'react';
import { WebSocketClient } from '@/lib/ws';

export function useWebSocket(path: string, handlers: Record<string, (data: any) => void>) {
  const wsRef = useRef<WebSocketClient | null>(null);

  useEffect(() => {
    const ws = new WebSocketClient(path);
    wsRef.current = ws;

    Object.entries(handlers).forEach(([type, handler]) => {
      ws.on(type, handler);
    });

    ws.connect();

    return () => {
      ws.disconnect();
    };
  }, [path]);

  return {
    send: (data: any) => wsRef.current?.send(data),
  };
}
