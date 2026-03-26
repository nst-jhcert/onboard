"use client";

import { useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface CspHeader {
  priority: number;
  source: number;
  destination: number;
  dport: number;
  sport: number;
  flags: number;
}

interface ParseResult {
  header: CspHeader;
  raw_hex: string;
  raw_int: number;
}

export default function CspParse() {
  const [rawInput, setRawInput] = useState("");
  const [result, setResult] = useState<ParseResult | null>(null);
  const [error, setError] = useState("");

  const handleParse = async () => {
    setError("");
    setResult(null);

    try {
      const res = await fetch(`${API_URL}/csp/parse`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ raw: rawInput }),
      });

      if (!res.ok) {
        const data = await res.json();
        setError(data.detail || "Parse failed");
        return;
      }

      setResult(await res.json());
    } catch {
      setError("API connection failed");
    }
  };

  return (
    <section>
      <h2>CSP Parse</h2>
      <p>32-bit hex 값을 입력하면 CSP 헤더 필드로 분해합니다.</p>

      <div style={{ display: "flex", gap: "8px", marginBottom: "16px" }}>
        <input
          type="text"
          value={rawInput}
          onChange={(e) => setRawInput(e.target.value)}
          placeholder="예: A5143403"
          style={{ padding: "8px", fontFamily: "monospace", flex: 1 }}
        />
        <button onClick={handleParse} style={{ padding: "8px 16px" }}>
          Parse
        </button>
      </div>

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
            <tr><td style={tdStyle}>Priority</td><td style={tdStyle}>{result.header.priority}</td></tr>
            <tr><td style={tdStyle}>Source</td><td style={tdStyle}>{result.header.source}</td></tr>
            <tr><td style={tdStyle}>Destination</td><td style={tdStyle}>{result.header.destination}</td></tr>
            <tr><td style={tdStyle}>Dest Port</td><td style={tdStyle}>{result.header.dport}</td></tr>
            <tr><td style={tdStyle}>Src Port</td><td style={tdStyle}>{result.header.sport}</td></tr>
            <tr><td style={tdStyle}>Flags</td><td style={tdStyle}>0x{result.header.flags.toString(16).toUpperCase().padStart(2, "0")}</td></tr>
            <tr><td style={tdStyle}>Raw Hex</td><td style={tdStyle}>{result.raw_hex}</td></tr>
            <tr><td style={tdStyle}>Raw Int</td><td style={tdStyle}>{result.raw_int}</td></tr>
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
