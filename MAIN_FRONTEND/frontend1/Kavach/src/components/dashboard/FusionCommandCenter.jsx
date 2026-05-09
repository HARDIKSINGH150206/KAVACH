import React from 'react';

export default function FusionCommandCenter({ score = 0.87, audioScore = 0.81, smsScore = 0.82, config = null }) {
  // Use backend config weights if available, else defaults
  const audioWeight = config?.audio_weight || 0.55;
  const smsWeight = config?.sms_weight || 0.45;
  
  // Calculate needle rotation based on score (0 to 1)
  // -90deg to 90deg is the range for a half-circle gauge
  const rotation = -90 + (score * 180);
  const isCritical = score > 0.80;

  return (
    <div className={`kavach-panel flex flex-col h-full transition-colors duration-500 ${isCritical ? 'border-threat-red/50 shadow-[0_0_20px_rgba(239,68,68,0.15)] bg-[#1a0a0a]' : ''}`}>
      <div className="kavach-panel-header">
        <h2 className="kavach-panel-title">Bayesian Fusion Command Center</h2>
        <div className="flex gap-1">
          <div className="w-1 h-1 bg-gray-500 rounded-full"></div>
          <div className="w-1 h-1 bg-gray-500 rounded-full"></div>
          <div className="w-1 h-1 bg-gray-500 rounded-full"></div>
        </div>
      </div>
      
      <div className="p-3 flex-1 flex flex-col items-center justify-center gap-2 relative min-h-0 overflow-hidden">
        {/* SVG Gauge */}
        <div className="relative w-64 h-32 overflow-hidden flex justify-center items-end">
          <svg viewBox="0 0 200 100" className={`w-full h-full ${isCritical ? 'drop-shadow-[0_0_20px_rgba(239,68,68,0.5)]' : 'drop-shadow-[0_0_15px_rgba(239,68,68,0.3)]'}`}>
            <defs>
              <linearGradient id="gaugeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#10b981" />
                <stop offset="50%" stopColor="#f59e0b" />
                <stop offset="100%" stopColor="#ef4444" />
              </linearGradient>
            </defs>
            {/* Background track */}
            <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="#222" strokeWidth="20" strokeLinecap="round" />
            {/* Colored track */}
            <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="url(#gaugeGrad)" strokeWidth="20" strokeLinecap="round" />
            
            {/* Needle Pivot */}
            <circle cx="100" cy="100" r="8" fill="#444" />
            <circle cx="100" cy="100" r="4" fill="#111" />
          </svg>
          
          {/* Needle - rotating element */}
          <div 
            className="absolute bottom-0 left-1/2 w-1 h-24 bg-gradient-to-t from-transparent via-gray-400 to-white origin-bottom transform -translate-x-1/2 z-10 transition-transform duration-500 ease-out"
            style={{ transform: `translateX(-50%) rotate(${rotation}deg)` }}
          >
            {/* Needle tip */}
            <div className="absolute top-0 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-0 h-0 border-l-[3px] border-r-[3px] border-b-[10px] border-l-transparent border-r-transparent border-b-white"></div>
          </div>
        </div>
        
        <div className="text-gray-400 font-mono text-xs tracking-wider uppercase mt-2">
          threat level
        </div>
        
        <div className="text-xl font-bold font-mono text-center">
          <span className="text-white">Threat Level: </span>
          <span className={isCritical ? "text-threat-red animate-pulse" : "text-safe-green"}>
            {score.toFixed(2)} {isCritical ? "(CRITICAL)" : "(SAFE)"}
          </span>
        </div>
        
        <div className="mt-4 text-center w-full">
          <div className="text-gray-400 font-mono text-[10px] mb-1 uppercase tracking-widest">
            Live Bayesian Formula
          </div>
          <div className={`font-mono text-sm font-bold px-3 py-2 rounded inline-block border transition-colors duration-300 ${isCritical ? 'bg-[#450a0a] border-threat-red text-threat-red shadow-[0_0_15px_rgba(239,68,68,0.3)]' : 'bg-[#064e3b]/30 border-safe-green/20 text-safe-green'}`}>
            <span className="text-gray-400 font-normal">{audioWeight.toFixed(2)} ×</span> {audioScore.toFixed(2)} <span className="text-gray-400 font-normal text-xs">(Audio)</span> 
            <span className="text-gray-400 font-normal mx-1">+</span> 
            <span className="text-gray-400 font-normal">{smsWeight.toFixed(2)} ×</span> {smsScore.toFixed(2)} <span className="text-gray-400 font-normal text-xs">(SMS)</span>
            <span className="text-gray-400 font-normal mx-2">=</span>
            <span className="text-white bg-black/50 px-2 py-1 rounded">{score.toFixed(2)}</span>
          </div>
        </div>
        
        {/* Star icon in bottom right */}
        <div className="absolute bottom-2 right-2 text-gray-600 opacity-50">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2L15 9L22 12L15 15L12 22L9 15L2 12L9 9L12 2Z" />
          </svg>
        </div>
      </div>
    </div>
  );
}
