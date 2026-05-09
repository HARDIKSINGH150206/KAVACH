import React, { useState } from 'react';
import { ShieldCheck, TriangleAlert, Siren, ShieldX, Send } from 'lucide-react';

export default function DemoControls() {
  const [status, setStatus] = useState("Ready");
  const [customSms, setCustomSms] = useState("");

  async function setScenario(scenario) {
    try {
      setStatus(`Setting ${scenario}...`);
      let response = await fetch('/api/v1/demo/scenario', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario })
      });
      
      if (response.status === 404) {
        response = await fetch('/api/demo/scenario', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ scenario })
        });
      }
      
      if (!response.ok) throw new Error('Failed');
      setStatus(scenario === 'auto' ? 'Auto mode' : `${scenario.toUpperCase()} armed`);
    } catch (e) {
      setStatus('Error connecting');
    }
  }

  async function injectCustomSms() {
    const text = customSms.trim();
    if (!text) return;
    
    try {
      setStatus('Scoring SMS...');
      let response = await fetch('/api/v1/sms/mock', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      });
      
      if (response.status === 404) {
        response = await fetch('/api/sms/mock', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });
      }
      
      if (!response.ok) throw new Error('Failed');
      setCustomSms("");
      setStatus('Custom SMS injected');
    } catch (e) {
      setStatus('Error injecting SMS');
    }
  }

  return (
    <div className="flex flex-col gap-2 bg-[#111] border border-[#333] rounded p-2 mt-auto">
      <div className="text-[10px] text-gray-400 font-mono uppercase tracking-widest border-b border-[#333] pb-1">
        God Mode Controls
      </div>
      <div className="text-[9px] text-safe-green font-mono">{status}</div>
      <div className="grid grid-cols-2 gap-2">
        <button 
          onClick={() => setScenario('safe')}
          className="flex items-center justify-center gap-1 bg-[#1a1a1a] hover:bg-[#2a2a2a] border border-[#444] p-1.5 rounded text-[10px] text-gray-300 font-mono transition-colors cursor-pointer"
        >
          <ShieldCheck size={12} className="text-safe-green" /> SAFE
        </button>
        <button 
          onClick={() => setScenario('high')}
          className="flex items-center justify-center gap-1 bg-[#1a1a1a] hover:bg-[#2a2a2a] border border-[#444] p-1.5 rounded text-[10px] text-gray-300 font-mono transition-colors cursor-pointer"
        >
          <TriangleAlert size={12} className="text-yellow-500" /> HIGH
        </button>
        <button 
          onClick={() => setScenario('critical')}
          className="flex items-center justify-center gap-1 bg-[#2a0a0a] hover:bg-[#3a0f0f] border border-threat-red/50 p-1.5 rounded text-[10px] text-threat-red font-mono transition-colors cursor-pointer"
        >
          <Siren size={12} /> CRITICAL
        </button>
        <button 
          onClick={() => setScenario('auto')}
          className="flex items-center justify-center gap-1 bg-[#1a1a1a] hover:bg-[#2a2a2a] border border-[#444] p-1.5 rounded text-[10px] text-gray-300 font-mono transition-colors cursor-pointer"
        >
          <ShieldX size={12} className="text-gray-400" /> AUTO
        </button>
      </div>
      
      {/* Custom SMS Injector */}
      <div className="flex flex-col gap-1 mt-1 border-t border-[#333] pt-2">
        <div className="text-[9px] text-gray-500 font-mono uppercase">Live SMS Injection</div>
        <textarea 
          value={customSms}
          onChange={(e) => setCustomSms(e.target.value)}
          placeholder="Paste a suspicious SMS here..."
          className="bg-[#1a1a1a] border border-[#444] rounded text-[10px] text-gray-300 font-mono p-1.5 resize-none outline-none focus:border-[#666]"
          rows="2"
        />
        <button 
          onClick={injectCustomSms}
          disabled={!customSms.trim()}
          className="flex items-center justify-center gap-1 bg-safe-green/20 hover:bg-safe-green/30 text-safe-green border border-safe-green/30 p-1 rounded text-[10px] font-mono transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Send size={10} /> Send to Inference Engine
        </button>
      </div>
    </div>
  );
}
