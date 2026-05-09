const GRID_PATTERN_URL = `url("data:image/svg+xml,%3Csvg width='100%25' height='100%25' xmlns='http://www.w3.org/2000/svg'%3E%3Cdefs%3E%3Cpattern id='grid' width='4' height='4' patternUnits='userSpaceOnUse'%3E%3Cpath d='M 4 0 L 0 0 0 4' fill='none' stroke='rgba(255,255,255,0.05)' stroke-width='1'/%3E%3C/pattern%3E%3C/defs%3E%3Crect width='100%25' height='100%25' fill='url(%23grid)' /%3E%3C/svg%3E")`;

export default function LiveSpectrogram({ transcripts = [], ganDetected = false, audioScore = 0.0 }) {
  const displayTranscripts = transcripts.length > 0 ? transcripts : [];

  return (
    <div className={`kavach-panel flex flex-col h-full transition-colors duration-500 ${ganDetected ? 'border-threat-red/50 shadow-[0_0_20px_rgba(239,68,68,0.1)]' : ''}`}>
      <div className="kavach-panel-header">
        <h2 className="kavach-panel-title flex items-center gap-2">
          KAVACH Live Spectrogram
          {ganDetected && <span className="w-2 h-2 rounded-full bg-threat-red animate-pulse"></span>}
        </h2>
        <div className="flex gap-1">
          <div className="w-1 h-1 bg-gray-500 rounded-full"></div>
          <div className="w-1 h-1 bg-gray-500 rounded-full"></div>
          <div className="w-1 h-1 bg-gray-500 rounded-full"></div>
        </div>
      </div>
      
      <div className="p-4 flex-1 flex flex-col gap-3">
        <div className="text-xs font-mono text-gray-400 flex justify-between">
          <span>AASIST runtime | Live Audio Score: <span className={ganDetected ? "text-threat-red font-bold" : "text-safe-green"}>{audioScore.toFixed(3)}</span> | Transcript stream</span>
        </div>
        
        {/* Spectrogram Mockup */}
        <div className="relative w-full h-32 bg-black rounded border border-[#222] overflow-hidden flex flex-col shrink-0">
          {/* Y Axis Labels */}
          <div className="absolute left-2 top-2 bottom-2 flex flex-col justify-between text-[10px] text-gray-500 font-mono z-10">
            <span>16kHz</span>
            <span>12kHz</span>
            <span>38Hz</span>
            <span>0</span>
          </div>
          
          {/* Spectrogram Graphic (CSS gradient mockup) */}
          <div className="absolute inset-0 opacity-80" 
               style={{
                 backgroundImage: `${ganDetected ? 'linear-gradient(to top, rgba(239,68,68,0.2), transparent)' : 'linear-gradient(to top, rgba(16,185,129,0.1), transparent)'}, ${GRID_PATTERN_URL}`,
                 backgroundRepeat: 'no-repeat, repeat',
                 backgroundSize: 'cover, auto',
                 backgroundPosition: 'center, center',
               }}>
            {/* Fake wave peaks - CLI style (crisp, narrow bars) */}
            <div className="absolute bottom-0 w-full h-full flex items-end justify-around px-2 opacity-80 mix-blend-screen">
              {[40, 60, 30, 80, 50, 90, 70, 45, 85, 35, 65, 55, 75, 20, 50, 80, 40, 95, 60, 30].map((h, i) => (
                <div 
                  key={i} 
                  className={`w-[3%] mx-[1px] animate-pulse ${ganDetected ? 'bg-gradient-to-t from-red-600 to-orange-400' : 'bg-gradient-to-t from-emerald-600 to-teal-400'}`}
                  style={{ height: `${h}%`, animationDelay: `${i * 0.1}s` }}
                ></div>
              ))}
            </div>
            {ganDetected && <div className="absolute bottom-[20%] left-[25%] w-[40%] h-[20%] bg-threat-red blur-xl mix-blend-screen opacity-40 animate-pulse"></div>}
          </div>
          
          {/* GAN Artifact Badge */}
          {ganDetected && (
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-20">
              <div className="border border-threat-red bg-threat-red-dark/80 text-threat-red px-3 py-1 font-mono text-xs font-bold shadow-[0_0_10px_rgba(239,68,68,0.5)] animate-pulse">
                GAN ARTIFACT DETECTED
              </div>
            </div>
          )}
        </div>

        {/* Transcripts */}
        <div className="mt-2 flex-1 bg-[#0a0a0a] border border-[#222] rounded p-3 overflow-hidden relative min-h-0">
          <div className="absolute right-2 top-2 bottom-2 w-1 bg-[#222] rounded-full">
            <div className="w-full h-1/3 bg-gray-500 rounded-full mt-2"></div>
          </div>
          <div className="font-mono text-xs text-gray-300 leading-relaxed flex flex-col gap-1 overflow-y-auto h-full pr-3">
            {displayTranscripts.length === 0 && (
              <div className="text-gray-500">Waiting for transcript events...</div>
            )}
            {displayTranscripts.map((t, i) => (
              <div key={i}>{t.text || JSON.stringify(t)}</div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
