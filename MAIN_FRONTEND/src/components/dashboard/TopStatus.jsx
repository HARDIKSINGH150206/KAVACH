import React from 'react';
import { AlertTriangle, Heart, ShieldCheck, Cpu } from 'lucide-react';

export default function TopStatus() {
  return (
    <div className="flex flex-col gap-2 w-full">
      <div className="flex justify-end mb-2">
        <span className="text-safe-green font-mono text-xs font-bold bg-[#064e3b] px-3 py-1 rounded border border-[#10b981]/30">
          MHA/CERT-In Integration: ACTIVE
        </span>
      </div>
      
      <div className="flex items-center gap-3 bg-threat-red-dark/30 border border-threat-red/50 rounded-md p-3 text-threat-red font-mono font-bold text-sm shadow-[0_0_15px_rgba(239,68,68,0.2)]">
        <AlertTriangle size={18} className="animate-pulse" />
        ALERT: CRITICAL THREAT!
      </div>
      
      <div className="flex items-center gap-3 bg-[#111] border border-[#333] rounded-md p-3 text-gray-400 font-mono text-xs">
        <Heart size={16} className="text-threat-red animate-pulse-heart" />
        <span className="text-white font-bold">100% OFFLINE</span> (Pulsing Heartbeat)
      </div>
      
      <div className="flex items-center gap-3 bg-safe-green-dark/20 border border-safe-green/30 rounded-md p-3 text-safe-green font-mono font-bold text-xs">
        <ShieldCheck size={16} />
        TIER 3 CITIES SAFE
      </div>
      
      <div className="flex items-center gap-3 bg-[#111] border border-[#333] rounded-md p-3 text-gray-400 font-mono text-xs">
        <Cpu size={16} className="text-safe-green" />
        <span className="text-white font-bold">RTX 3050 GPU Latency:</span> 78ms
      </div>
    </div>
  );
}
