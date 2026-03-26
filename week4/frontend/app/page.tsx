import CspParse from "./csp/parse";
import CspSerialize from "./csp/serialize";

export default function Home() {
  return (
    <main style={{ maxWidth: "960px", margin: "0 auto", padding: "24px" }}>
      <h1>ONBOARD-WEEK4</h1>
      <p>CSP/CCSDS Packet Handler</p>
      <hr style={{ margin: "24px 0" }} />
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "32px" }}>
        <CspParse />
        <CspSerialize />
      </div>
    </main>
  );
}
