import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle2, UserPlus, FileBarChart, LayoutDashboard } from 'lucide-react';

export default function ForHealthcareWorkers() {
  return (
    <section className="py-24 bg-primary dark:bg-primary-dark relative overflow-hidden">
      <div className="container mx-auto px-6 relative z-10">
        <div className="flex flex-col lg:flex-row items-center gap-16">
          
          {/* Left Text */}
          <div className="flex-1">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-teal-500/20 text-teal-300 text-sm font-medium mb-6"
            >
              <LayoutDashboard className="w-4 h-4" />
              <span>Doctor Dashboard</span>
            </motion.div>
            
            <motion.h2 
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 }}
              className="text-3xl md:text-5xl font-bold text-white mb-6 leading-tight"
            >
              Supercharging <span className="text-amber-400">Rural Doctors</span> and ASHA Workers.
            </motion.h2>

            <motion.p 
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
              className="text-primary-light text-lg mb-8"
            >
              Get a bird's-eye view of your village's health. Manage patient queues efficiently, track outbreak patterns, and intervene before a mild symptom becomes an emergency.
            </motion.p>

            <div className="space-y-4 mb-10">
              {[
                "AI pre-filled patient symptom summaries.",
                "Automated triage highlighting critical patients.",
                "Direct ABDM integration for health records."
              ].map((item, i) => (
                <motion.div 
                  key={i}
                  initial={{ opacity: 0, x: -20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: 0.3 + (i * 0.1) }}
                  className="flex items-center gap-3 text-white"
                >
                  <CheckCircle2 className="w-5 h-5 text-teal-400" />
                  <span>{item}</span>
                </motion.div>
              ))}
            </div>

            <motion.button
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.6 }}
              className="px-8 py-4 bg-white text-primary rounded-xl font-bold hover:bg-gray-100 transition-colors flex items-center gap-2 shadow-xl shadow-black/20"
            >
              <UserPlus className="w-5 h-5 text-amber-500" />
              Join as Verified Doctor
            </motion.button>
          </div>

          {/* Right Dashboard Mockup */}
          <motion.div 
            initial={{ opacity: 0, x: 20, rotateY: -10 }}
            whileInView={{ opacity: 1, x: 0, rotateY: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="flex-1 w-full perspective-1000"
          >
            <div className="bg-[#0f172a] rounded-2xl border border-gray-800 shadow-2xl shadow-black/50 overflow-hidden transform-gpu rotate-y-[-5deg] rotate-x-[5deg]">
              {/* Dashboard Header */}
              <div className="h-12 bg-gray-900 border-b border-gray-800 flex items-center px-4 gap-2">
                <div className="flex gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-rose-500" />
                  <div className="w-3 h-3 rounded-full bg-amber-500" />
                  <div className="w-3 h-3 rounded-full bg-green-500" />
                </div>
                <div className="mx-auto bg-gray-800 text-gray-400 text-xs py-1 px-24 rounded-md">
                  doctor.medichain.in
                </div>
              </div>

              {/* Dashboard Content */}
              <div className="p-6 grid grid-cols-3 gap-6">
                {/* Sidebar */}
                <div className="col-span-1 space-y-4">
                  <div className="h-8 bg-gray-800 rounded-md w-full" />
                  <div className="h-8 bg-gray-800/50 rounded-md w-3/4" />
                  <div className="h-8 bg-gray-800/50 rounded-md w-5/6" />
                  <div className="mt-8 h-32 bg-gradient-to-br from-teal-500/20 to-blue-500/20 rounded-xl border border-teal-500/30 flex items-center justify-center">
                    <FileBarChart className="w-8 h-8 text-teal-400" />
                  </div>
                </div>

                {/* Main Content */}
                <div className="col-span-2 space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="h-24 bg-gray-800 rounded-xl p-4 flex flex-col justify-between border border-gray-700">
                      <div className="w-8 h-8 rounded-full bg-rose-500/20 flex items-center justify-center">
                         <div className="w-2 h-2 rounded-full bg-rose-500 animate-pulse" />
                      </div>
                      <div>
                        <div className="text-2xl font-bold text-white">12</div>
                        <div className="text-xs text-gray-400">Critical Patients</div>
                      </div>
                    </div>
                    <div className="h-24 bg-gray-800 rounded-xl p-4 flex flex-col justify-between border border-gray-700">
                      <div className="w-8 h-8 rounded-full bg-amber-500/20" />
                      <div>
                        <div className="text-2xl font-bold text-white">45</div>
                        <div className="text-xs text-gray-400">In Queue</div>
                      </div>
                    </div>
                  </div>

                  {/* List Mockup */}
                  <div className="bg-gray-800 rounded-xl p-4 border border-gray-700 h-48 space-y-3">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-gray-700" />
                      <div className="flex-1">
                        <div className="h-3 bg-gray-700 rounded w-1/3 mb-1" />
                        <div className="h-2 bg-gray-700 rounded w-1/2" />
                      </div>
                      <div className="w-16 h-6 rounded-full bg-rose-500/20 border border-rose-500/30" />
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-gray-700" />
                      <div className="flex-1">
                        <div className="h-3 bg-gray-700 rounded w-1/4 mb-1" />
                        <div className="h-2 bg-gray-700 rounded w-1/2" />
                      </div>
                      <div className="w-16 h-6 rounded-full bg-amber-500/20 border border-amber-500/30" />
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-gray-700" />
                      <div className="flex-1">
                        <div className="h-3 bg-gray-700 rounded w-1/3 mb-1" />
                        <div className="h-2 bg-gray-700 rounded w-2/3" />
                      </div>
                      <div className="w-16 h-6 rounded-full bg-green-500/20 border border-green-500/30" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>

        </div>
      </div>
    </section>
  );
}
