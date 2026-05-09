import { AlertTriangle, CheckCircle2, ShieldAlert, ShieldCheck } from "lucide-react";

const icons = {
  SAFE: ShieldCheck,
  SUSPICIOUS: AlertTriangle,
  HIGH: ShieldAlert,
  CRITICAL: ShieldAlert,
};

export function ThreatBanner({ fusion }) {
  const level = fusion?.threat_level ?? "SAFE";
  const color = fusion?.color ?? "#1F9D55";
  const Icon = icons[level] ?? CheckCircle2;

  const scenario = fusion?.scenario ?? "Automatic live demo stream";

  return (
    <section className="threatBanner" style={{ borderColor: color, backgroundColor: `${color}18` }}>
      <div className="threatHeader">
        <Icon size={32} color={color} />
        <div>
          <div className="threatLevel" style={{ color }}>
            {level}
          </div>
          <div className="threatMeta">
            threat_score <strong>{(fusion?.threat_score ?? 0).toFixed(3)}</strong>
          </div>
        </div>
      </div>
      <div className="formula">{fusion?.formula_str ?? "threat = 0.000"}</div>
      <div className="scenarioMeta">scenario: {scenario}</div>
      <div className="explanations">
        {(fusion?.explanation?.length ? fusion.explanation : ["Signals are within normal range."]).map((item) => (
          <span key={item}>{item}</span>
        ))}
      </div>
    </section>
  );
}
