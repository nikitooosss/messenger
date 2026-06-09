import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { useQueryClient } from "@tanstack/react-query";
import { handleWsEvent } from "./handleWsEvent";
import { qk } from "../lib/queryKeys";
import type { ClientEvent, ServerEvent } from "../types/wsEvents";

export type WsStatus = "connecting" | "open" | "closed" | "reconnecting";

interface WsCtx {
  status: WsStatus;
  send: (event: ClientEvent) => void;
}

const WSContext = createContext<WsCtx | null>(null);

interface WebSocketProviderProps {
  children: ReactNode;
  enabled: boolean;
}

export function WebSocketProvider({
  children,
  enabled,
}: WebSocketProviderProps) {
  const qc = useQueryClient();
  const wsRef = useRef<WebSocket | null>(null);
  const retryRef = useRef(0);
  const timerRef = useRef<number | null>(null);
  const queueRef = useRef<ClientEvent[]>([]);
  const [status, setStatus] = useState<WsStatus>("closed");

  const connect = useCallback(() => {
    if (!enabled) return;
    setStatus(retryRef.current === 0 ? "connecting" : "reconnecting");

    const proto = window.location.protocol === "https:" ? "wss" : "ws";
    const url = `${proto}://${window.location.host}/api/ws`;
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      retryRef.current = 0;
      setStatus("open");
      const pending = queueRef.current.splice(0);
      pending.forEach((ev) => ws.send(JSON.stringify(ev)));
      qc.invalidateQueries({ queryKey: qk.messagesRoot });
      qc.invalidateQueries({ queryKey: qk.chats() });
    };

    ws.onmessage = (e) => {
      try {
        const ev = JSON.parse(e.data) as ServerEvent;
        handleWsEvent(ev, qc);
      } catch (err) {
        console.error("WS message parse error", err);
      }
    };

    ws.onclose = () => {
      setStatus("closed");
      wsRef.current = null;
      const delay =
        Math.min(30_000, 500 * 2 ** retryRef.current) + Math.random() * 250;
      retryRef.current += 1;
      timerRef.current = window.setTimeout(connect, delay);
    };

    ws.onerror = () => {
      ws.close();
    };
  }, [enabled, qc]);

  useEffect(() => {
    if (!enabled) return;
    connect();
    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
        timerRef.current = null;
      }
      if (wsRef.current) {
        wsRef.current.onclose = null;
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [enabled, connect]);

  const send = useCallback((event: ClientEvent) => {
    const ws = wsRef.current;
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(event));
    } else {
      queueRef.current.push(event);
    }
  }, []);

  return (
    <WSContext.Provider value={{ status, send }}>{children}</WSContext.Provider>
  );
}

export function useWebSocket(): WsCtx {
  const ctx = useContext(WSContext);
  if (!ctx)
    throw new Error("useWebSocket must be used within WebSocketProvider");
  return ctx;
}
