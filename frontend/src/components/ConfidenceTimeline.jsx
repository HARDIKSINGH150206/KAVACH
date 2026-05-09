import { useEffect, useRef } from "react";

export function ConfidenceTimeline({ points }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const width = canvas.width;
    const height = canvas.height;
    ctx.clearRect(0, 0, width, height);
    ctx.strokeStyle = "#d0d7de22";
    ctx.lineWidth = 1;
    [0.3, 0.55, 0.8].forEach((threshold) => {
      const y = height - threshold * height;
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    });

    if (points.length < 2) return;
    ctx.strokeStyle = "#4fb3ff";
    ctx.lineWidth = 3;
    ctx.beginPath();
    points.forEach((point, index) => {
      const x = (index / (points.length - 1)) * width;
      const y = height - point.score * height;
      if (index === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();
  }, [points]);

  return (
    <section className="panel timelinePanel">
      <div className="panelTitle">
        <span>Confidence Timeline</span>
        <strong>30s</strong>
      </div>
      <canvas ref={canvasRef} width="900" height="160" />
    </section>
  );
}

