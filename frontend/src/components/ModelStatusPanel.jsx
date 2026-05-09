export function ModelStatusPanel({ health, config, error }) {
  const audio = health?.models?.audio;
  const sms = health?.models?.sms;
  const fusion = health?.models?.fusion;
  const checkpointState = audio?.checkpoint_state ?? "unknown";
  const checkpointClass = checkpointState === "validated" ? "ok" : checkpointState === "missing" ? "warn" : "danger";
  const statusLabel = error ? "OFFLINE" : health ? "READY" : "CHECKING";
  const statusClass = error ? "danger" : health ? "ok" : "warn";

  return (
    <section className="panel modelStatusPanel">
      <div className="panelTitle">
        <span>Model Status</span>
        <strong className={statusClass}>{statusLabel}</strong>
      </div>
      <div className="statusGrid">
        <div className="statusItem">
          <span>Audio</span>
          <strong>{audio?.backend ?? "--"}</strong>
        </div>
        <div className="statusItem">
          <span>AASIST checkpoint</span>
          <strong className={checkpointClass}>{checkpointState}</strong>
        </div>
        <div className="statusItem">
          <span>SMS</span>
          <strong>{sms?.backend ?? "--"}</strong>
        </div>
        <div className="statusItem">
          <span>Source</span>
          <strong>{config?.audio_source?.toUpperCase() ?? "--"}</strong>
        </div>
      </div>
      <div className="formula compact">
        weights {fusion?.audio_weight ?? config?.audio_weight ?? "--"} / {fusion?.sms_weight ?? config?.sms_weight ?? "--"} /{" "}
        {fusion?.transcript_weight ?? config?.transcript_weight ?? "--"}
        {" | "}thresholds {config?.thresholds?.suspicious ?? "--"} / {config?.thresholds?.high ?? "--"} /{" "}
        {config?.thresholds?.critical ?? "--"}
      </div>
      {error && <div className="statusError">{error}</div>}
    </section>
  );
}
