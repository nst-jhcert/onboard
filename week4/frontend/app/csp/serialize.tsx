"use client";

import { useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface BuildResult {
  raw_hex: string;
  raw_bytes: number[];
  length: number;
}

const FIELDS = [
  { name: "priority", label: "Priority", min: 0, max: 3 },
  { name: "source", label: "Source", min: 0, max: 31 },
  { name: "destination", label: "Destination", min: 0, max: 31 },
  { name: "dport", label: "Dest Port", min: 0, max: 63 },
  { name: "sport", label: "Src Port", min: 0, max: 63 },
  { name: "flags", label: "Flags", min: 0, max: 255 },
] as const;

type FieldName = (typeof FIELDS)[number]["name"];

export default function CspSerialize() {
  const [fields, setFields] = useState<Record<FieldName, number>>({
    priority: 0,
    source: 0,
    destination: 0,
    dport: 0,
    sport: 0,
    flags: 0,
  });
  const [payload, setPayload] = useState("");
  const [result, setResult] = useState<BuildResult | null>(null);
  const [error, setError] = useState("");

  const handleChange = (name: FieldName, value: string) => {
    setFields((prev) => ({ ...prev, [name]: Number(value) || 0 }));
  };

  const handleBuild = async () => {
    setError("");
    setResult(null);

    try {
      const res = await fetch(`${API_URL}/csp/packet/build`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ header: fields, payload }),
      });

      if (!res.ok) {
        const data = await res.json();
        setError(data.detail || "Build failed");
        return;
      }

      setResult(await res.json());
    } catch {
      setError("API connection failed");
    }
  };

  return (
    <section>
      <h2>CSP Build</h2>
      <p>CSP 헤더 필드와 페이로드를 입력하면 전체 패킷을 생성합니다.</p>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px", marginBottom: "8px" }}>
        {FIELDS.map((f) => (
          <label key={f.name} style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
            <span>{f.label} ({f.min}-{f.max})</span>
            <input
              type="number"
              min={f.min}
              max={f.max}
              value={fields[f.name]}
              onChange={(e) => handleChange(f.name, e.target.value)}
              style={{ padding: "8px", fontFamily: "monospace" }}
            />
          </label>
        ))}
      </div>

      <label style={{ display: "flex", flexDirection: "column", gap: "4px", marginBottom: "16px" }}>
        <span>Payload (hex)</span>
        <input
          type="text"
          value={payload}
          onChange={(e) => setPayload(e.target.value)}
          placeholder="예: 48656C6C6F"
          style={{ padding: "8px", fontFamily: "monospace" }}
        />
      </label>

      <button onClick={handleBuild} style={{ padding: "8px 16px", marginBottom: "16px" }}>
        Build
      </button>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {result && (
        <table style={{ borderCollapse: "collapse", width: "100%" }}>
          <thead>
            <tr>
              <th style={thStyle}>Field</th>
              <th style={thStyle}>Value</th>
            </tr>
          </thead>
          <tbody>
            <tr><td style={tdStyle}>Full Packet</td><td style={tdStyle}>{result.raw_hex}</td></tr>
            <tr><td style={tdStyle}>Raw Bytes</td><td style={tdStyle}>[{result.raw_bytes.join(", ")}]</td></tr>
            <tr><td style={tdStyle}>Length</td><td style={tdStyle}>{result.length} bytes</td></tr>
          </tbody>
        </table>
      )}
    </section>
  );
}

const thStyle: React.CSSProperties = {
  border: "1px solid #ccc",
  padding: "8px",
  textAlign: "left",
  backgroundColor: "#f5f5f5",
};

const tdStyle: React.CSSProperties = {
  border: "1px solid #ccc",
  padding: "8px",
  fontFamily: "monospace",
};
