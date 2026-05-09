import { useEffect, useState } from "react";
import { WS_THREAT_URL } from "./config.js";
import { ConfidenceTimeline } from "./components/ConfidenceTimeline.jsx";
import { DemoControls } from "./components/DemoControls.jsx";
import { GPULatencyCard } from "./components/GPULatencyCard.jsx";
import { ModelStatusPanel } from "./components/ModelStatusPanel.jsx";
import { SMSFeed } from "./components/SMSFeed.jsx";
import { Spectrogram } from "./components/Spectrogram.jsx";
import { TranscriptPanel } from "./components/TranscriptPanel.jsx";
import { ThreatBanner } from "./components/ThreatBanner.jsx";
import { useBackendStatus } from "./hooks/useBackendStatus.js";
import { useWebSocket } from "./hooks/useWebSocket.js";

export default function App() {
  const { data, connected, error: socketError, lastMessageAt, retryCount } = useWebSocket(WS_THREAT_URL);
  const { health, config, error: statusError } = useBackendStatus();
  const [fusion, setFusion] = useState(null);
  const [audio, setAudio] = useState(null);
  const [smsItems, setSmsItems] = useState([]);
  const [transcript, setTranscript] = useState(null);
  const [timeline, setTimeline] = useState([]);
  const [operatorStatus, setOperatorStatus] = useState("Demo controls ready");

  useEffect(() => {
    if (!data) return;
    if (data.type === "audio") setAudio(data);
    if (data.type === "sms") setSmsItems((items) => [data, ...items].slice(0, 10));
    if (data.type === "transcript") setTranscript(data);
    if (data.type === "fusion") {
      setFusion(data);
      setTimeline((items) => [...items, { time: data.timestamp, score: data.threat_score }].slice(-60));
    }
  }, [data]);

  function resetDashboard() {
    setSmsItems([]);
    setTranscript(null);
    setTimeline([]);
    setOperatorStatus("Dashboard reset");
  }

  const threatLevel = fusion?.threat_level ?? "SAFE";
  const threatColor = fusion?.color ?? "#1F9D55";
  const threatScore = fusion?.threat_score?.toFixed(2) ?? "0.00";

  return (
    <main className="appShell">
      <header className="topBar">
        <div>
          <h1>KAVACH</h1>
          <p>India’s first real-time, offline dual-vector AI shield</p>
        </div>
        <div className="topStatus">
          <span>{socketError || statusError || operatorStatus}</span>
          <div className={connected ? "status live" : "status"}>{connected ? "LIVE" : "OFFLINE"}</div>
        </div>
      </header>

      <div className="heroRow">
        <div className="heroText">
          <div className="heroBadge">MHA/CERT-In Integration: ACTIVE</div>
          <div className="heroBadge secondary">Runtime demo protected</div>
        </div>
        <div className="heroSummary">
          <span>Threat score</span>
          <strong style={{ color: threatColor }}>{threatScore}</strong>
        </div>
      </div>

      <div className="statusCards">
        <article className="statusCard" style={{ borderColor: threatColor }}>
          <span>Threat level</span>
          <strong style={{ color: threatColor }}>{threatLevel}</strong>
          <p>Bayesian fusion command center</p>
        </article>
        <article className="statusCard">
          <span>Connection</span>
          <strong className={connected ? "ok" : "danger"}>{connected ? "ONLINE" : "OFFLINE"}</strong>
          <p>{lastMessageAt ? `Last event ${new Date(lastMessageAt).toLocaleTimeString()}` : "Awaiting stream events"}</p>
        </article>
        <article className="statusCard">
          <span>Mode</span>
          <strong>{health?.mode?.toUpperCase() ?? "DEMO"}</strong>
          <p>Runtime processing source</p>
        </article>
        <article className="statusCard">
          <span>Explainable score</span>
          <strong>Auditable & repeatable</strong>
          <p>{retryCount > 0 ? `Reconnected ${retryCount} times` : "Summary of scoring decisions"}</p>
        </article>
      </div>

      <div className="dashboardGrid">
        <div className="mainColumn">
          <Spectrogram melData={audio?.mel_data} audioScore={audio?.audio_score ?? 0} />
          <div className="bottomPanels">
            <ConfidenceTimeline points={timeline} />
            <TranscriptPanel item={transcript} />
          </div>
        </div>

        <aside className="sideColumn">
          <ThreatBanner fusion={fusion} />
          <div className="sideStack">
            <SMSFeed items={smsItems} />
            <ModelStatusPanel health={health} config={config} error={statusError} />
            <DemoControls onReset={resetDashboard} onStatus={setOperatorStatus} />
          </div>
        </aside>
      </div>
    </main>
  );
}
