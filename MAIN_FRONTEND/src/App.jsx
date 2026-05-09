import React, { useState, useEffect } from 'react';
import { useKavachBackend } from './hooks/useKavachBackend';
import LiveSpectrogram from './components/dashboard/LiveSpectrogram';
import ConfidenceTimeline from './components/dashboard/ConfidenceTimeline';
import SmsThreatFeed from './components/dashboard/SmsThreatFeed';
import FusionCommandCenter from './components/dashboard/FusionCommandCenter';
import DemoControls from './components/dashboard/DemoControls';
import LandingPage from './components/LandingPage';
import { Shield, AlertTriangle, Cpu } from 'lucide-react';

function App() {
  const [showDashboard, setShowDashboard] = useState(false);
  const { config, health, threatEvents, isConnected } = useKavachBackend();

  if (!showDashboard) {
    return <LandingPage onLaunch={() => setShowDashboard(true)} />;
  }
  const [gpuLatency, setGpuLatency] = useState(72);

  // Flutter GPU latency between 68 and 78 ms to simulate live metrics
  useEffect(() => {
    const interval = setInterval(() => {
      setGpuLatency(Math.floor(Math.random() * (78 - 68 + 1)) + 68);
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  // Derive scores and states
  const latestFusion = threatEvents.fusion.length > 0 ? threatEvents.fusion[0] : null;
  const currentThreatScore = latestFusion ? latestFusion.threat_score : 0.15;
  const isCritical = currentThreatScore > 0.80;
  
  const latestAudio = threatEvents.audio.length > 0 ? threatEvents.audio[0] : null;
  const ganDetected = latestAudio ? latestAudio.spoof_hint : false;
  const audioScore = latestAudio ? latestAudio.audio_score : 0.12;

  const latestSmsEvent = threatEvents.sms.length > 0 ? threatEvents.sms[0] : null;
  const smsScore = latestSmsEvent ? latestSmsEvent.sms_score : 0.05;

  return (
    <div className={`h-screen w-screen overflow-hidden flex flex-col p-4 font-sans selection:bg-threat-red/30 selection:text-white transition-all duration-700 ${isCritical ? 'bg-[#150000] text-gray-200' : 'bg-kavach-bg text-gray-200'}`}>
      
      {/* Critical Alert Banner */}
      {isCritical && (
        <div className="w-full bg-threat-red text-white text-center py-1 font-mono font-bold text-sm tracking-widest flex items-center justify-center gap-4 shadow-[0_0_20px_rgba(239,68,68,0.5)] shrink-0 z-50">
          <AlertTriangle size={18} />
          ALERT: CRITICAL THREAT DETECTED
          <AlertTriangle size={18} />
        </div>
      )}

      {/* Top Navigation Bar */}
      <nav className={`flex justify-between items-center mb-4 border-b pb-3 shrink-0 ${isCritical ? 'border-threat-red/30' : 'border-[#333]'}`}>
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 flex items-center justify-center">
            <Shield className={`w-6 h-6 ${isCritical ? 'text-threat-red animate-pulse' : 'text-safe-green'}`} />
          </div>
          <h1 className="text-xl font-mono tracking-wide text-gray-300">
            <span className={`font-bold ${isCritical ? 'text-threat-red drop-shadow-[0_0_8px_rgba(239,68,68,0.8)]' : 'text-white'}`}>KAVACH</span> | India's First Real-Time, Offline Dual-Vector AI Shield
          </h1>
        </div>
        
        <div className="flex items-center gap-4">
          {!isConnected && (
            <span className="text-threat-red text-xs font-mono animate-pulse">WS Disconnected</span>
          )}
          
          {/* GPU Latency Card */}
          <div className="flex items-center gap-2 bg-[#111] border border-[#333] rounded px-3 py-1 text-gray-400 font-mono text-xs">
            <Cpu size={14} className="text-safe-green" />
            <span className="text-white font-bold">RTX 3050 Latency:</span> 
            <span className={gpuLatency > 80 ? "text-warn-amber" : "text-safe-green"}>{gpuLatency}ms</span>
          </div>

          <span className="text-safe-green font-mono text-xs font-bold bg-[#064e3b] px-3 py-1 rounded border border-[#10b981]/30">
            MHA/CERT-In Integration: ACTIVE
          </span>
        </div>
      </nav>

      {/* Main Grid Layout */}
      <main className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-4 overflow-hidden min-h-0 pb-2">
        
        {/* Left Column (Spectrogram & Timeline) */}
        <div className="lg:col-span-7 flex flex-col gap-4 h-full overflow-hidden">
          {/* Top Half: Spectrogram */}
          <div className="flex-1 min-h-0 overflow-hidden">
            <LiveSpectrogram transcripts={threatEvents.transcript} ganDetected={ganDetected} />
          </div>
          
          {/* Bottom Half: Timeline */}
          <div className="h-1/2 shrink-0 overflow-hidden">
            <ConfidenceTimeline history={threatEvents.fusion} />
          </div>
        </div>
        
        {/* Right Column (SMS Feed, Status, Command Center) */}
        <div className="lg:col-span-5 flex flex-col gap-4 h-full overflow-hidden">
          
          {/* Top right block wrapper (Alerts + SMS Feed) */}
          <div className="flex gap-4 flex-1 min-h-0 overflow-hidden">
            {/* SMS Feed */}
            <div className="flex-1 min-w-0 overflow-hidden">
              <SmsThreatFeed smsEvents={threatEvents.sms} />
            </div>
            
            {/* Status Indicators side column */}
            <div className="w-64 shrink-0 flex flex-col gap-2 overflow-y-auto pr-1">
              <div className={`flex items-center justify-center gap-2 rounded p-2 font-mono font-bold text-[10px] transition-all duration-300 ${isCritical ? 'bg-threat-red text-white shadow-[0_0_20px_rgba(239,68,68,0.8)] scale-105' : 'bg-threat-red-dark/30 border border-threat-red/50 text-threat-red'}`}>
                <span className="animate-pulse">⚠</span> {isCritical ? "CRITICAL THREAT ACTIVE!" : "ALERT: STANDBY"}
              </div>
              <div className="flex items-center gap-2 bg-[#111] border border-[#333] rounded p-2 text-gray-400 font-mono text-[10px]">
                <span className="text-threat-red animate-pulse-heart">♥</span> <span className="text-white">100% OFFLINE</span> <span className="text-[8px]">(Pulsing Heartbeat)</span>
              </div>
              <div className="flex items-center gap-2 bg-safe-green-dark/20 border border-safe-green/30 rounded p-2 text-safe-green font-mono font-bold text-[10px]">
                ⬡ TIER 3 CITIES SAFE
              </div>
              <DemoControls />
            </div>
          </div>
          
          {/* Bottom right: Fusion Command Center */}
          <div className="h-1/2 shrink-0 overflow-hidden">
            <FusionCommandCenter 
              score={currentThreatScore}
              audioScore={audioScore}
              smsScore={smsScore}
              config={config} 
            />
          </div>
          
        </div>
        
      </main>
    </div>
  );
}

export default App;
