import React from 'react';

export default function ConfidenceTimeline() {
  // Mock data points for the SVG path
  const points = "0,150 20,150 40,140 60,110 80,115 100,100 120,80 140,85 160,105 180,85 200,60 220,65 240,55 260,60 280,45 300,50 320,40 340,30 360,35 380,30 400,35 450,25 500,20";
  
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
          Rolling 30 seconds, thart: mapping , "glowing line"
        </div>
        
        <div className="flex-1 relative border-l border-b border-[#333]">
          {/* Y-axis labels */}
          <div className="absolute -left-6 top-0 bottom-0 flex flex-col justify-between text-[10px] text-gray-500 font-mono">
            <span>80</span>
            <span>60</span>
            <span>40</span>
            <span>20</span>
            <span>0</span>
          </div>
          
          {/* X-axis labels */}
          <div className="absolute -bottom-6 left-0 right-0 flex justify-between text-[10px] text-gray-500 font-mono">
            <span>0</span>
            <span>10</span>
            <span>30</span>
            <span className="absolute left-1/2 transform -translate-x-1/2">Time (s)</span>
          </div>
          
          {/* Grid lines */}
          <div className="absolute inset-0 flex justify-between">
            <div className="w-[1px] h-full bg-[#333] border-r border-dashed border-[#555] ml-[33%]"></div>
            <div className="w-[1px] h-full bg-[#333] border-r border-dashed border-[#555] mr-[33%]"></div>
          </div>
          
          {/* The glowing line (SVG) */}
          <svg className="w-full h-full" viewBox="0 0 500 160" preserveAspectRatio="none">
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
            <circle cx="200" cy="60" r="4" fill="#111" stroke="#f59e0b" strokeWidth="2" />
            <circle cx="340" cy="30" r="4" fill="#111" stroke="#ef4444" strokeWidth="2" />
            <circle cx="500" cy="20" r="4" fill="#ef4444" />
          </svg>
          
          {/* Annotations */}
          <div className="absolute top-[35%] left-[32%] bg-[#111] border border-[#333] text-gray-300 font-mono text-[10px] px-2 py-1 rounded">
            AI VOICE DETECTED
          </div>
          <div className="absolute top-[10%] left-[55%] text-threat-red font-mono text-[10px] font-bold">
            SMS HIGH RISK
          </div>
          <div className="absolute top-[20%] right-[5%] text-threat-red font-mono text-[10px] font-bold">
            AI VOICE DETECTED
          </div>
          
          {/* Y-axis label */}
          <div className="absolute -left-8 top-1/2 transform -translate-y-1/2 -rotate-90 text-[10px] text-gray-500 font-mono tracking-widest">
            threat_score
          </div>
        </div>
      </div>
    </div>
  );
}
