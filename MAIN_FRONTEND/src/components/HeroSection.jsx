import React from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, Stethoscope, Activity } from 'lucide-react';
import { cn } from '../lib/utils';

export default function HeroSection() {
  return (
    <section className="relative min-h-screen flex items-center pt-24 overflow-hidden bg-gradient-to-b from-surface to-surface-dark dark:from-background dark:to-primary-dark">
      {/* Abstract Background with glowing dots representing rural nodes */}
      <div className="absolute inset-0 z-0 overflow-hidden opacity-30 dark:opacity-40">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-teal-500/20 rounded-full blur-[100px] animate-pulse-slow" />
        <div className="absolute bottom-1/4 right-1/4 w-[30rem] h-[30rem] bg-amber-500/10 rounded-full blur-[120px] animate-pulse-slow" style={{ animationDelay: '1s' }} />
        
        {/* Animated grid/network dots */}
        <svg className="absolute inset-0 w-full h-full" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
              <circle cx="2" cy="2" r="1.5" className="fill-current text-primary-light/20 dark:text-teal-500/20" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#grid)" />
        </svg>

        {/* Glowing Pulse Dots */}
        {[...Array(6)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-3 h-3 bg-teal-400 rounded-full"
            style={{
              top: `${Math.random() * 80 + 10}%`,
              left: `${Math.random() * 80 + 10}%`,
              boxShadow: '0 0 15px 4px rgba(0, 198, 167, 0.4)'
            }}
            animate={{
              scale: [1, 1.5, 1],
              opacity: [0.5, 1, 0.5],
            }}
            transition={{
              duration: 3 + Math.random() * 2,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          />
        ))}
      </div>

      <div className="container mx-auto px-6 relative z-10">
        <div className="flex flex-col lg:flex-row items-center gap-16">
          {/* Left Content */}
          <div className="flex-1 text-center lg:text-left">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-card text-teal-600 dark:text-teal-400 text-sm font-medium mb-6"
            >
              <Activity className="w-4 h-4" />
              <span>AI-Powered Rural Health Triage</span>
            </motion.div>

            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="text-5xl md:text-6xl lg:text-7xl font-extrabold tracking-tight mb-6 text-primary dark:text-white leading-tight"
            >
              Healthcare shouldn't stop at the <span className="text-teal-500">city border.</span>
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="text-lg md:text-xl text-gray-600 dark:text-gray-300 mb-10 max-w-2xl mx-auto lg:mx-0 leading-relaxed"
            >
              AI-powered symptom triage in your language, even without internet. Bridging the gap between rural patients and life-saving medical care.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
              className="flex flex-col sm:flex-row items-center gap-4 justify-center lg:justify-start"
            >
              <button className="w-full sm:w-auto px-8 py-4 bg-teal-500 hover:bg-teal-600 text-white rounded-xl font-semibold transition-all flex items-center justify-center gap-2 shadow-lg shadow-teal-500/30 hover:shadow-teal-500/50 hover:-translate-y-1">
                Check Symptoms Now
                <ArrowRight className="w-5 h-5" />
              </button>
              <button className="w-full sm:w-auto px-8 py-4 bg-white dark:bg-primary/50 text-primary dark:text-white border border-gray-200 dark:border-primary-light rounded-xl font-semibold hover:bg-gray-50 dark:hover:bg-primary transition-all flex items-center justify-center gap-2">
                <Stethoscope className="w-5 h-5 text-amber-500" />
                For Doctors
              </button>
            </motion.div>
          </div>

          {/* Right Content (Floating Phone Mockup) */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9, x: 20 }}
            animate={{ opacity: 1, scale: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="flex-1 relative"
          >
            {/* Soft decorative blob behind phone */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-gradient-to-tr from-teal-400/30 to-amber-400/20 rounded-full blur-3xl" />
            
            <motion.div
              animate={{ y: [-10, 10, -10] }}
              transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
              className="relative mx-auto w-72 md:w-80 h-[600px] bg-gray-900 rounded-[2.5rem] border-8 border-gray-800 shadow-2xl overflow-hidden"
            >
              {/* Notch */}
              <div className="absolute top-0 inset-x-0 h-6 bg-gray-800 rounded-b-xl w-32 mx-auto z-20" />
              
              {/* App Screen Simulation */}
              <div className="bg-white dark:bg-primary h-full w-full relative flex flex-col pt-12 p-4 z-10">
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-10 h-10 bg-teal-100 dark:bg-teal-500/20 rounded-full flex items-center justify-center">
                    <Activity className="w-6 h-6 text-teal-600 dark:text-teal-400" />
                  </div>
                  <div>
                    <h3 className="font-bold text-gray-900 dark:text-white">MediChain AI</h3>
                    <p className="text-xs text-green-500 font-medium">● Online (Offline Mode Ready)</p>
                  </div>
                </div>

                <div className="flex-1 flex flex-col gap-4">
                  <div className="bg-gray-100 dark:bg-primary-light p-3 rounded-2xl rounded-tl-sm text-sm text-gray-800 dark:text-gray-200 max-w-[85%]">
                    Namaste. How are you feeling today? You can type or speak in Hindi, English, or 10 other languages.
                  </div>
                  <div className="bg-teal-500 text-white p-3 rounded-2xl rounded-tr-sm text-sm self-end max-w-[85%]">
                    My child has a high fever and is breathing fast since last night.
                  </div>
                  
                  <motion.div 
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 1 }}
                    className="bg-amber-50 dark:bg-amber-500/10 border border-amber-200 dark:border-amber-500/20 p-4 rounded-2xl"
                  >
                    <div className="flex items-center gap-2 text-amber-600 dark:text-amber-400 font-bold text-sm mb-2">
                      <div className="w-2 h-2 rounded-full bg-amber-500 animate-pulse" />
                      Monitor Closely
                    </div>
                    <p className="text-xs text-gray-700 dark:text-gray-300 mb-3">
                      Based on these symptoms (high fever + rapid breathing), please seek medical attention soon.
                    </p>
                    <button className="w-full py-2 bg-amber-500 hover:bg-amber-600 text-white rounded-lg text-xs font-bold transition-colors">
                      View First-Aid Guide
                    </button>
                  </motion.div>
                </div>

                <div className="mt-auto relative">
                  <div className="h-12 bg-gray-100 dark:bg-primary-light rounded-full flex items-center px-4">
                    <p className="text-gray-400 text-sm">Type a message...</p>
                    <div className="w-8 h-8 bg-teal-500 rounded-full flex items-center justify-center ml-auto shadow-md">
                      <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                      </svg>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
