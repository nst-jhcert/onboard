"use client";

import { useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface BuildResult {
  raw_hex: string;
  raw_bytes: number[];
  length: number;
}

const FIELDS = [
  { name: "type", label: "Type (0=TM, 1=TC)", min: 0, max: 1 },
  { name: "sec_hdr_flag", label: "Sec Hdr Flag", min: 0, max: 1 },
  { name: "apid", label: "APID", min: 0, max: 2047 },
  { name: "seq_flags", label: "Seq Flags", min: 0, max: 3 },
  { name: "seq_count", label: "Seq Count", min: 0, max: 16383 },
  { name: "data_length", label: "Data Length", min: 0, max: 65535 },
] as const;

type FieldName = (typeof FIELDS)[number]["name"];

export default function CcsdsSerialize() {
  const [fields, setFields] = useState<Record<FieldName, number>>({
    version: 0,
    type: 0,
    sec_hdr_flag: 0,
    apid: 0,
    seq_flags: 3,
    seq_count: 0,
    data_length: 0,
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
      const res = await fetch(`${API_URL}/ccsds/packet/build`, {
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
      <h2>CCSDS Build</h2>
      <p>CCSDS Primary Header 필드와 페이로드를 입력하면 전체 패킷을 생성합니다.</p>

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
