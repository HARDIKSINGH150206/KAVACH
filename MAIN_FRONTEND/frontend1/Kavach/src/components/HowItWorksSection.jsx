import React from 'react';
import { motion } from 'framer-motion';
import { Mic, BrainCircuit, HeartPulse } from 'lucide-react';

const steps = [
  {
    id: 1,
    title: "Describe Symptoms",
    description: "Speak or type your symptoms in your local language. No complex medical terms needed.",
    icon: Mic,
    color: "text-teal-500",
    bg: "bg-teal-50",
    darkBg: "dark:bg-teal-500/10"
  },
  {
    id: 2,
    title: "AI Triage & Analysis",
    description: "Our on-device AI instantly analyzes the symptoms to determine the severity (Emergency, Monitor, or Safe).",
    icon: BrainCircuit,
    color: "text-amber-500",
    bg: "bg-amber-50",
    darkBg: "dark:bg-amber-500/10"
  },
  {
    id: 3,
    title: "First-Aid & Booking",
    description: "Get immediate visual first-aid guidance and auto-book the nearest available government doctor.",
    icon: HeartPulse,
    color: "text-rose-500",
    bg: "bg-rose-50",
    darkBg: "dark:bg-rose-500/10"
  }
];

export default function HowItWorksSection() {
  return (
    <section className="py-24 bg-gray-50 dark:bg-[#06121e] relative overflow-hidden">
      <div className="container mx-auto px-6 relative z-10">
        <div className="text-center max-w-3xl mx-auto mb-20">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
            How MediChain Works
          </h2>
          <p className="text-gray-600 dark:text-gray-400 text-lg">
            A simple 3-step process designed for users with zero digital literacy, guided entirely by voice and visuals.
          </p>
        </div>

        <div className="relative max-w-5xl mx-auto">
          {/* Animated Connecting Line */}
          <div className="hidden md:block absolute top-1/2 left-0 w-full h-1 bg-gray-200 dark:bg-gray-800 -translate-y-1/2 z-0">
            <motion.div
              initial={{ width: "0%" }}
              whileInView={{ width: "100%" }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 1.5, ease: "easeInOut" }}
              className="h-full bg-gradient-to-r from-teal-400 via-amber-400 to-rose-400"
            />
          </div>

          <div className="grid md:grid-cols-3 gap-12 relative z-10">
            {steps.map((step, index) => (
              <motion.div
                key={step.id}
                initial={{ opacity: 0, y: 40 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-100px" }}
                transition={{ duration: 0.6, delay: index * 0.3 }}
                className="flex flex-col items-center text-center relative"
              >
                {/* Number Badge */}
                <div className="absolute -top-4 -right-4 md:top-0 md:left-1/2 md:-translate-x-1/2 md:-translate-y-1/2 w-8 h-8 bg-white dark:bg-primary rounded-full shadow-md flex items-center justify-center font-bold text-gray-900 dark:text-white border border-gray-100 dark:border-gray-800 z-20 hidden md:flex">
                  {step.id}
                </div>

                <div className={`w-32 h-32 rounded-full ${step.bg} ${step.darkBg} flex items-center justify-center mb-8 shadow-inner relative group`}>
                  <div className="absolute inset-0 rounded-full border-4 border-white dark:border-[#06121e] scale-110" />
                  <step.icon className={`w-12 h-12 ${step.color} group-hover:scale-110 transition-transform duration-300`} />
                </div>
                
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-3">
                  {step.title}
                </h3>
                <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
                  {step.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
