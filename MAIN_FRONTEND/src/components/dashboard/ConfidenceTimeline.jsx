export default function ConfidenceTimeline({ history = [] }) {
  // Default points to a flat safe line if no data
  let points = "0,150 500,150";
  let markers = [];
  let annotations = [];

  if (history && history.length > 0) {
    const reversed = [...history].reverse(); // Oldest to newest (left to right)
    const step = 500 / Math.max(reversed.length - 1, 1);
    
    points = reversed.map((event, index) => {
      const x = index * step;
      // threat_score is typically 0.0 to 1.0. Map 0 -> 150 (bottom), 1 -> 20 (top)
      const score = event.threat_score || 0;
      const y = 150 - (score * 130);
      
      // If score is high, maybe add a marker and annotation
      if (score > 0.7) {
        markers.push(
          <circle key={index} cx={x} cy={y} r="4" fill="#111" stroke="#ef4444" strokeWidth="2" />
        );
        
        // Add a few annotations but avoid clutter
        if (index === reversed.length - 1 || index % 10 === 0) {
          annotations.push(
            <div 
              key={`anno-${index}`}
              className="absolute text-threat-red font-mono text-[10px] font-bold z-10"
              style={{ left: `${(x / 500) * 100}%`, top: `${(y / 160) * 100 - 15}%`, transform: 'translateX(-50%)' }}
            >
              CRITICAL THREAT
            </div>
          );
        }
      } else if (score > 0.4) {
        markers.push(
          <circle key={index} cx={x} cy={y} r="3" fill="#111" stroke="#f59e0b" strokeWidth="2" />
        );
      }

      // Special marker for newest point
      if (index === reversed.length - 1) {
        markers.push(
          <circle key="latest" cx={x} cy={y} r="4" fill={score > 0.7 ? "#ef4444" : score > 0.4 ? "#f59e0b" : "#10b981"} />
        );
      }

      return `${x.toFixed(1)},${y.toFixed(1)}`;
    }).join(" ");
  }

  return (
    <div className="kavach-panel h-full flex flex-col">
      <div className="kavach-panel-header">
        <h2 className="kavach-panel-title">Confidence Timeline</h2>
        <div className="flex gap-1">
          <div className="w-1 h-1 bg-gray-500 rounded-full"></div>
          <div className="w-1 h-1 bg-gray-500 rounded-full"></div>
          <div className="w-1 h-1 bg-gray-500 rounded-full"></div>
        </div>
      </div>
      
      <div className="p-4 flex-1 flex flex-col relative">
        <div className="text-xs font-mono text-gray-400 mb-2">
          Rolling timeline of fusion threat scores
        </div>
        
        <div className="flex-1 relative border-l border-b border-[#333]">
          {/* Y-axis labels */}
          <div className="absolute -left-6 top-0 bottom-0 flex flex-col justify-between text-[10px] text-gray-500 font-mono">
            <span>1.0</span>
            <span>0.8</span>
            <span>0.6</span>
            <span>0.4</span>
            <span>0.2</span>
            <span>0.0</span>
          </div>
          
          {/* X-axis labels */}
          <div className="absolute -bottom-6 left-0 right-0 flex justify-between text-[10px] text-gray-500 font-mono">
            <span>T-50s</span>
            <span>T-30s</span>
            <span>T-10s</span>
            <span className="absolute left-1/2 transform -translate-x-1/2 text-gray-400">Time</span>
            <span>NOW</span>
          </div>
          
          {/* Grid lines */}
          <div className="absolute inset-0 flex justify-between">
            <div className="w-[1px] h-full bg-[#333] border-r border-dashed border-[#555] ml-[33%]"></div>
            <div className="w-[1px] h-full bg-[#333] border-r border-dashed border-[#555] mr-[33%]"></div>
          </div>
          
          {/* The glowing line (SVG) */}
          <svg className="w-full h-full relative z-0" viewBox="0 0 500 160" preserveAspectRatio="none">
            <defs>
              <linearGradient id="lineGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#10b981" />
                <stop offset="30%" stopColor="#10b981" />
                <stop offset="60%" stopColor="#f59e0b" />
                <stop offset="80%" stopColor="#ef4444" />
                <stop offset="100%" stopColor="#ef4444" />
              </linearGradient>
              <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="3" result="blur" />
                <feMerge>
                  <feMergeNode in="blur" />
                  <feMergeNode in="SourceGraphic" />
                </feMerge>
              </filter>
            </defs>
            
            {/* Base line with glow */}
            <polyline 
              points={points} 
              fill="none" 
              stroke="url(#lineGrad)" 
              strokeWidth="3" 
              filter="url(#glow)"
              strokeLinejoin="round"
              strokeLinecap="round"
            />
            
            {/* Markers */}
            {markers}
          </svg>
          
          {/* Dynamic Annotations */}
          {annotations}
          
          {/* Y-axis label */}
          <div className="absolute -left-8 top-1/2 transform -translate-y-1/2 -rotate-90 text-[10px] text-gray-500 font-mono tracking-widest">
            threat_score
          </div>
        </div>
      </div>
    </div>
  );
}
