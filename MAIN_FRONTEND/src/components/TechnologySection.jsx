import { motion } from 'framer-motion';
import { Cpu, ShieldCheck, Database, ServerOff } from 'lucide-react';

const badges = [
  { icon: Cpu, label: "On-Device LLM", desc: "Powered by quantized models running entirely locally." },
  { icon: ServerOff, label: "Offline-First", desc: "Syncs when internet is available, but never stops working." },
  { icon: ShieldCheck, label: "End-to-End Encrypted", desc: "HIPAA equivalent standards for Indian health data." },
  { icon: Database, label: "ABDM Compliant", desc: "Seamlessly integrates with the Ayushman Bharat Digital Mission." }
];

export default function TechnologySection() {
  return (
    <section className="py-20 bg-white dark:bg-background border-t border-gray-100 dark:border-gray-800">
      <div className="container mx-auto px-6">
        <div className="text-center mb-12">
          <h2 className="text-2xl font-bold text-gray-500 dark:text-gray-400 uppercase tracking-widest text-sm mb-8">
            Built on robust, scalable technology
          </h2>
          
          <div className="flex flex-wrap justify-center gap-4 md:gap-8">
            {badges.map((badge, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: idx * 0.1 }}
                className="flex items-center gap-3 px-6 py-4 bg-gray-50 dark:bg-primary-dark/30 border border-gray-200 dark:border-gray-800 rounded-2xl group hover:border-teal-500 dark:hover:border-teal-500 transition-colors"
              >
                <badge.icon className="w-6 h-6 text-gray-400 group-hover:text-teal-500 transition-colors" />
                <div className="text-left">
                  <p className="font-bold text-gray-900 dark:text-white text-sm">{badge.label}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 hidden sm:block w-48 truncate">{badge.desc}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Fake Certifications Logos */}
        <div className="flex justify-center items-center gap-8 md:gap-16 opacity-50 grayscale hover:grayscale-0 transition-all duration-500 pt-8 border-t border-gray-100 dark:border-gray-800">
          <div className="font-bold text-xl text-gray-400 font-heading tracking-tighter">NHA APPROVED</div>
          <div className="font-bold text-xl text-gray-400 font-heading">ISO 27001</div>
          <div className="font-bold text-xl text-gray-400 font-heading tracking-widest">STARTUP INDIA</div>
        </div>
      </div>
    </section>
  );
}
