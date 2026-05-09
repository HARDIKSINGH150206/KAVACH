import { Shield, Cpu, Network, Lock, ChevronRight, Zap } from 'lucide-react';

export default function LandingPage({ onLaunch }) {
  return (
    <div className="min-h-screen bg-[#0a0a0a] text-gray-200 font-mono flex flex-col relative overflow-hidden">
      {/* Background visual elements */}
      <div className="absolute inset-0 z-0 opacity-20 pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-threat-red rounded-full mix-blend-screen filter blur-[100px] animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-safe-green rounded-full mix-blend-screen filter blur-[100px] opacity-50"></div>
        <div className="absolute inset-0" style={{ backgroundImage: 'linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px)', backgroundSize: '50px 50px' }}></div>
      </div>

      <header className="relative z-10 w-full p-6 flex justify-between items-center border-b border-[#333]">
        <div className="flex items-center gap-3">
          <Shield className="text-threat-red" size={28} />
          <span className="text-2xl font-bold tracking-widest text-white">KAVACH</span>
        </div>
        <div className="flex items-center gap-2 border border-safe-green/30 bg-safe-green-dark/20 px-3 py-1.5 text-safe-green text-xs tracking-wider">
          <div className="w-2 h-2 bg-safe-green rounded-full animate-pulse"></div>
          SYSTEM SECURE
        </div>
      </header>

      <main className="relative z-10 flex-1 flex flex-col items-center justify-center p-6 text-center">
        <div className="max-w-3xl flex flex-col items-center gap-8">
          
          <div className="space-y-4">
            <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-white drop-shadow-[0_0_15px_rgba(255,255,255,0.1)]">
              Next-Gen <span className="text-threat-red">Protection</span>
            </h1>
            <p className="text-xl md:text-2xl text-gray-400 max-w-2xl mx-auto leading-relaxed">
              India's First Real-Time, Offline Dual-Vector AI Shield.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full mt-8">
            <div className="kavach-panel p-6 flex flex-col items-center text-center gap-4 hover:border-gray-500 transition-colors">
              <div className="p-3 bg-[#1a1a1a] rounded-full border border-[#333]">
                <Cpu className="text-gray-300" size={24} />
              </div>
              <h3 className="font-bold text-white tracking-wide">100% Offline AI</h3>
              <p className="text-sm text-gray-500">
                Zero data leaves your device. All inference runs locally ensuring absolute privacy.
              </p>
            </div>
            
            <div className="kavach-panel p-6 flex flex-col items-center text-center gap-4 hover:border-threat-red/50 transition-colors">
              <div className="p-3 bg-[#1a0a0a] rounded-full border border-threat-red/30">
                <Network className="text-threat-red" size={24} />
              </div>
              <h3 className="font-bold text-white tracking-wide">Dual-Vector Fusion</h3>
              <p className="text-sm text-gray-500">
                Simultaneous analysis of live audio and SMS text streams using Bayesian fusion models.
              </p>
            </div>

            <div className="kavach-panel p-6 flex flex-col items-center text-center gap-4 hover:border-gray-500 transition-colors">
              <div className="p-3 bg-[#1a1a1a] rounded-full border border-[#333]">
                <Lock className="text-gray-300" size={24} />
              </div>
              <h3 className="font-bold text-white tracking-wide">MHA/CERT-In Ready</h3>
              <p className="text-sm text-gray-500">
                Designed for seamless integration with national cyber security infrastructures.
              </p>
            </div>
          </div>

          <div className="mt-12 w-full flex justify-center">
            <button
              type="button"
              onClick={onLaunch}
              onKeyDown={(event) => {
                if (event.key === 'Enter' || event.key === ' ') {
                  event.preventDefault();
                  onLaunch?.();
                }
              }}
              className="group relative px-8 py-4 bg-threat-red text-white font-bold tracking-widest uppercase flex items-center gap-3 overflow-hidden transition-all hover:bg-threat-red-dark hover:shadow-[0_0_30px_rgba(239,68,68,0.4)] cursor-pointer focus:outline-none focus:ring-2 focus:ring-safe-green focus:ring-offset-2 focus:ring-offset-[#0a0a0a]"
              aria-label="Open dashboard"
            >
              <div className="absolute inset-0 w-full h-full bg-white/20 -translate-x-full group-hover:animate-[shimmer_1.5s_infinite] pointer-events-none"></div>
              <Zap size={20} className="relative z-10" />
              <span className="relative z-10">Initialize Command Center</span>
              <ChevronRight size={20} className="relative z-10 group-hover:translate-x-1 transition-transform" />
            </button>
          </div>

          <div className="mt-4 flex flex-wrap items-center justify-center gap-3 text-xs text-gray-500">
            <button
              type="button"
              onClick={onLaunch}
              className="underline decoration-dotted underline-offset-4 hover:text-white transition-colors"
            >
              Open dashboard
            </button>
            <span className="hidden sm:inline">or press Enter when focused here</span>
            <span className="sm:hidden">tap the launch button above</span>
          </div>
          
        </div>
      </main>

      <footer className="relative z-10 w-full p-4 border-t border-[#333] flex justify-between items-center text-[10px] text-gray-600 uppercase tracking-widest">
        <span>v2.0.4.891 / KAVACH CORE</span>
        <span>AASIST 96%+ ACCURACY</span>
      </footer>

      <style dangerouslySetInnerHTML={{__html: `
        @keyframes shimmer {
          100% { transform: translateX(100%); }
        }
      `}} />
    </div>
  );
}
