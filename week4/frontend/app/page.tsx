import CspParse from "./csp/parse";
import CspSerialize from "./csp/serialize";
import CcdsParse from "./ccsds/parse";
import CcsdsSerialize from "./ccsds/serialize";
import WsMonitor from "./monitor/ws-monitor";

export default function Home() {
  return (
    <main style={{ maxWidth: "960px", margin: "0 auto", padding: "24px" }}>
      <h1>ONBOARD-WEEK4</h1>
      <p>CSP/CCSDS Packet Handler &amp; MQ Monitor</p>

      <hr style={{ margin: "24px 0" }} />
      <h2 style={{ marginBottom: "16px" }}>CSP</h2>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "32px" }}>
        <CspParse />
        <CspSerialize />
      </div>

      <hr style={{ margin: "24px 0" }} />
      <h2 style={{ marginBottom: "16px" }}>CCSDS</h2>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "32px" }}>
        <CcdsParse />
        <CcsdsSerialize />
      </div>

      <hr style={{ margin: "24px 0" }} />
      <h2 style={{ marginBottom: "16px" }}>MQ Monitor</h2>
      <WsMonitor />
    </main>
  );
}
