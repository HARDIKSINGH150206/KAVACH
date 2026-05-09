import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Mic, Activity, AlertTriangle, ShieldCheck } from 'lucide-react';

export default function LiveDemoSection() {
  const [input, setInput] = useState('');
  const [chat, setChat] = useState([
    { sender: 'ai', text: 'Namaste! How can I help you today? Please describe your symptoms.', severity: null }
  ]);
  const [isTyping, setIsTyping] = useState(false);

  const handleSend = (e) => {
    e?.preventDefault();
    if (!input.trim()) return;

    const userMsg = input;
    setChat(prev => [...prev, { sender: 'user', text: userMsg }]);
    setInput('');
    setIsTyping(true);

    // Mock AI delay and response logic
    setTimeout(() => {
      setIsTyping(false);
      let responseText = '';
      let severity = 'green'; // green, yellow, red

      const lowerInput = userMsg.toLowerCase();
      if (lowerInput.includes('chest pain') || lowerInput.includes('breath')) {
        responseText = 'Based on your symptoms (chest pain/breathing issues), this could be a medical emergency. Please seek immediate care at the nearest hospital or call 108.';
        severity = 'red';
      } else if (lowerInput.includes('fever') && lowerInput.includes('days')) {
        responseText = 'A prolonged fever requires monitoring. Please stay hydrated and visit a local clinic if it does not subside in 24 hours. Would you like a booking?';
        severity = 'yellow';
      } else {
        responseText = 'It sounds like a mild condition. Please take rest and drink plenty of fluids. I have attached a basic first-aid guide for you.';
        severity = 'green';
      }

      setChat(prev => [...prev, { sender: 'ai', text: responseText, severity }]);
    }, 1500);
  };

  return (
    <section className="py-24 bg-white dark:bg-primary-dark">
      <div className="container mx-auto px-6">
        <div className="flex flex-col lg:flex-row gap-16 items-center">
          
          {/* Left Text */}
          <div className="flex-1 text-center lg:text-left">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-6">
              Experience the Magic. <br/>
              <span className="text-teal-500">Try it yourself.</span>
            </h2>
            <p className="text-lg text-gray-600 dark:text-gray-400 mb-8 max-w-xl">
              Type a symptom like <span className="font-semibold text-gray-800 dark:text-gray-200">"mild fever"</span>, <span className="font-semibold text-gray-800 dark:text-gray-200">"fever for 3 days"</span>, or <span className="font-semibold text-rose-500">"severe chest pain"</span> to see how our AI triages responses instantly. No login required.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
              <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                <ShieldCheck className="w-5 h-5 text-teal-500" />
                100% Private & Secure
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                <Activity className="w-5 h-5 text-amber-500" />
                No Data Stored
              </div>
            </div>
          </div>

          {/* Right Widget */}
          <div className="flex-1 w-full max-w-md">
            <div className="glass-card rounded-[2rem] overflow-hidden border border-gray-200 dark:border-gray-800 shadow-2xl">
              {/* Header */}
              <div className="bg-teal-500 text-white p-6 flex items-center gap-4 rounded-b-3xl shadow-lg relative z-10">
                <div className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center backdrop-blur-sm">
                  <Activity className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="font-bold text-lg leading-tight">MediChain AI</h3>
                  <p className="text-teal-100 text-sm">Always online</p>
                </div>
              </div>

              {/* Chat Body */}
              <div className="h-[350px] bg-gray-50 dark:bg-[#0a1929]/50 p-6 overflow-y-auto flex flex-col gap-4">
                <AnimatePresence>
                  {chat.map((msg, idx) => (
                    <motion.div
                      key={idx}
                      initial={{ opacity: 0, y: 10, scale: 0.95 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      className={`max-w-[85%] rounded-2xl p-4 text-sm ${
                        msg.sender === 'user' 
                          ? 'bg-teal-500 text-white rounded-tr-sm self-end' 
                          : 'bg-white dark:bg-primary border border-gray-100 dark:border-gray-800 text-gray-800 dark:text-gray-200 rounded-tl-sm self-start shadow-sm'
                      }`}
                    >
                      {msg.text}
                      
                      {msg.sender === 'ai' && msg.severity && (
                        <div className={`mt-3 pt-3 border-t ${msg.sender === 'user' ? 'border-teal-400' : 'border-gray-100 dark:border-gray-800'} flex items-center gap-2 font-semibold text-xs`}>
                          {msg.severity === 'red' && <><AlertTriangle className="w-4 h-4 text-rose-500" /><span className="text-rose-500">EMERGENCY</span></>}
                          {msg.severity === 'yellow' && <><AlertTriangle className="w-4 h-4 text-amber-500" /><span className="text-amber-500">MONITOR</span></>}
                          {msg.severity === 'green' && <><ShieldCheck className="w-4 h-4 text-teal-500" /><span className="text-teal-500">SAFE / MILD</span></>}
                        </div>
                      )}
                    </motion.div>
                  ))}
                </AnimatePresence>
                {isTyping && (
                  <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="self-start bg-white dark:bg-primary border border-gray-100 dark:border-gray-800 text-gray-500 p-4 rounded-2xl rounded-tl-sm shadow-sm flex gap-1">
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </motion.div>
                )}
              </div>

              {/* Input Area */}
              <div className="p-4 bg-white dark:bg-primary border-t border-gray-100 dark:border-gray-800">
                <form onSubmit={handleSend} className="flex items-center gap-2 bg-gray-100 dark:bg-primary-dark p-2 rounded-full">
                  <button type="button" className="p-2 text-gray-500 hover:text-teal-500 transition-colors">
                    <Mic className="w-5 h-5" />
                  </button>
                  <input 
                    type="text" 
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Type your symptoms..."
                    className="flex-1 bg-transparent border-none outline-none text-sm text-gray-800 dark:text-gray-200"
                  />
                  <button type="submit" disabled={!input.trim()} className="p-2 bg-teal-500 text-white rounded-full disabled:opacity-50 disabled:cursor-not-allowed hover:bg-teal-600 transition-colors">
                    <Send className="w-4 h-4" />
                  </button>
                </form>
              </div>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
