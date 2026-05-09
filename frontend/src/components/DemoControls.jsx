import { Play, RotateCcw, Send, ShieldCheck, ShieldX, Siren, Smartphone, TriangleAlert } from "lucide-react";
import { useRef, useState } from "react";
import { API_BASE, API_V1_BASE } from "../config.js";

const messages = {
  echallan:
    "Vehicle MH12AB1234 ka e-challan Rs.500 pending hai. Pay karein: https://bit.ly/challan99 -MoRTH",
  kyc:
    "SBI: Aapka KYC expire ho raha hai. Abhi update: https://tinyurl.com/sbikycnow ya account band!",
  fastag:
    "FASTag balance low Rs.12. Recharge now: https://cutt.ly/fastagpay avoid toll penalty",
  legit: "HDFCBK: Your A/c XX4321 credited Rs.15000 on 07-May. Avl Bal Rs.87650.",
};

async function postJson(path, payload) {
  let response = await fetch(`${API_V1_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (response.status === 404) {
    response = await fetch(`${API_BASE}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  }
  if (!response.ok) throw new Error(`Request failed: ${response.status}`);
  const data = await response.json();
  if (data.accepted === false) throw new Error(data.error || "Request rejected");
  return data;
}

export function DemoControls({ onReset, onStatus }) {
  const [customSms, setCustomSms] = useState("");
  const [runningDemo, setRunningDemo] = useState(false);
  const timers = useRef([]);

  async function injectMessage(type) {
    await postJson("/sms/mock", { text: messages[type] });
    onStatus(`Injected ${type.toUpperCase()} SMS`);
  }

  async function setScenario(scenario) {
    await postJson("/demo/scenario", { scenario });
    onStatus(scenario === "auto" ? "Automatic live stream resumed" : `${scenario.toUpperCase()} scenario armed`);
  }

  async function injectCustomSms() {
    const text = customSms.trim();
    if (!text) {
      onStatus("Enter an SMS before sending");
      return;
    }
    await postJson("/sms/mock", { text });
    setCustomSms("");
    onStatus("Custom SMS injected");
  }

  function clearTimers() {
    timers.current.forEach((timer) => window.clearTimeout(timer));
    timers.current = [];
    setRunningDemo(false);
  }

  function schedule(delay, action) {
    const timer = window.setTimeout(() => run(action), delay);
    timers.current.push(timer);
  }

  function startGuidedDemo() {
    clearTimers();
    setRunningDemo(true);
    onReset();
    onStatus("Demo step 1: SAFE baseline");
    schedule(0, () => setScenario("safe"));
    schedule(3500, async () => {
      onStatus("Demo step 2: e-Challan SMS attack");
      await injectMessage("echallan");
      await setScenario("high");
    });
    schedule(8000, async () => {
      onStatus("Demo step 3: deepfake voice confirms attack");
      await setScenario("critical");
    });
    schedule(13000, async () => {
      onStatus("Demo step 4: return to normal");
      await injectMessage("legit");
      await setScenario("safe");
    });
    schedule(16500, async () => {
      await setScenario("auto");
      setRunningDemo(false);
      onStatus("Guided demo complete");
    });
  }

  async function run(action) {
    try {
      await action();
    } catch (error) {
      onStatus(error.message);
    }
  }

  return (
    <section className="panel controlsPanel">
      <div className="panelTitle">
        <span>Demo Controls</span>
        <strong>Operator</strong>
      </div>

      <div className="controlGroup">
        <span className="controlLabel">SMS injection</span>
        <button type="button" onClick={() => run(() => injectMessage("echallan"))}>
          <Smartphone size={16} /> e-Challan
        </button>
        <button type="button" onClick={() => run(() => injectMessage("kyc"))}>
          <Smartphone size={16} /> KYC Scam
        </button>
        <button type="button" onClick={() => run(() => injectMessage("fastag"))}>
          <Smartphone size={16} /> FASTag
        </button>
        <button type="button" onClick={() => run(() => injectMessage("legit"))}>
          <ShieldCheck size={16} /> Legit SMS
        </button>
      </div>

      <div className="manualSms">
        <textarea
          value={customSms}
          onChange={(event) => setCustomSms(event.target.value)}
          placeholder="Paste any SMS here to score it live"
          rows={3}
        />
        <button type="button" onClick={() => run(injectCustomSms)}>
          <Send size={16} /> Send SMS
        </button>
      </div>

      <div className="controlGroup">
        <span className="controlLabel">Threat scenario</span>
        <button type="button" onClick={() => run(() => setScenario("safe"))}>
          <ShieldCheck size={16} /> SAFE
        </button>
        <button type="button" onClick={() => run(() => setScenario("high"))}>
          <TriangleAlert size={16} /> HIGH
        </button>
        <button type="button" onClick={() => run(() => setScenario("critical"))}>
          <Siren size={16} /> CRITICAL
        </button>
        <button type="button" onClick={() => run(() => setScenario("auto"))}>
          <ShieldX size={16} /> Auto
        </button>
      </div>

      <div className="guidedDemo">
        <button type="button" className="primaryButton" disabled={runningDemo} onClick={startGuidedDemo}>
          <Play size={16} /> {runningDemo ? "Running flow" : "Run demo flow"}
        </button>
        <button type="button" className="resetButton" onClick={clearTimers}>
          <ShieldX size={16} /> Stop flow
        </button>
        <button type="button" className="resetButton" onClick={onReset}>
          <RotateCcw size={16} /> Reset dashboard
        </button>
      </div>
    </section>
  );
}
