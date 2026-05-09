import { useEffect, useRef } from "react";

export function Spectrogram({ melData, audioScore }) {
  const canvasRef = useRef(null);
  const historyRef = useRef([]);

  useEffect(() => {
    if (!melData || !canvasRef.current) return;
    historyRef.current.push(melData);
    historyRef.current = historyRef.current.slice(-24);

    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    const width = canvas.width;
    const height = canvas.height;
    ctx.clearRect(0, 0, width, height);

    const colWidth = width / historyRef.current.length;
    historyRef.current.forEach((frame, frameIndex) => {
      const bins = frame.length;
      const rowHeight = height / bins;
      frame.forEach((row, rowIndex) => {
        const value = Array.isArray(row) ? Math.max(...row) : row;
        const normalized = Math.max(0, Math.min(1, (value + 80) / 80));
        const artifact = audioScore > 0.6 && normalized > 0.58;
        const red = artifact ? 210 : 35 + normalized * 80;
        const green = artifact ? 60 : 120 + normalized * 80;
        const blue = artifact ? 55 : 190 + normalized * 45;
        ctx.fillStyle = `rgba(${red}, ${green}, ${blue}, ${0.25 + normalized * 0.7})`;
        ctx.fillRect(frameIndex * colWidth, height - (rowIndex + 1) * rowHeight, colWidth + 1, rowHeight + 1);
      });
    });
  }, [melData, audioScore]);

  return (
    <section className="panel spectrogramPanel">
      <div className="panelTitle">
        <span>Live Spectrogram</span>
        <strong className={audioScore > 0.6 ? "danger" : "ok"}>
          audio {(audioScore ?? 0).toFixed(3)}
        </strong>
      </div>
      <canvas ref={canvasRef} width="900" height="280" />
    </section>
  );
}

