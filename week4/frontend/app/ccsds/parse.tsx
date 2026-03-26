"use client";

import { useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface CcsdsPrimaryHeader {
  version: number;
  type: number;
  sec_hdr_flag: number;
  apid: number;
  seq_flags: number;
  seq_count: number;
  data_length: number;
}

interface ParseResult {
  header: CcsdsPrimaryHeader;
  payload: string;
  raw_hex: string;
}

export default function CcdsParse() {
  const [rawInput, setRawInput] = useState("");
  const [result, setResult] = useState<ParseResult | null>(null);
  const [error, setError] = useState("");

  const handleParse = async () => {
    setError("");
    setResult(null);

    try {
      const res = await fetch(`${API_URL}/ccsds/packet/parse`, {
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
      <h2>CCSDS Parse</h2>
      <p>CCSDS 패킷 hex를 입력하면 Primary Header와 페이로드로 분해합니다.</p>

      <div style={{ display: "flex", gap: "8px", marginBottom: "16px" }}>
        <input
          type="text"
          value={rawInput}
          onChange={(e) => setRawInput(e.target.value)}
          placeholder="예: 08C6C00A001048656C6C6F"
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
            <tr><td style={tdStyle}>Version</td><td style={tdStyle}>{result.header.version}</td></tr>
            <tr><td style={tdStyle}>Type</td><td style={tdStyle}>{result.header.type} ({result.header.type === 0 ? "TM" : "TC"})</td></tr>
            <tr><td style={tdStyle}>Sec Hdr Flag</td><td style={tdStyle}>{result.header.sec_hdr_flag}</td></tr>
            <tr><td style={tdStyle}>APID</td><td style={tdStyle}>{result.header.apid}</td></tr>
            <tr><td style={tdStyle}>Seq Flags</td><td style={tdStyle}>{result.header.seq_flags}</td></tr>
            <tr><td style={tdStyle}>Seq Count</td><td style={tdStyle}>{result.header.seq_count}</td></tr>
            <tr><td style={tdStyle}>Data Length</td><td style={tdStyle}>{result.header.data_length}</td></tr>
            <tr><td style={tdStyle}>Payload</td><td style={tdStyle}>{result.payload || "(empty)"}</td></tr>
            <tr><td style={tdStyle}>Full Packet</td><td style={tdStyle}>{result.raw_hex}</td></tr>
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
