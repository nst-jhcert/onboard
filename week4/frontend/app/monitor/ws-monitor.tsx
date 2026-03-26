"use client";

import { useEffect, useRef, useState } from "react";

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8080/ws";
const MAX_MESSAGES = 100;

interface MqMessage {
  protocol: string;
  topic?: string;
  message: string;
  timestamp: string;
}

export default function WsMonitor() {
  const [messages, setMessages] = useState<MqMessage[]>([]);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);
    ws.onerror = () => setConnected(false);

    ws.onmessage = (event) => {
      const data: MqMessage = JSON.parse(event.data);
      setMessages((prev) => [...prev.slice(-(MAX_MESSAGES - 1)), data]);
    };

    return () => {
      ws.close();
    };
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleClear = () => setMessages([]);

  return (
    <section>
      <h3>
        MQ Monitor{" "}
        <span style={{ color: connected ? "green" : "red", fontSize: "14px" }}>
          {connected ? "● Connected" : "● Disconnected"}
        </span>
      </h3>

      <button onClick={handleClear} style={{ padding: "4px 12px", marginBottom: "8px" }}>
        Clear
      </button>

      <div
        style={{
          height: "400px",
          overflow: "auto",
          border: "1px solid #ccc",
          fontFamily: "monospace",
          fontSize: "13px",
        }}
      >
        <table style={{ borderCollapse: "collapse", width: "100%" }}>
          <thead>
            <tr>
              <th style={thStyle}>Time</th>
              <th style={thStyle}>Protocol</th>
              <th style={thStyle}>Message</th>
            </tr>
          </thead>
          <tbody>
            {messages.map((msg, i) => (
              <tr key={i}>
                <td style={tdStyle}>{new Date(msg.timestamp).toLocaleTimeString()}</td>
                <td style={{ ...tdStyle, color: msg.protocol === "ZeroMQ" ? "#e67e22" : "#2ecc71" }}>
                  {msg.protocol}
                </td>
                <td style={tdStyle}>{msg.message}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <div ref={bottomRef} />
      </div>
    </section>
  );
}

const thStyle: React.CSSProperties = {
  border: "1px solid #ccc",
  padding: "6px 8px",
  textAlign: "left",
  backgroundColor: "#f5f5f5",
  position: "sticky",
  top: 0,
};

const tdStyle: React.CSSProperties = {
  border: "1px solid #ccc",
  padding: "4px 8px",
};
