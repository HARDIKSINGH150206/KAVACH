export function GPULatencyCard({ latency, connected, mode }) {
  return (
    <section className="metricRow">
      <div className="metric">
        <span>Inference</span>
        <strong>{latency == null ? "--" : `${latency.toFixed(1)} ms`}</strong>
      </div>
      <div className="metric">
        <span>Backend</span>
        <strong className={connected ? "ok" : "danger"}>{connected ? "LIVE" : "OFFLINE"}</strong>
      </div>
      <div className="metric">
        <span>Mode</span>
        <strong>{mode?.toUpperCase() ?? "DEMO"}</strong>
      </div>
    </section>
  );
}
