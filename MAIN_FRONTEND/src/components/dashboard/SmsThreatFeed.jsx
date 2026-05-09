import { ChevronDown } from 'lucide-react';

export default function SmsThreatFeed({ smsEvents = [] }) {
  const latestSms = smsEvents.length > 0 ? smsEvents[0] : null;

  if (!latestSms) {
    return (
      <div className="kavach-panel h-full flex flex-col">
        <div className="kavach-panel-header">
          <h2 className="kavach-panel-title">SMS Threat Feed</h2>
          <div className="flex gap-1">
            <div className="w-1 h-1 bg-gray-500 rounded-full"></div>
            <div className="w-1 h-1 bg-gray-500 rounded-full"></div>
            <div className="w-1 h-1 bg-gray-500 rounded-full"></div>
          </div>
        </div>
        <div className="p-3 flex-1 flex flex-col items-center justify-center text-gray-500">
          No SMS intercepted yet.
        </div>
      </div>
    );
  }

  return (
    <div className="kavach-panel h-full flex flex-col">
      <div className="kavach-panel-header">
        <h2 className="kavach-panel-title">SMS Threat Feed</h2>
        <div className="flex gap-1">
          <div className="w-1 h-1 bg-gray-500 rounded-full"></div>
          <div className="w-1 h-1 bg-gray-500 rounded-full"></div>
          <div className="w-1 h-1 bg-gray-500 rounded-full"></div>
        </div>
      </div>
      
      <div className="p-3 flex-1 flex flex-col gap-2 overflow-y-auto">
        {/* Terminal Tags */}
        <div className="flex justify-between text-[10px] font-mono text-gray-400 flex-wrap gap-1">
          <div className="flex gap-2">
            <span className="bg-[#222] px-1 rounded">Terminal: Metadata</span>
            <span className="bg-[#222] px-1 rounded">source: {latestSms.ml_source || 'unknown'}</span>
          </div>
          <span className="whitespace-nowrap">Top Tags</span>
        </div>
        <div className="flex gap-2 text-[10px] font-mono text-gray-400 flex-wrap">
          <span className="bg-[#222] px-1 rounded">TLD: {latestSms.tld || '.in'}</span>
          <span className="bg-[#222] px-1 rounded">Entropy: {latestSms.entropy?.toFixed(2) || 'N/A'}</span>
          <span className="bg-[#222] px-1 rounded text-threat-red">Spoofed Sender: {latestSms.scam_type === 'spoofing' ? latestSms.scam_type : 'Unknown'}</span>
        </div>
        
        <div className="flex justify-between text-[10px] font-mono text-gray-500 mt-1">
          <span>Message timestamp: {latestSms.timestamp ? new Date(latestSms.timestamp * 1000).toLocaleTimeString() : 'N/A'}</span>
          <span>Metadata Tags</span>
        </div>
        
        {/* NLP Analysis Card */}
        <div className={`border rounded p-3 flex flex-col gap-2 relative transition-colors duration-300 ${latestSms.riskScore > 0.7 ? 'border-threat-red/50 bg-threat-red-dark/10' : 'border-[#333] bg-[#151515]'}`}>
          <div className="flex justify-between items-start">
            <div className="text-gray-300 font-mono text-sm font-bold">
              MuRIL NLP Analysis
              <div className="text-gray-500 font-normal text-xs">Hinglish/Hindi</div>
            </div>
            <ChevronDown size={16} className={latestSms.riskScore > 0.7 ? "text-threat-red animate-pulse" : "text-safe-green"} />
          </div>
          
          <div className="text-sm text-gray-300 font-mono leading-relaxed">
            {latestSms.text ? (
              latestSms.text.split(' ').map((word, i) => {
                const isHighlight = latestSms.highlights?.find(h => word.toLowerCase().includes(h.word.toLowerCase()));
                if (isHighlight) {
                  return <span key={i} className="text-threat-red font-bold"> {word} </span>;
                }
                return <span key={i}> {word} </span>;
              })
            ) : "No SMS intercepted."}
          </div>
          
          <div className="text-xs font-mono text-gray-400 mt-2 bg-black/40 p-2 rounded">
            <div className="font-bold text-gray-300 mb-1">Explainable AI Triggers:</div>
            {latestSms.highlights?.map((h, i) => (
              <span key={i} className="mr-3 block sm:inline-block">
                Word '{h.word}' <span className="text-threat-red">→ {h.score}</span>
              </span>
            ))}
            {latestSms.entropy > 4 && (
              <span className="block mt-1">URL Entropy {latestSms.entropy?.toFixed(2)} <span className="text-threat-red">→ +0.22</span></span>
            )}
          </div>
          
          <div className={`text-sm font-mono font-bold mt-2 ${latestSms.riskScore > 0.7 ? 'text-threat-red' : 'text-safe-green'}`}>
            SMS Risk Score: {latestSms.riskScore?.toFixed(2) || 0.0}
          </div>
        </div>
        
        {/* Explainable Score note */}
        <div className="mt-auto">
          <div className="flex justify-between items-center text-gray-300 text-sm font-bold border-t border-[#333] pt-3">
            <span>Explainable Score</span>
            <div className="flex gap-1">
              <div className="w-1 h-1 bg-gray-500 rounded-full"></div>
              <div className="w-1 h-1 bg-gray-500 rounded-full"></div>
              <div className="w-1 h-1 bg-gray-500 rounded-full"></div>
            </div>
          </div>
          <div className="text-xs font-mono text-gray-500 mt-1">
            KAVACH isn't a black box.<br/>
            Scores are auditable for<br/>
            banks/government.
          </div>
        </div>
      </div>
    </div>
  );
}
