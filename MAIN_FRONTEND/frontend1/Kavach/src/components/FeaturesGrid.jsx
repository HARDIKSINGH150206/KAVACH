import React from 'react';
import { motion } from 'framer-motion';
import { WifiOff, Languages, CalendarCheck, BookOpen, Shield, Smartphone } from 'lucide-react';

const features = [
  {
    icon: WifiOff,
    title: "Works Offline",
    description: "On-device AI engine processes triage without needing internet connectivity, crucial for remote villages.",
    gradient: "from-blue-500/20 to-cyan-500/20",
    color: "text-blue-500"
  },
  {
    icon: Languages,
    title: "12 Indian Languages",
    description: "Voice and text support in Hindi, Tamil, Telugu, Marathi, Bengali, and more.",
    gradient: "from-amber-500/20 to-orange-500/20",
    color: "text-amber-500"
  },
  {
    icon: CalendarCheck,
    title: "Govt Hospital Booking",
    description: "Direct integration with ABDM for instant slot booking at the nearest primary health center (PHC).",
    gradient: "from-teal-500/20 to-emerald-500/20",
    color: "text-teal-500"
  },
  {
    icon: BookOpen,
    title: "Instant First-Aid",
    description: "Visual and audio guides for immediate care before reaching a medical facility.",
    gradient: "from-rose-500/20 to-pink-500/20",
    color: "text-rose-500"
  },
  {
    icon: Shield,
    title: "100% Private",
    description: "No data is stored on our servers. Processing happens on-device ensuring patient confidentiality.",
    gradient: "from-purple-500/20 to-fuchsia-500/20",
    color: "text-purple-500"
  },
  {
    icon: Smartphone,
    title: "Low-End Device Support",
    description: "Optimized to run smoothly on ₹3000 entry-level Android smartphones with minimal RAM.",
    gradient: "from-indigo-500/20 to-violet-500/20",
    color: "text-indigo-500"
  }
];

export default function FeaturesGrid() {
  return (
    <section className="py-24 bg-gray-50 dark:bg-background relative">
      <div className="container mx-auto px-6 relative z-10">
        <div className="text-center max-w-2xl mx-auto mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
            Built for the Next Billion
          </h2>
          <p className="text-gray-600 dark:text-gray-400 text-lg">
            Every feature is engineered to overcome the unique challenges of rural healthcare delivery in India.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-50px" }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="glass-card p-8 rounded-3xl hover:-translate-y-2 transition-all duration-300 group cursor-pointer relative overflow-hidden"
            >
              <div className={`absolute inset-0 bg-gradient-to-br ${feature.gradient} opacity-0 group-hover:opacity-100 transition-opacity duration-500`} />
              
              <div className="relative z-10">
                <div className={`w-14 h-14 rounded-2xl bg-white dark:bg-[#0a1929] shadow-sm flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300`}>
                  <feature.icon className={`w-7 h-7 ${feature.color}`} />
                </div>
                
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-3">
                  {feature.title}
                </h3>
                <p className="text-gray-600 dark:text-gray-400 text-sm leading-relaxed">
                  {feature.description}
                </p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
